# Normalize recipes and ingredients across API sources

Use one backend recipe format for every source and one frontend layout for every recipe. The first release migrates Spoonacular and proves the design with a second, differently shaped offline fixture. Recipes from different providers keep their own pages and favourites, even when their titles match. Ingredients share identities across providers, and quantities prefer metric where the source supports a reliable conversion.

## 1. Normalize recipes at import

- Give each provider an adapter that produces the same recipe fields: source and external ID, original recipe URL when available, title, plain-text description, optional image, time in minutes, servings, meal types, diets, ordered ingredient lines, and ordered instruction sections and steps. Require a title and source identity for imported recipes. Represent unknown values explicitly.
- Route featured imports, suggestions, stale-recipe refreshes, instruction fetches, and API seeding through the same adapter and persistence logic. Convert HTML lists and paragraphs into readable text while preserving step boundaries and section headings. Normalize known tag spellings and deduplicate tags without inferring dietary claims.
- Identify an imported recipe by `(provider, external_id)`, with external IDs stored as strings. Keep the local recipe ID as the public URL and favourite target. Update each recipe atomically. A full refresh replaces obsolete lines and tags, a partial response updates only supplied fields, and a failed import leaves the last successful version usable.

## 2. Separate ingredient identity from the recipe line

- Give each catalog ingredient a display name and a normalized lookup key. Resolve provider ingredient IDs first, then exact normalized names and a small, tested alias list. For example, `scallions` and `green onions` can share an identity, while `onion` and `onion powder` stay distinct. Preserve unfamiliar names and meaningful qualifiers.
- Replace the current one-row-per-recipe-and-ingredient constraint with ordered recipe lines. Each line carries its own ID, ingredient reference, original wording, quantity, unit, and preparation note when supplied. This lets “butter, melted” in the batter and “butter, softened” in the frosting appear independently.
- Prefer an explicit metric measure from the source. Otherwise convert within mass or volume only when the unit convention is known. Display practical units such as `250 g` or `1.5 L`, convert both ends of ranges, and round only for display. Preserve counts, “to taste,” ambiguous cups, and unparsed lines in readable form. A cup of flour needs a source-provided weight to display in grams.
- Use the same identity lookup for ingredient search, filters, fridge availability, and missing-item shopping actions. Count each distinct ingredient once for availability and mark every corresponding recipe line. For bulk shopping, combine compatible amounts and retain separate amount descriptions when they cannot be combined. Preserve users’ existing fridge and shopping-list wording.

## 3. Migrate existing data and unify the frontend

- Add an Alembic migration that backfills Spoonacular source IDs, ingredient identities, and recipe lines while preserving local recipe IDs and favourites. Keep local recipes valid without external IDs. Existing ingredient rows have no stored order, so use ingredient ID for deterministic legacy ordering until a provider refresh restores source order.
- Keep the existing recipe endpoints and update FastAPI schemas and shared TypeScript types together. Expose ordered instruction sections, ingredient line IDs, original wording, formatted metric-preferred amounts, and nullable metadata. Keep the legacy instruction text and quantity/unit fields available to existing callers.
- Use the same card and detail presentation for local and imported recipes. Reserve consistent image space and provide a fallback for missing or broken images. Omit unknown time and servings, render instructions as numbered steps, and show ingredient amounts and preparation notes consistently. Use line IDs for rendering and canonical ingredient IDs for availability. Show original source attribution on the detail page when supplied.

## 4. Verify with two source shapes and existing workflows

- Import paired fixtures for the same example dish, one with Spoonacular-style structured fields and one with free-text ingredients, HTML directions, and missing metadata. Verify that they produce two local recipes with shared ingredient identities, the same frontend layout, readable steps, and no invented values.
- Test repeated and concurrent imports, changed quantities, removed lines, repeated ingredients, ambiguous aliases, partial responses, and failed refreshes. Verify metric formatting with explicit metric values, fractions, ranges, counts, and ambiguous units.
- Rehearse the migration on isolated PostgreSQL and SQLite databases populated with legacy recipes, ingredients, and favourites. Run the backend suite, frontend tests, lint, production build, and browser E2E suite. Check both fixture recipes at desktop and mobile widths, including ingredient filtering, fridge counts, favourites, and adding missing ingredients to the shopping list.

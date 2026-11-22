# Meal Maker project review

Reviewed November 20, 2026. Findings 1 through 4, 6, and 8 are fixed in the code, and all three further improvements are complete. The next priority is the guest “Apply fridge ingredients” filter. Remaining findings are based on source inspection.

## Fixed findings

1. **Case-variant usernames could resolve to the wrong account.** Registration and the database now reject case-only duplicates. Login is case-insensitive, username spelling is preserved for display, and access tokens identify accounts by an immutable ID. [Authentication lookup and registration](backend/crud/users.py), [User model](backend/app/models.py)

2. **Access and refresh tokens were interchangeable.** The API now requires a signed access token with the access purpose claim. Refresh tokens are stored as hashes, replaced atomically after one use, and revoked on logout. Concurrent refresh requests in the same browser tab share one request. [Token signing and verification](backend/util/auth.py), [Refresh handling](backend/crud/users.py), [Frontend session service](frontend/services/UserService.ts)

3. **The guest fridge was overwritten when Home reopened.** Home now restores saved ingredients before writing to browser storage. The regression test verifies that the saved ingredient and its recipe suggestion reappear and that removing the ingredient updates storage. [Home page](frontend/pages/index.tsx), [Guest fridge test](frontend/tests/home.test.tsx)

4. **Multiple ingredient selections produced contradictory filters.** Both recipe list endpoints now require every selected ingredient by ID. The existing name filter accepts exact names without regard to case, and unknown selections yield no matches. Home suggestions can still use any ingredient in the fridge. [Recipe queries](backend/crud/recipes.py), [Backend filter tests](backend/tests/test_recipes.py), [Frontend request test](frontend/tests/recipe-service.test.ts)

6. **Overlapping local and Spoonacular IDs could select the wrong recipe.** Recipe details, fridge availability, and shopping-list additions now resolve recipes by local ID. Requests with no matching local ID return `404`. Spoonacular imports and refreshes still use the external ID. [Recipe lookup](backend/crud/recipes.py), [Recipe ID regression tests](backend/tests/test_recipes.py)

8. **Spoonacular calls had no timeouts.** All seven HTTP calls now use a 3-second connect timeout and an 8-second read timeout. When a recipe refresh or instruction request fails, the API returns the saved recipe. When external suggestions fail, it returns any local matches. [Spoonacular client](backend/util/spoonacular.py), [Timeout regression tests](backend/tests/test_recipes.py)

The six new account and token regressions and five initial guest fridge and ingredient filter regressions failed before their fixes and passed afterward. Mocked requests verified the timeout settings on all seven calls. The latest local run passed 60 backend tests, 12 frontend tests, and 5 browser tests. The frontend production build and lint checks also passed. [Backend authentication tests](backend/tests/test_users.py), [Frontend refresh test](frontend/tests/auth-refresh.test.ts), [Browser tests](frontend/e2e/mvp.spec.ts)

Before deploying, resolve any existing case-colliding usernames and apply the account identity migration. Users will need to sign in again. [Migration instructions](README.md#database-migrations)

## Open findings in recommended fix order

5. **Guest “Apply fridge ingredients” rejects all results when the fridge is populated.** The page checks each recipe’s ingredient list, but the summary returned by `/recipes/` omits that field. Align the API response with the filter or perform matching on the backend. [Recipe discovery page](frontend/pages/recipes/index.tsx), [Response schemas](backend/app/schemas.py)

7. **The frontend’s suggestion count is ignored.** Home requests nine suggestions using `number`, but the endpoint reads `count` and defaults to five. Standardize the parameter and verify it end to end. [Recipe service](frontend/services/recipeService.tsx), [API routes](backend/app/routes.py)

## Deployment configuration

- **Cross-site session refresh.** If the frontend and API run on different sites, the browser excludes the `SameSite=Strict` refresh cookie, which prevents session restoration. Verify the deployment topology and prefer a same-site setup, or configure the cookie policy and CSRF protection together. [Cookie settings](backend/crud/users.py), [MDN Set-Cookie reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)
- **Docker frontend API URL.** Compose supplies the frontend environment file at runtime, while Next.js embeds `NEXT_PUBLIC_API_URL` during the image build. The Docker build excludes `.env` and does not pass the variable, so the browser bundle falls back to localhost. Pass the public URL at build time. [Compose configuration](docker-compose.yml), [Frontend Dockerfile](frontend/dockerfile), [Next.js environment variables](https://nextjs.org/docs/app/guides/environment-variables)

## Further improvements completed

- **Stronger verification.** The recipe test sends `meal_types` and proves that the filter excludes a nonmatching recipe. Coverage includes `crud` and `util`. The account migration test passed on both SQLite and a disposable PostgreSQL 18 container, verifying that upgrades preserve existing users and reject case-only duplicate usernames, and that downgrades preserve existing users. CI runs both variants. [Recipe tests](backend/tests/test_recipes.py), [Coverage configuration](backend/pytest.ini), [Migration test](backend/tests/test_migrations.py), [CI workflow](.github/workflows/ci.yml)
- **Imported recipe descriptions render as plain text.** The recipe detail page displays the description text and decodes HTML entities. Imported links and formatting are removed. [Recipe detail page](frontend/pages/recipes/%5Bid%5D.tsx), [Recipe detail test](frontend/tests/recipe-detail.test.tsx)
- **Failed logout clears local authentication and shows a warning.** Clicking Log Out clears the in-memory access token and prevents a pending refresh from restoring it. After a failed request, the app returns to guest mode and warns that the server session could not be ended. [Logout service](frontend/services/UserService.ts), [Logout tests](frontend/tests/logout.test.tsx), [Browser test](frontend/e2e/mvp.spec.ts)

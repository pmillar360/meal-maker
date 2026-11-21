"""Two offline provider shapes for contract and browser tests."""
from crud.recipe_import import ImportedRecipe, free_text_line, spoonacular_recipe
from util.recipe_normalization import instruction_sections

STRUCTURED = {
    "id": 207, "title": "Green onion broth", "servings": 2, "readyInMinutes": 15,
    "summary": "<p>A simple <b>broth</b>.</p>", "sourceUrl": "https://example.org/broth",
    "extendedIngredients": [
        {"id": 17, "name": "scallions", "original": "2 scallions, sliced", "amount": 2, "meta": ["sliced"]},
        {"id": 19, "name": "water", "amount": 1, "unit": "cup", "original": "1 cup water",
         "measures": {"metric": {"amount": 240, "unitShort": "ml"}}},
        {"id": 19, "name": "water", "amount": 10, "unit": "ml", "original": "10 ml water"},
    ],
    "analyzedInstructions": [{"name": "Broth", "steps": [{"step": "Slice the onions."}, {"step": "Simmer."}]}],
}

TEXT = {
    "slug": "207", "name": "Green onion broth", "ingredients": ["2 green onions, sliced", "250 ml water"],
    "directions": "<h2>Broth</h2><ol><li>Slice the onions.</li><li>Simmer.</li></ol>",
}


def fixture_recipes():
    return (
        spoonacular_recipe(STRUCTURED),
        ImportedRecipe(provider="offline", external_id=TEXT["slug"], title=TEXT["name"],
                       lines=[free_text_line(line) for line in TEXT["ingredients"]],
                       sections=instruction_sections(TEXT["directions"])),
    )

import pytest
from sqlalchemy import select
from app import models
from crud.recipe_import import save_import, spoonacular_recipe, free_text_line
from tests.normalization_fixtures import fixture_recipes, STRUCTURED
from util.recipe_normalization import display_amount, ingredient_key


@pytest.mark.parametrize("quantity,unit,expected", [
    ("1/2", "lb", "226.8 g"), ("1-2", "lb", "453.6–907.2 g"), ("1500", "ml", "1.5 L"),
    ("1/2", "cup", "1/2 cup"), (None, "to taste", "to taste"), ("2", None, "2"),
])
def test_display_amount(quantity, unit, expected):
    assert display_amount(quantity, unit) == expected


@pytest.mark.parametrize("unit", ["tablespoon", "teaspoon"])
def test_spoon_spellings_share_ingredient(unit):
    singular = free_text_line(f"1 {unit} olive oil")
    plural = free_text_line(f"2 {unit}s olive oil")
    assert singular.name == plural.name == "olive oil"
    assert (singular.unit, plural.unit) == (unit, unit + "s")


def test_empty_import_fetches_instructions_on_detail(db_session, client, monkeypatch):
    data = dict(STRUCTURED, instructions=None, analyzedInstructions=[])
    recipe = save_import(db_session, spoonacular_recipe(data))
    monkeypatch.setattr("crud.recipes.get_recipe_instructions", lambda _: STRUCTURED["analyzedInstructions"])
    response = client.get(f"/recipes/{recipe.id}")
    assert response.json()["instructions"] == "Slice the onions.\nSimmer."
    assert save_import(db_session, spoonacular_recipe(data)).instructions == response.json()["instructions"]


def test_two_sources_and_shopping(db_session, authenticated_client, test_user):
    a, b = [save_import(db_session, data) for data in fixture_recipes()]
    assert a.id != b.id and a.title == b.title
    assert a.instruction_sections == b.instruction_sections
    assert a.recipe_ingredients[0].ingredient_id == b.recipe_ingredients[0].ingredient_id
    assert a.recipe_ingredients[1].amount == "240 mL"
    assert b.recipe_ingredients[1].amount == "250 mL"
    assert b.cooking_time is None and b.image_url is None
    db_session.add(models.FridgeItem(name="Scallions", user_id=test_user.id))
    db_session.commit()
    data = authenticated_client.get(f"/recipes/{a.id}/availability/").json()
    assert (data["available_ingredients"], data["total_ingredients"]) == (1, 2)
    items = authenticated_client.post(f"/recipes/{a.id}/missing-to-shopping-list/").json()["created_items"]
    assert [(item["name"], item["quantity"]) for item in items] == [("water", "250 mL")]
    assert ingredient_key("onion") != ingredient_key("onion powder")
    assert free_text_line("salt to taste").original == "salt to taste"


def test_refresh_and_rollback(db_session, monkeypatch):
    recipe = save_import(db_session, spoonacular_recipe(STRUCTURED))
    recipe_id = recipe.id
    partial = spoonacular_recipe({"id": 207, "title": "Updated title"})
    assert len(save_import(db_session, partial).recipe_ingredients) == 3
    updated = dict(STRUCTURED, extendedIngredients=[dict(STRUCTURED["extendedIngredients"][0], amount=7)])
    for _ in range(2):
        recipe = save_import(db_session, spoonacular_recipe(updated))
        assert recipe.id == recipe_id
        assert [line.quantity for line in recipe.recipe_ingredients] == ["7"]
    invalid = spoonacular_recipe(dict(STRUCTURED, title="Failed update"))
    def fail_tag_write(*args):
        raise ValueError("Invalid tag")
    monkeypatch.setattr("crud.recipe_import.tags", fail_tag_write)
    invalid.diets = ["Vegan"]
    with pytest.raises(ValueError):
        save_import(db_session, invalid)
    assert db_session.scalar(select(models.Recipe)).title == STRUCTURED["title"]
    assert len(recipe.recipe_ingredients) == 1

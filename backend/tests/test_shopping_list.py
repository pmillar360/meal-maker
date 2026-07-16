from fastapi import status
from app import models


def _create_recipe_with_ingredients(db_session, test_user, ingredient_names: list[str]):
    recipe = models.Recipe(
        title="Shopping List Bulk Test Recipe",
        description="A recipe for shopping list bulk add tests",
        instructions="Cook",
        cooking_time=20,
        servings=2,
        user_id=test_user.id,
    )
    db_session.add(recipe)
    db_session.flush()

    for ingredient_name in ingredient_names:
        ingredient = models.Ingredient(name=ingredient_name, category="Produce")
        db_session.add(ingredient)
        db_session.flush()

        recipe_ingredient = models.RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id,
            quantity="1",
            unit="unit",
        )
        db_session.add(recipe_ingredient)

    db_session.commit()
    db_session.refresh(recipe)
    return recipe

def test_create_shopping_list_item(authenticated_client):
    item_data = {
        "name": "Test Item",
        "quantity": "2 units",
    }
    
    response = authenticated_client.post("/shopping-list/", json=item_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["quantity"] == item_data["quantity"]
    assert "completed" in data
    assert data["completed"] == False

def test_get_shopping_list(authenticated_client, test_shopping_list_item):
    response = authenticated_client.get("/shopping-list/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(item["id"] == test_shopping_list_item.id for item in data)

def test_update_shopping_list_item(authenticated_client, test_shopping_list_item):
    update_data = {
        "completed": True
    }
    response = authenticated_client.patch(f"/shopping-list/{test_shopping_list_item.id}", json=update_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == test_shopping_list_item.name
    assert data["quantity"] == test_shopping_list_item.quantity
    assert data["completed"] == True

def test_delete_shopping_list_item(authenticated_client, test_shopping_list_item):
    response = authenticated_client.delete(f"/shopping-list/{test_shopping_list_item.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
    
    # Verify item is deleted
    get_response = authenticated_client.get("/shopping-list/")
    items = get_response.json()
    assert not any(item["id"] == test_shopping_list_item.id for item in items) 


def test_add_missing_ingredients_to_shopping_list(authenticated_client, db_session, test_user):
    recipe = _create_recipe_with_ingredients(db_session, test_user, ["Carrot", "Celery"])
    authenticated_client.post("/fridge/", json={"name": "carrot", "quantity": "1"})

    response = authenticated_client.post(f"/recipes/{recipe.id}/missing-to-shopping-list/")

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["created_count"] == 1
    assert len(data["created_items"]) == 1
    assert data["created_items"][0]["name"] == "Celery"


def test_add_missing_ingredients_to_shopping_list_allows_duplicates(authenticated_client, db_session, test_user):
    recipe = _create_recipe_with_ingredients(db_session, test_user, ["Milk", "Eggs"])
    authenticated_client.post("/fridge/", json={"name": "milk", "quantity": "1"})

    first_response = authenticated_client.post(f"/recipes/{recipe.id}/missing-to-shopping-list/")
    second_response = authenticated_client.post(f"/recipes/{recipe.id}/missing-to-shopping-list/")

    assert first_response.status_code == status.HTTP_201_CREATED
    assert second_response.status_code == status.HTTP_201_CREATED

    items_response = authenticated_client.get("/shopping-list/")
    assert items_response.status_code == status.HTTP_200_OK
    items = [item for item in items_response.json() if item["name"] == "Eggs"]
    assert len(items) == 2
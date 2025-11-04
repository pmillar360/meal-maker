from fastapi import status

def test_get_recipe_by_id(client, test_recipe):
    response = client.get(f"/recipes/{test_recipe.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_recipe.id
    assert data["title"] == test_recipe.title
    assert "instructions" in data
    assert "recipe_ingredients" in data

def test_get_recipes(client, test_recipe):
    response = client.get("/recipes/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(recipe["id"] == test_recipe.id for recipe in data)

def test_get_recipes_with_meal_type(client, test_recipe):
    response = client.get(f"/recipes/?meal_type={test_recipe.meal_types[0]}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(recipe["id"] == test_recipe.id for recipe in data) 

def test_get_user_favorite_recipes(authenticated_client, test_user, test_recipe):
    # First, add the recipe to the user's favorites
    authenticated_client.post("/users/favorites/",
        json={"recipe_id": test_recipe.id}
    )
    
    # Now, retrieve the user's favorite recipes
    response = authenticated_client.get("/users/favorites/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(recipe["id"] == test_recipe.id for recipe in data)
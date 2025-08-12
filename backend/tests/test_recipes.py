from fastapi import status

def test_get_recipe(client, test_recipe):
    response = client.get(f"/recipes/{test_recipe.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_recipe.id
    assert data["title"] == test_recipe.title
    assert "instructions" in data
    assert "ingredients" in data

def test_get_recipes(client, test_recipe):
    response = client.get("/recipes/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(recipe["id"] == test_recipe.id for recipe in data)

def test_get_recipes_with_meal_type(client, test_recipe):
    response = client.get(f"/recipes/?meal_type={test_recipe.meal_type}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(recipe["meal_type"] == test_recipe.meal_type for recipe in data)

def test_get_ingredients(client, test_ingredient):
    response = client.get("/ingredients/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(ingredient["id"] == test_ingredient.id for ingredient in data) 
import pytest
from fastapi import status

def test_get_ingredient(client, test_ingredient):
    response = client.get(f"/ingredients/{test_ingredient.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_ingredient.id
    assert data["name"] == test_ingredient.name
    assert data["category"] == test_ingredient.category

def test_get_ingredients(client, test_ingredient):
    response = client.get("/ingredients/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(ingredient["id"] == test_ingredient.id for ingredient in data)

def test_update_ingredient(client, test_ingredient):
    update_data = {
        "name": "Updated Ingredient",
        "category": "Updated Category"
    }
    
    response = client.put(
        f"/ingredients/{test_ingredient.id}",
        json=update_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["category"] == update_data["category"]

def test_delete_ingredient(client, test_ingredient):
    response = client.delete(f"/ingredients/{test_ingredient.id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify ingredient is deleted
    get_response = client.get(f"/ingredients/{test_ingredient.id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_get_ingredients_by_category(client, test_ingredient):
    response = client.get(f"/ingredients/category/{test_ingredient.category}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(ingredient["category"] == test_ingredient.category for ingredient in data) 
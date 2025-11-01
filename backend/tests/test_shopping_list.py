from fastapi import status

def test_create_shopping_list_item(authenticated_client):
    item_data = {
        "name": "Test Item",
        "quantity": "2 units",
    }
    
    response = authenticated_client.post("/shopping-list/", json=item_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["quantity"] == item_data["quantity"]
    assert "completed" in data
    assert data["completed"] == False

# TODO How to test things that require user to be authenticated?
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

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == True
    
    # Verify item is deleted
    get_response = authenticated_client.get("/shopping-list/")
    items = get_response.json()
    assert not any(item["id"] == test_shopping_list_item.id for item in items) 
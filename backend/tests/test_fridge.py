from fastapi import status

def test_get_fridge_items(authenticated_client, test_fridge_item):
    response = authenticated_client.get("/fridge")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(item["id"] == test_fridge_item.id for item in data)

def test_add_fridge_item(authenticated_client):
    item_data = {
        "name": "Milk",
        "quantity": "1 liter",
    }

    response = authenticated_client.post("/fridge/", json=item_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["quantity"] == item_data["quantity"]

def test_update_fridge_item(authenticated_client, test_fridge_item):
    update_data = {
        # "name": "Almond Milk",
        "quantity": "2 liters",
    }

    response = authenticated_client.patch(f"/fridge/{test_fridge_item.id}", json=update_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # assert data["name"] == update_data["name"]
    assert data["quantity"] == update_data["quantity"]

def test_delete_fridge_item(authenticated_client, test_fridge_item):
    response = authenticated_client.delete(f"/fridge/{test_fridge_item.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    # Verify item is deleted
    get_response = authenticated_client.get("/fridge")
    items = get_response.json()
    assert not any(item["id"] == test_fridge_item.id for item in items)
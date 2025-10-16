from fastapi import status

def test_register_user(client):
    item_data = {
        "username": "TestUser",
        "password": "TestPassword"
    }
    
    response = client.post(f"/register/", json=item_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data["access_token"]) > 0
    assert data["token_type"] == "bearer"

def test_login_user(client):
    login_data = {
        "username": "TestUser",
        "password": "TestPassword"
    }

    response = client.post(f"/token/", data=login_data)

    assert response.status_code == status.HTTP_200_OK
from fastapi import status

from backend.util.auth import verify_token

def test_register_user(client):
    item_data = {
        "username": "TestUser",
        "password": "TestPassword"
    }
    
    response = client.post(f"/register", json=item_data)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    cookies = response.cookies

    assert data["token_type"] == "bearer"

    access_token = data["access_token"]
    refresh_token = cookies["refresh_token"]

    assert access_token
    assert refresh_token
    assert verify_token(access_token)
    assert verify_token(refresh_token)

def test_login_user(client, test_user):
    login_data = {
        "username": test_user.username,
        "password": "hashedpassword123"
    }

    response = client.post(f"/token", json=login_data)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    cookies = response.cookies

    access_token = data["access_token"]
    refresh_token = cookies["refresh_token"]

    assert access_token
    assert refresh_token
    assert verify_token(access_token)
    assert verify_token(refresh_token)
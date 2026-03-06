from fastapi import status

from util.auth import verify_token

def test_register_user(client):
    item_data = {
        "username": "TestUser",
        "password": "TestPassword"
    }
    
    response = client.post("/users", json=item_data)

    assert response.status_code == status.HTTP_201_CREATED

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

    response = client.post("/auth/tokens", json=login_data)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    cookies = response.cookies

    access_token = data["access_token"]
    refresh_token = cookies["refresh_token"]

    assert access_token
    assert refresh_token
    assert verify_token(access_token)
    assert verify_token(refresh_token)

def test_get_current_user_restful_route(authenticated_client, test_user):
    response = authenticated_client.get("/users/me")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user.username

def test_refresh_token_requires_cookie(client):
    response = client.post("/auth/tokens/refresh")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_refresh_token_restful_route(client, test_user):
    login_data = {
        "username": test_user.username,
        "password": "hashedpassword123"
    }

    login_response = client.post("/auth/tokens", json=login_data)
    refresh_token = login_response.cookies.get("refresh_token")
    assert refresh_token is not None

    # Explicitly set the cookie in the test client so it is sent to refresh endpoint.
    client.cookies.set("refresh_token", refresh_token)

    refresh_response = client.post("/auth/tokens/refresh")

    assert refresh_response.status_code == status.HTTP_200_OK
    data = refresh_response.json()
    assert data["token_type"] == "bearer"
    assert verify_token(data["access_token"])

def test_delete_current_auth_token(authenticated_client):
    response = authenticated_client.delete("/auth/tokens/current")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
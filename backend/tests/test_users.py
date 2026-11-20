from fastapi import status

from util.auth import verify_token
from app.models import User


def test_register_user(client):
    item_data = {"username": "TestUser", "password": "TestPassword"}

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
    assert verify_token(refresh_token) is None


def test_login_user(client, test_user):
    login_data = {"username": test_user.username, "password": "hashedpassword123"}

    response = client.post("/auth/tokens", json=login_data)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    cookies = response.cookies

    access_token = data["access_token"]
    refresh_token = cookies["refresh_token"]

    assert access_token
    assert refresh_token
    assert verify_token(access_token)
    assert verify_token(refresh_token) is None


def test_get_current_user_restful_route(authenticated_client, test_user):
    response = authenticated_client.get("/users/me")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user.username


def test_refresh_token_requires_cookie(client):
    response = client.post("/auth/tokens/refresh")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token_restful_route(client, test_user):
    login_data = {"username": test_user.username, "password": "hashedpassword123"}

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


def test_rejects_case_variant_and_preserves_display_spelling(client):
    original = client.post(
        "/users", json={"username": "VoHiYo", "password": "test-password"}
    )
    assert original.status_code == 201
    duplicate = client.post(
        "/users", json={"username": "vohiyo", "password": "test-password"}
    )
    assert duplicate.status_code == 400
    token = original.json()["access_token"]
    identity = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert identity.json() == {"username": "VoHiYo"}


def test_access_identity_survives_username_change(
    authenticated_client, db_session, test_user
):
    test_user.username = "RenamedUser"
    db_session.commit()
    assert authenticated_client.get("/users/me").json() == {"username": "RenamedUser"}


def test_access_identity_rejects_deleted_account(
    authenticated_client, db_session, test_user
):
    user_id = test_user.id
    username = test_user.username
    db_session.query(User).filter_by(id=user_id).delete()
    db_session.commit()
    assert authenticated_client.get("/users/me").status_code == 401
    db_session.add(User(id=user_id, username=username, hashed_password="unused"))
    db_session.commit()
    assert authenticated_client.get("/users/me").status_code == 401


def test_token_purpose_is_enforced(client, test_user):
    login = client.post(
        "/auth/tokens",
        json={"username": test_user.username, "password": "hashedpassword123"},
    )
    access = login.json()["access_token"]
    refresh = login.cookies["refresh_token"]
    assert (
        client.get(
            "/users/me", headers={"Authorization": f"Bearer {refresh}"}
        ).status_code
        == 401
    )
    client.cookies.clear()
    client.cookies.set("refresh_token", access)
    assert client.post("/auth/tokens/refresh").status_code == 401


def test_refresh_is_single_use_and_logout_revokes_it(client, test_user):
    login = client.post(
        "/auth/tokens",
        json={"username": test_user.username, "password": "hashedpassword123"},
    )
    original = login.cookies["refresh_token"]

    def use_cookie(token):
        client.cookies.clear()
        client.cookies.set("refresh_token", token)

    use_cookie(original)
    rotated = client.post("/auth/tokens/refresh")
    assert rotated.status_code == 200
    replacement = rotated.cookies["refresh_token"]
    assert replacement != original
    use_cookie(original)
    assert client.post("/auth/tokens/refresh").status_code == 401
    use_cookie(replacement)
    assert client.delete("/auth/tokens/current").status_code == 204
    use_cookie(replacement)
    assert client.post("/auth/tokens/refresh").status_code == 401


def test_inactive_account_cannot_refresh(client, db_session, test_user):
    login = client.post(
        "/auth/tokens",
        json={"username": test_user.username, "password": "hashedpassword123"},
    )
    test_user.is_active = False
    db_session.commit()
    client.cookies.clear()
    client.cookies.set("refresh_token", login.cookies["refresh_token"])
    assert client.post("/auth/tokens/refresh").status_code == 401

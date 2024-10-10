# test_user_expenses.py
import datetime
from copy import deepcopy

import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from api.app import app
from api.config import TOKEN_ALGORITHM, TOKEN_SECRET_KEY


@pytest.mark.anyio
class TestUserCreation:
    async def test_invalid_data(self, async_client: AsyncClient):
        response = await async_client.post(
            "/users/", json={"username": "", "password": ""}  # Invalid data
        )
        assert response.status_code == 422
        assert response.json()["detail"] == "Invalid credential"

    async def test_valid(self, async_client: AsyncClient):
        response = await async_client.post(
            "/users/", json={"username": "usertestuser", "password": "usertestpassword"}
        )
        assert response.status_code == 200, response.json()
        assert (
            response.json()["message"]
            == "User and default accounts created successfully"
        )

    async def test_duplicate(self, async_client: AsyncClient):
        response = await async_client.post(
            "/users/", json={"username": "usertestuser", "password": "usertestpassword"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Username already exists"


@pytest.mark.anyio
async def test_create_token_invalid_credentials(async_client: AsyncClient):
    response = await async_client.post(
        "/users/token/", data={"username": "usertestuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.anyio
async def test_verify_token_non_existence(async_client: AsyncClient):
    response = await async_client.post(
        "/users/token/",
        data={"username": "usertestuser", "password": "usertestpassword"},
    )
    assert response.status_code == 200, response
    token_id = response.json()["result"]["_id"]
    token = response.json()["result"]["token"]
    response = await async_client.delete(
        f"/users/token/{token_id}", headers={"token": token}
    )
    assert response.status_code == 200, response
    response = await async_client.get("/users/", headers={"token": token})
    assert response.status_code == 401, response.json()
    assert response.json()["detail"] == "Token does not exist"


@pytest.mark.anyio
async def test_token_expired(async_client: AsyncClient):
    # Create a fake token with an expired timestamp
    payload = {
        "sub": "507f1f77bcf86cd799439011",
        "username": "expired_user",
        "exp": datetime.datetime.now(datetime.timezone.utc)
        - datetime.timedelta(minutes=1),
    }
    expired_token = jwt.encode(payload, TOKEN_SECRET_KEY, algorithm=TOKEN_ALGORITHM)
    headers = {"token": expired_token}

    # Try to access user details with the expired token
    response = await async_client.get("/users/", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"


@pytest.mark.anyio
async def test_create_token(async_client: AsyncClient):
    response = await async_client.post(
        "/users/token/",
        data={"username": "usertestuser", "password": "usertestpassword"},
    )
    assert response.status_code == 200
    assert "_id" in response.json()["result"]
    assert response.json()["result"]["token_type"] == "bearer"
    # Save token for future tests
    # async_client.headers.update({"Authorization": f"Bearer {response.json()['result']['token']}"})
    async_client.headers.update({"token": response.json()["result"]["token"]})


@pytest.mark.anyio
async def test_delete_token(async_client: AsyncClient):
    response = await async_client.post(
        "/users/token/",
        data={"username": "usertestuser", "password": "usertestpassword"},
    )
    assert response.status_code == 200
    token_id = response.json()["result"]["_id"]
    response = await async_client.delete(f"/users/token/{token_id}")
    assert response.status_code == 200, response
    assert response.json()["message"] == "Token deleted successfully", response.json()

    response = await async_client.get(f"/users/token/{token_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Token not found"


@pytest.mark.anyio
async def test_get_user(async_client: AsyncClient):
    response = await async_client.get("/users/")
    assert response.status_code == 200
    assert "username" in response.json()
    assert response.json()["username"] == "usertestuser"


@pytest.mark.anyio
async def test_get_tokens(async_client: AsyncClient):
    response = await async_client.get("/users/token/")
    assert response.status_code == 200
    assert "tokens" in response.json()
    assert isinstance(response.json()["tokens"], list)


@pytest.mark.anyio
async def test_get_token(async_client: AsyncClient):
    response = await async_client.get("/users/token/")
    assert response.status_code == 200
    token_id = response.json()["tokens"][0]["_id"]
    response = await async_client.get(f"/users/token/{token_id}")
    assert response.status_code == 200
    assert response.json()["_id"] == token_id


@pytest.mark.anyio
async def test_update_user_empty(async_client: AsyncClient):
    response = await async_client.put("/users/", json={})
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to update user"


@pytest.mark.anyio
async def test_update_user_invalid_input(async_client: AsyncClient):
    response = await async_client.put("/users/", json={"invalid?": "haha..."})
    assert response.status_code == 500, response.json()
    assert response.json()["detail"] == "Failed to update user"


@pytest.mark.anyio
async def test_update_user(async_client: AsyncClient):
    response = await async_client.put(
        "/users/",
        json={
            "password": "newpassword",
            "categories": ["Health", "Travel"],
            "currencies": ["INR"],
        },
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User updated successfully"
    assert "updated_user" in response.json()
    assert "Health" in response.json()["updated_user"]["categories"]


@pytest.mark.anyio
async def test_update_token_expiration(async_client: AsyncClient):
    response = await async_client.get("/users/token/")
    assert response.status_code == 200
    token_id = response.json()["tokens"][0]["_id"]
    response = await async_client.put(
        f"/users/token/{token_id}", params={"new_expiry": 60}
    )
    assert response.status_code == 200, response.json()
    assert response.json()["message"] == "Token expiration updated successfully"


@pytest.mark.anyio
async def test_login_with_nonexistent_user(async_client: AsyncClient):
    # Create a fake token for a nonexistent user
    payload = {
        "sub": None,
        "username": "nonexistent_user",
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=30),
    }
    fake_token = jwt.encode(payload, TOKEN_SECRET_KEY, algorithm=TOKEN_ALGORITHM)
    headers = {"token": fake_token}

    # Try to access user details with the fake token
    response = await async_client.get("/users/", headers=headers)
    assert response.status_code == 401, response.json()
    assert (
        response.json()["detail"] == "Invalid authentication credentials"
    ), response.json()


@pytest.mark.anyio
async def test_get_user_unauthenticated(async_client: AsyncClient):
    # Make a deep copy of the original headers to restore later
    original_headers = deepcopy(async_client.headers)

    # Temporarily remove the "token" header
    if "token" in async_client.headers:
        async_client.headers.pop("token")

    response = await async_client.get("/users/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Token is missing"

    # Restore the original headers
    async_client.headers.update(original_headers)


@pytest.mark.anyio
async def test_delete_user_unauthenticated(async_client: AsyncClient):
    # Make a deep copy of the original headers to restore later
    original_headers = deepcopy(async_client.headers)

    # Temporarily remove the "token" header
    if "token" in async_client.headers:
        async_client.headers.pop("token")

    response = await async_client.delete("/users/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Token is missing"

    # Restore the original headers
    async_client.headers.update(original_headers)


@pytest.mark.anyio
async def test_delete_user(async_client: AsyncClient):
    response = await async_client.delete("/users/")
    assert response.status_code == 200, response.json()
    assert response.json()["message"] == "User deleted successfully", response.json()

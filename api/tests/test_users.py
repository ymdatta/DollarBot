# test_user_expenses.py
import pytest
from httpx import AsyncClient, ASGITransport
from api.app import app

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.mark.anyio
async def test_create_user(async_client: AsyncClient):
    response = await async_client.post(
        "/users/",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User and default accounts created successfully"

@pytest.mark.anyio
async def test_login_for_access_token(async_client: AsyncClient):
    response = await async_client.post(
        "/users/token/",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    # Save token for future tests
    async_client.headers.update({"Authorization": f"Bearer {response.json()['access_token']}"})

@pytest.mark.anyio
async def test_get_user_details(async_client: AsyncClient):
    response = await async_client.get("/users/")
    assert response.status_code == 200
    assert "username" in response.json()
    assert response.json()["username"] == "testuser"

@pytest.mark.anyio
async def test_update_user_details(async_client: AsyncClient):
    response = await async_client.put(
        "/users/",
        json={"password": "newpassword", "categories": ["Health", "Travel"]}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User updated successfully"
    assert "updated_user" in response.json()
    assert "Health" in response.json()["updated_user"]["categories"]

@pytest.mark.anyio
async def test_update_token_expiration(async_client: AsyncClient):
    response = await async_client.put(
        "/users/token/",
        params={"token_expires": 60}  # Update token expiration to 60 minutes using query parameters
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Token expiration updated successfully"

@pytest.mark.anyio
async def test_delete_token(async_client: AsyncClient):
    response = await async_client.delete("/users/token/")
    assert response.status_code == 200,response.json()
    assert response.json()["message"] == "Token deleted successfully",response.json()

@pytest.mark.anyio
async def test_delete_user(async_client: AsyncClient):
    response = await async_client.delete("/users/")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

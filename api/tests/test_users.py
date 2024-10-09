# test_user_expenses.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from api.app import app  # Assuming you have a main.py that imports and includes your routers
from motor.motor_asyncio import AsyncIOMotorClient
from api.config import MONGO_URI

# MongoDB setup
client = AsyncIOMotorClient(MONGO_URI)
db = client.mmdb
users_collection = db.users
tokens_collection = db.tokens
accounts_collection = db.accounts

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

@pytest.fixture(scope="session")
async def access_token(async_client: AsyncClient):
    response = await async_client.post(
        "/users/token/",
        data={"username": "testuser", "password": "testpassword"}
    )
    return response.json()["access_token"]

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

@pytest.mark.anyio
async def test_get_user_details(async_client: AsyncClient, access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await async_client.get("/users/", headers=headers)
    assert response.status_code == 200
    assert "username" in response.json()
    assert response.json()["username"] == "testuser"

@pytest.mark.anyio
async def test_cleanup_user():
    # Find the user first
    user = await users_collection.find_one({"username": "testuser"})
    if user:
        user_id = str(user["_id"])
        await users_collection.delete_one({"_id": user["_id"]})
        await tokens_collection.delete_many({"user_id": user_id})
        await accounts_collection.delete_many({"user_id": user_id})

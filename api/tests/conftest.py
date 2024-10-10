# test_expenses.py
import pytest
from httpx import AsyncClient, ASGITransport
from api.app import app
from datetime import datetime
from asyncio import get_event_loop
import asyncio

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

        
@pytest.fixture(scope="session")
async def async_client_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a user and log in to use for expenses tests
        await client.post(
            "/users/",
            json={"username": "testuser", "password": "testpassword"}
        )
        response = await client.post(
            "/users/token/",
            data={"username": "testuser", "password": "testpassword"}
        )
        token = response.json()["access_token"]
        client.headers.update({"token": token})
        
        yield client

        # Teardown: Delete the user after the tests in this module
        response = await client.delete("/users/")
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "User deleted successfully", response.json()


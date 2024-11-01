from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from httpx import AsyncClient

from api.app import app
from api.routers.analytics import router as analytics_router
from api.utils.auth import verify_token


@pytest.fixture
def sample_data():
    # Sample data mimicking the format fetched from MongoDB for 60 days of expenses
    return [
        {
            "_id": "6724032b8c1b4460b0741189",
            "account_name": "abc",
            "amount": 100.0,
            "category": "Food",
            "currency": "USD",
            "date": datetime(2024, 10, 1, 22, 22, 35),
            "description": None,
            "user_id": "6723e84242163f8755603857",
        },
        {
            "_id": "672403588c1b4460b074118a",
            "account_name": "abc",
            "amount": 15.0,
            "category": "Groceries",
            "currency": "USD",
            "date": datetime(2024, 10, 31, 22, 23, 20),
            "description": None,
            "user_id": "6723e84242163f8755603857",
        },
        {
            "_id": "672403698c1b4460b074118b",
            "account_name": "abc",
            "amount": 57.0,
            "category": "Transport",
            "currency": "USD",
            "date": datetime(2024, 10, 31, 22, 23, 37),
            "description": None,
            "user_id": "6723e84242163f8755603857",
        },
    ]


@pytest.mark.anyio
async def test_expense_bar_valid_token(async_client_auth: AsyncClient, sample_data):
    with patch("api.utils.auth.verify_token", return_value="6723e84242163f8755603857"):
        with patch("api.routers.analytics.expenses_collection.find") as mock_find:
            mock_find.return_value.to_list = AsyncMock(return_value=sample_data)
            response = await async_client_auth.get(
                "/analytics/expense/bar",
                params={"x_days": 30},
                headers={"token": "valid_token"},
            )
            assert response.status_code == 401


@pytest.mark.anyio
async def test_expense_bar_no_expenses(async_client_auth: AsyncClient):
    with patch("api.utils.auth.verify_token", return_value="6723e84242163f8755603857"):
        with patch("api.routers.analytics.expenses_collection.find") as mock_find:
            mock_find.return_value.to_list = AsyncMock(return_value=[])
            response = await async_client_auth.get(
                "/analytics/expense/bar",
                params={"x_days": 30},
                headers={"token": "valid_token"},
            )
            assert response.status_code == 401
            assert "Invalid authentication credentials" in response.json().get(
                "detail", ""
            )


@pytest.mark.anyio
async def test_expense_bar_invalid_token(async_client_auth: AsyncClient):
    with patch("api.utils.auth.verify_token", return_value=None):
        response = await async_client_auth.get(
            "/analytics/expense/bar",
            params={"x_days": 30},
            headers={"token": "invalid_token"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid authentication credentials"


@pytest.mark.anyio
async def test_expense_pie_valid_token(async_client_auth: AsyncClient, sample_data):
    with patch("api.utils.auth.verify_token", return_value="6723e84242163f8755603857"):
        with patch("api.routers.analytics.expenses_collection.find") as mock_find:
            mock_find.return_value.to_list = AsyncMock(return_value=sample_data)
            response = await async_client_auth.get(
                "/analytics/expense/pie",
                params={"x_days": 30},
                headers={"token": "valid_token"},
            )
            assert response.status_code == 401


@pytest.mark.anyio
async def test_expense_pie_no_expenses(async_client_auth: AsyncClient):
    with patch("api.utils.auth.verify_token", return_value="6723e84242163f8755603857"):
        with patch("api.routers.analytics.expenses_collection.find") as mock_find:
            mock_find.return_value.to_list = AsyncMock(return_value=[])
            response = await async_client_auth.get(
                "/analytics/expense/pie",
                params={"x_days": 30},
                headers={"token": "valid_token"},
            )
            assert response.status_code == 401
            assert "Invalid authentication credentials" in response.json().get(
                "detail", ""
            )


@pytest.mark.anyio
async def test_expense_pie_invalid_token(async_client_auth: AsyncClient):
    with patch("api.utils.auth.verify_token", return_value=None):
        response = await async_client_auth.get(
            "/analytics/expense/pie",
            params={"x_days": 30},
            headers={"token": "invalid_token"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid authentication credentials"


@pytest.mark.anyio
async def test_expense_bar_missing_token(async_client_auth: AsyncClient):
    response = await async_client_auth.get(
        "/analytics/expense/bar", params={"x_days": 30}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "No expenses found for the specified period"

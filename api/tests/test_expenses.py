# test_expenses.py
import asyncio
import datetime
from asyncio import get_event_loop
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from bson import ObjectId
from currency_converter import CurrencyConverter
from fastapi import APIRouter, Depends, Header, HTTPException
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

import api.routers.expenses
from api.app import app
from api.config import MONGO_URI

# MongoDB setup
client = AsyncIOMotorClient(MONGO_URI)
db = client.mmdb
users_collection = db.users
expenses_collection = db.expenses
accounts_collection = db.accounts
tokens_collection = db.tokens


# Test case for when "from_cur" and "to_cur" are the same
def test_convert_currency_same_currency():
    amount = 100
    result = api.routers.expenses.convert_currency(100, "USD", "USD")
    assert (
        result == amount
    ), "Conversion should return the original amount if currencies are the same"


# Test case for successful conversion
@patch("api.routers.expenses.currency_converter.convert")
def test_convert_currency_success(mock_convert):
    # Mock the currency converter to return a fixed value
    mock_convert.return_value = 85.0

    amount = 100
    from_cur = "USD"
    to_cur = "EUR"
    result = api.routers.expenses.convert_currency(amount, from_cur, to_cur)

    mock_convert.assert_called_once_with(amount, from_cur, to_cur)
    assert result == 85.0, "Conversion should match the mocked return value"


# Test case for failed conversion (e.g., unsupported currency)
@patch("api.routers.expenses.currency_converter.convert")
def test_convert_currency_failure(mock_convert):
    # Simulate an exception being raised during conversion
    mock_convert.side_effect = Exception("Unsupported currency")

    amount = 100
    from_cur = "USD"
    to_cur = "XYZ"  # Assume "XYZ" is an unsupported currency
    with pytest.raises(HTTPException) as exc_info:
        api.routers.expenses.convert_currency(amount, from_cur, to_cur)

    assert exc_info.value.status_code == 400
    assert "Currency conversion failed" in str(
        exc_info.value.detail
    ), "Exception message should indicate conversion failure"


@pytest.mark.anyio
async def test_add_expense(async_client_auth: AsyncClient):
    response = await async_client_auth.post(
        "/expenses/",
        json={
            "amount": 50.0,
            "currency": "USD",
            "category": "Food",
            "description": "Grocery shopping",
            "account_type": "Checking",
        },
    )
    assert response.status_code == 200, response.json()
    assert response.json()["message"] == "Expense added successfully"
    assert "expense" in response.json()


@pytest.mark.anyio
async def test_add_expense_invalid_currency(async_client_auth: AsyncClient):
    response = await async_client_auth.post(
        "/expenses/",
        json={"amount": 100.0, "currency": "INVALID", "category": "Food"},
    )
    assert response.status_code == 400
    assert response.json()["detail"].startswith(
        "Currency type is not added to user account. Available currencies are"
    ), response.json()


@pytest.mark.anyio
async def test_add_expense_insufficient_balance(async_client_auth: AsyncClient):
    response = await async_client_auth.post(
        "/expenses/",
        json={"amount": 1000000.0, "currency": "USD", "category": "Food"},
    )
    assert response.status_code == 400
    assert response.json()["detail"].startswith("Insufficient balance")


@pytest.mark.anyio
async def test_add_expense_invalid_category(async_client_auth: AsyncClient):
    response = await async_client_auth.post(
        "/expenses/",
        json={"amount": 50.0, "currency": "USD", "category": "InvalidCategory"},
    )
    assert response.status_code == 400
    assert response.json()["detail"].startswith(
        "Category is not present in the user account"
    )


@pytest.mark.anyio
async def test_add_expense_invalid_account(async_client_auth: AsyncClient):
    response = await async_client_auth.post(
        "/expenses/",
        json={
            "amount": 50.0,
            "currency": "USD",
            "category": "Food",
            "account_type": "InvalidAccount",
        },
    )
    assert response.status_code == 400, response.json()
    assert response.json()["detail"] == ("Invalid account type")


@pytest.mark.anyio
async def test_get_expenses(async_client_auth: AsyncClient):
    response = await async_client_auth.get("/expenses/")
    assert response.status_code == 200
    assert "expenses" in response.json()
    assert isinstance(response.json()["expenses"], list)


@pytest.mark.anyio
async def test_update_expense(async_client_auth: AsyncClient):
    # First, add an expense
    add_response = await async_client_auth.post(
        "/expenses/",
        json={
            "amount": 30.0,
            "currency": "USD",
            "category": "Transport",
            "description": "Taxi fare",
            "account_type": "Checking",
        },
    )
    assert add_response.status_code == 200, add_response.json()
    expense_id = add_response.json()["expense"]["_id"]

    # Update the expense
    response = await async_client_auth.put(
        f"/expenses/{expense_id}",
        json={
            "amount": 40.0,
            "description": "Updated taxi fare",
            "category": "Transport",
        },
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Expense updated successfully"
    assert response.json()["updated_expense"]["amount"] == 40.0


@pytest.mark.anyio
async def test_update_expense_empty(async_client_auth: AsyncClient):
    # First, add an expense
    add_response = await async_client_auth.post(
        "/expenses/",
        json={
            "amount": 30.0,
            "currency": "USD",
            "category": "Transport",
            "description": "Taxi fare",
            "account_type": "Checking",
        },
    )
    assert add_response.status_code == 200, add_response.json()
    expense_id = add_response.json()["expense"]["_id"]

    # Update the expense
    response = await async_client_auth.put(f"/expenses/{expense_id}", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "No fields to update"


@pytest.mark.anyio
async def test_update_expense_currency_404(async_client_auth: AsyncClient):
    # First, add an expense
    add_response = await async_client_auth.post(
        "/expenses/",
        json={
            "amount": 30.0,
            "currency": "USD",
            "category": "Food",
            "description": "Patel Bros",
            "account_type": "Checking",
        },
    )
    assert add_response.status_code == 200, add_response.json()
    expense_id = add_response.json()["expense"]["_id"]
    # Update the expense
    response = await async_client_auth.put(
        f"/expenses/{expense_id}",
        json={"amount": 40.0, "currency": "InvalidCurrency"},
    )
    assert response.status_code == 400
    assert response.json()["detail"].startswith(
        "Currency type is not added to user account"
    )


@pytest.mark.anyio
async def test_update_expense_category_404(async_client_auth: AsyncClient):
    # First, add an expense
    add_response = await async_client_auth.post(
        "/expenses/",
        json={
            "amount": 30.0,
            "currency": "USD",
            "category": "Food",
            "description": "Patel Bros",
            "account_type": "Checking",
        },
    )
    assert add_response.status_code == 200, add_response.json()
    expense_id = add_response.json()["expense"]["_id"]
    # Update the expense
    response = await async_client_auth.put(
        f"/expenses/{expense_id}",
        json={"amount": 40.0, "category": "InvalidCategory"},
    )
    assert response.status_code == 400
    assert response.json()["detail"].startswith(
        "Category is not present in the user account"
    )


@pytest.mark.anyio
async def test_update_expense_account_404(async_client_auth: AsyncClient):
    # First, add an expense
    add_response = await async_client_auth.post(
        "/expenses/",
        json={
            "amount": 30.0,
            "currency": "USD",
            "category": "Food",
            "description": "Patel Bros",
            "account_type": "Checking",
        },
    )
    assert add_response.status_code == 200, add_response.json()
    expense_id = add_response.json()["expense"]["_id"]
    await expenses_collection.update_one(
        {"_id": ObjectId(expense_id)}, {"$set": {"account_type": "InvalidAccount"}}
    )
    # Update the expense
    response = await async_client_auth.put(
        f"/expenses/{expense_id}",
        json={"amount": 40.0, "account_type": "InvalidAccount"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"


@pytest.mark.anyio
async def test_update_expense_insufficient_balance(async_client_auth: AsyncClient):
    # First, add an expense
    add_response = await async_client_auth.post(
        "/expenses/",
        json={
            "amount": 30.0,
            "currency": "USD",
            "category": "Food",
            "description": "Patel Bros",
            "account_type": "Checking",
        },
    )
    assert add_response.status_code == 200, add_response.json()
    expense_id = add_response.json()["expense"]["_id"]
    # Update the expense
    response = await async_client_auth.put(
        f"/expenses/{expense_id}",
        json={"amount": 400000.0},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient balance to update the expense"


@pytest.mark.anyio
async def test_delete_expense(async_client_auth: AsyncClient):
    # First, add an expense
    add_response = await async_client_auth.post(
        "/expenses/",
        json={
            "amount": 20.0,
            "currency": "USD",
            "category": "Shopping",
            "description": "Book purchase",
            "account_type": "Checking",
        },
    )
    assert add_response.status_code == 200, add_response.json()
    expense_id = add_response.json()["expense"]["_id"]

    # Delete the expense
    response = await async_client_auth.delete(f"/expenses/{expense_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Expense deleted successfully"


@pytest.mark.anyio
async def test_delete_expense_not_found(async_client_auth: AsyncClient):
    response = await async_client_auth.delete("/expenses/507f1f77bcf86cd799439011")
    assert response.status_code == 404
    assert response.json()["detail"] == "Expense not found"


@pytest.mark.anyio
async def test_update_expense_not_found(async_client_auth: AsyncClient):
    response = await async_client_auth.put(
        "/expenses/507f1f77bcf86cd799439011", json={"amount": 100.0}
    )
    assert response.status_code == 404, response.json()
    assert response.json()["detail"] == "Expense not found"


@pytest.mark.anyio
async def test_currency_conversion(async_client_auth: AsyncClient):
    response = await async_client_auth.post(
        "/expenses/",
        json={
            "amount": 50,
            "currency": "USD",
            "category": "Food",
            "account_type": "Checking",
        },
    )
    assert response.status_code == 200, response.json()
    balance = response.json()["balance"]
    response = await async_client_auth.post(
        "/expenses/",
        json={
            "amount": 1000,
            "currency": "INR",
            "category": "Food",
            "account_type": "Checking",
        },
    )
    assert response.status_code == 200, response.json()
    assert "expense" in response.json(), response.json()
    assert response.json()["expense"]["currency"] == "INR"

    expense_id = response.json()["expense"]["_id"]
    # update
    response = await async_client_auth.put(
        f"/expenses/{expense_id}", json={"amount": 50, "currency": "USD"}
    )
    assert response.status_code == 200
    # delete
    response = await async_client_auth.delete(f"/expenses/{expense_id}")
    assert response.status_code == 200
    assert response.json()["balance"] == balance

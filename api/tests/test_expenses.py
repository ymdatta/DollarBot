# test_expenses.py
import pytest
from httpx import AsyncClient, ASGITransport
from api.app import app
from datetime import datetime
from asyncio import get_event_loop
import asyncio


@pytest.mark.anyio
async def test_add_expense(async_client_auth: AsyncClient):
    response = await async_client_auth.post(
        "/expenses/",
        params={
            "amount": 50.0,
            "currency": "USD",
            "category": "Food",
            "description": "Grocery shopping",
            "account_type": "Checking"
        }
    )
    assert response.status_code == 200, response.json()
    assert response.json()["message"] == "Expense added successfully"
    assert "expense" in response.json()

@pytest.mark.anyio
async def test_add_expense_invalid_currency(async_client_auth: AsyncClient):
    response = await async_client_auth.post(
        "/expenses/",
        params={
            "amount": 100.0,
            "currency": "INVALID",
            "category": "Food"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"].startswith("Currency type is not added to user account. Available currencies are"), response.json()

@pytest.mark.anyio
async def test_add_expense_insufficient_balance(async_client_auth: AsyncClient):
    response = await async_client_auth.post(
        "/expenses/",
        params={
            "amount": 1000000.0,
            "currency": "USD",
            "category": "Food"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"].startswith("Insufficient balance")

@pytest.mark.anyio
async def test_add_expense_invalid_category(async_client_auth: AsyncClient):
    response = await async_client_auth.post(
        "/expenses/",
        params={
            "amount": 50.0,
            "currency": "USD",
            "category": "InvalidCategory"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"].startswith("Category is not present in the user account")

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
        params={
            "amount": 30.0,
            "currency": "USD",
            "category": "Transport",
            "description": "Taxi fare",
            "account_type": "Checking"
        }
    )
    expense_id = add_response.json()["expense"]["_id"]

    # Update the expense
    response = await async_client_auth.put(
        f"/expenses/{expense_id}",
        params={
            "amount": 40.0,
            "description": "Updated taxi fare"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Expense updated successfully"
    assert response.json()["updated_expense"]["amount"] == 40.0

@pytest.mark.anyio
async def test_delete_expense(async_client_auth: AsyncClient):
    # First, add an expense
    add_response = await async_client_auth.post(
        "/expenses/",
        params={
            "amount": 20.0,
            "currency": "USD",
            "category": "Shopping",
            "description": "Book purchase",
            "account_type": "Checking"
        }
    )
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
        "/expenses/507f1f77bcf86cd799439011",
        params={"amount": 100.0}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Expense not found"


@pytest.mark.anyio
async def test_currency_conversion(async_client_auth: AsyncClient):
    response = await async_client_auth.post(
        "/expenses/",
        params={
            "amount": 50,
            "currency": "USD",
            "category": "Food",
            "account_type": "Checking"
        }
    )
    assert response.status_code == 200, response.json()
    balance = response.json()["balance"]
    response = await async_client_auth.post(
        "/expenses/",
        params={
            "amount": 1000,
            "currency": "INR",
            "category": "Food",
            "account_type": "Checking"
        }
    )
    assert response.status_code == 200, response.json()
    assert "expense" in response.json(), response.json()
    assert response.json()["expense"]["currency"] == "INR"
    
    expense_id = response.json()["expense"]["_id"]
    #update
    response = await async_client_auth.put(
        f"/expenses/{expense_id}",
        params={
            "amount": 50,
            "currency": "USD"
        }
    )
    assert response.status_code == 200
    # delete
    response = await async_client_auth.delete(
        f"/expenses/{expense_id}"
    )
    assert response.status_code == 200
    assert response.json()["balance"] == balance


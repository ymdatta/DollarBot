# test_expenses.py
import datetime
from unittest.mock import patch

import pytest
from bson import ObjectId
from fastapi import HTTPException
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

import api.routers.expenses
from api.config import MONGO_URI

# MongoDB setup
client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)
db = client.mmdb
users_collection = db.users
expenses_collection = db.expenses
accounts_collection = db.accounts
tokens_collection = db.tokens


class TestConvertCurrency:
    # Test case for when "from_cur" and "to_cur" are the same
    def test_same_currency(self):
        amount = 100
        result = api.routers.expenses.convert_currency(100, "USD", "USD")
        assert (
            result == amount
        ), "Conversion should return the original amount if currencies are the same"

    # Test case for successful conversion
    @patch("api.routers.expenses.currency_converter.convert")
    def test_success(self, mock_convert):
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
    def test_failure(self, mock_convert):
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
class TestExpenseAdd:
    async def test_valid(self, async_client_auth: AsyncClient):
        response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 50.0,
                "currency": "USD",
                "category": "Food",
                "description": "Grocery shopping",
                "account_name": "Checking",
            },
        )
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Expense added successfully"
        assert "expense" in response.json()

    async def test_invalid_currency(self, async_client_auth: AsyncClient):
        response = await async_client_auth.post(
            "/expenses/",
            json={"amount": 100.0, "currency": "INVALID", "category": "Food"},
        )
        assert response.status_code == 400
        assert response.json()["detail"].startswith(
            "Currency type is not added to user account. Available currencies are"
        ), response.json()

    async def test_insufficient_balance(self, async_client_auth: AsyncClient):
        response = await async_client_auth.post(
            "/expenses/",
            json={"amount": 1000000.0, "currency": "USD", "category": "Food"},
        )
        assert response.status_code == 400
        assert response.json()["detail"].startswith("Insufficient balance")

    async def test_invalid_category(self, async_client_auth: AsyncClient):
        response = await async_client_auth.post(
            "/expenses/",
            json={"amount": 50.0, "currency": "USD", "category": "InvalidCategory"},
        )
        assert response.status_code == 400
        assert response.json()["detail"].startswith(
            "Category is not present in the user account"
        )

    async def test_invalid_account(self, async_client_auth: AsyncClient):
        response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 50.0,
                "currency": "USD",
                "category": "Food",
                "account_name": "InvalidAccount",
            },
        )
        assert response.status_code == 400, response.json()
        assert response.json()["detail"] == ("Invalid account type")

    async def test_no_date(self, async_client_auth: AsyncClient):
        """
        Test case when no date is provided, should default to current datetime.
        """
        response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 100.0,
                "currency": "USD",
                "category": "Food",
                "description": "Grocery shopping",
                "account_name": "Checking",
            },
        )
        assert response.status_code == 200, response.json()
        expense_date = response.json()["expense"]["date"]
        assert isinstance(expense_date, str) and datetime.datetime.fromisoformat(
            expense_date
        ), "The date should be a valid ISO datetime"

    async def test_valid_date(self, async_client_auth: AsyncClient):
        """
        Test case when a valid ISO date is provided.
        """
        valid_date = "2024-10-06T12:00:00"
        response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 50.0,
                "currency": "USD",
                "category": "Transport",
                "description": "Bus fare",
                "account_name": "Checking",
                "date": valid_date,
            },
        )
        assert response.status_code == 200, response.json()
        expense_date = response.json()["expense"]["date"]
        assert datetime.datetime.fromisoformat(
            expense_date
        ), "The date should be a valid ISO datetime"
        assert (
            expense_date == valid_date
        ), "The date should match the user-provided date"

    async def test_invalid_date(self, async_client_auth: AsyncClient):
        """
        Test case when an invalid date format is provided.
        """
        invalid_date = "2024-10-96 90:00:00"  # Invalid format (missing 'T')
        response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 75.0,
                "currency": "USD",
                "category": "Groceries",
                "description": "Weekly groceries",
                "account_name": "Checking",
                "date": invalid_date,
            },
        )
        assert response.status_code == 422, response.json()

    async def test_empty_string_date(self, async_client_auth: AsyncClient):
        """
        Test case when an invalid date format is provided.
        """
        response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 75.0,
                "currency": "USD",
                "category": "Groceries",
                "description": "Weekly groceries",
                "account_name": "Checking",
                "date": "",
            },
        )
        assert response.status_code == 422, response.json()


@pytest.mark.anyio
class TestExpenseGet:
    async def test_all(self, async_client_auth: AsyncClient):
        """
        Test to retrieve all expenses for a user.
        """
        # Create a new expense first to ensure there is something to retrieve
        response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 50.0,
                "currency": "USD",
                "category": "Food",
                "description": "Grocery shopping",
                "account_name": "Checking",
            },
        )
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Expense added successfully"

        # Test to get all expenses
        response = await async_client_auth.get("/expenses/")
        assert response.status_code == 200, response.json()
        assert "expenses" in response.json()
        assert isinstance(response.json()["expenses"], list)

    async def test_specific(self, async_client_auth: AsyncClient):
        """
        Test to retrieve a specific expense by its ID.
        """
        # Create a new expense
        response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 100.0,
                "currency": "USD",
                "category": "Transport",
                "description": "Taxi fare",
                "account_name": "Checking",
            },
        )
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Expense added successfully"

        # Get the inserted expense ID
        expense_id = response.json()["expense"]["_id"]

        # Test to get the specific expense by ID
        response = await async_client_auth.get(f"/expenses/{expense_id}")
        assert response.status_code == 200, response.json()
        assert "_id" in response.json()
        assert response.json()["_id"] == expense_id

    async def test_not_found(self, async_client_auth: AsyncClient):
        """
        Test to retrieve an expense by a non-existent ID.
        """
        # Generate a random non-existent ObjectId
        random_expense_id = str(ObjectId())

        response = await async_client_auth.get(f"/expenses/{random_expense_id}")
        assert response.status_code == 404, response.json()
        assert response.json()["detail"] == "Expense not found"


@pytest.mark.anyio
class TestExpenseUpdate:
    async def test_valid(self, async_client_auth: AsyncClient):
        # First, add an expense
        add_response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 30.0,
                "currency": "USD",
                "category": "Transport",
                "description": "Taxi fare",
                "account_name": "Checking",
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

    async def test_empty(self, async_client_auth: AsyncClient):
        # First, add an expense
        add_response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 30.0,
                "currency": "USD",
                "category": "Transport",
                "description": "Taxi fare",
                "account_name": "Checking",
            },
        )
        assert add_response.status_code == 200, add_response.json()
        expense_id = add_response.json()["expense"]["_id"]

        # Update the expense
        response = await async_client_auth.put(f"/expenses/{expense_id}", json={})
        assert response.status_code == 400
        assert response.json()["detail"] == "No fields to update"

    async def test_currency_404(self, async_client_auth: AsyncClient):
        # First, add an expense
        add_response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 30.0,
                "currency": "USD",
                "category": "Food",
                "description": "Patel Bros",
                "account_name": "Checking",
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

    async def test_category_404(self, async_client_auth: AsyncClient):
        # First, add an expense
        add_response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 30.0,
                "currency": "USD",
                "category": "Food",
                "description": "Patel Bros",
                "account_name": "Checking",
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

    async def test_account_404(self, async_client_auth: AsyncClient):
        # First, add an expense
        add_response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 30.0,
                "currency": "USD",
                "category": "Food",
                "description": "Patel Bros",
                "account_name": "Checking",
            },
        )
        assert add_response.status_code == 200, add_response.json()
        expense_id = add_response.json()["expense"]["_id"]
        await expenses_collection.update_one(
            {"_id": ObjectId(expense_id)}, {"$set": {"account_name": "InvalidAccount"}}
        )
        # Update the expense
        response = await async_client_auth.put(
            f"/expenses/{expense_id}",
            json={"amount": 40.0, "account_name": "InvalidAccount"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Account not found"

    async def test_insufficient_balance(self, async_client_auth: AsyncClient):
        # First, add an expense
        add_response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 30.0,
                "currency": "USD",
                "category": "Food",
                "description": "Patel Bros",
                "account_name": "Checking",
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

    async def test_not_found(self, async_client_auth: AsyncClient):
        response = await async_client_auth.put(
            "/expenses/507f1f77bcf86cd799439011", json={"amount": 100.0}
        )
        assert response.status_code == 404, response.json()
        assert response.json()["detail"] == "Expense not found"

    async def test_valid_date(self, async_client_auth):
        # Create an expense first
        create_response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 5.0,
                "currency": "USD",
                "category": "Food",
                "account_name": "Checking",
            },
        )
        assert create_response.status_code == 200, create_response.json()
        expense_id = create_response.json()["expense"]["_id"]

        # Update the expense with a valid date
        response = await async_client_auth.put(
            f"/expenses/{expense_id}",
            json={"date": "2024-10-06T10:00:00"},
        )
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Expense updated successfully"
        assert "updated_expense" in response.json()
        assert response.json()["updated_expense"]["date"] == "2024-10-06T10:00:00"

    async def test_invalid_date(self, async_client_auth):
        # Create an expense first
        create_response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 5.0,
                "currency": "USD",
                "category": "Food",
                "account_name": "Checking",
            },
        )
        assert create_response.status_code == 200, create_response.json()
        expense_id = create_response.json()["expense"]["_id"]

        # Attempt to update the expense with an invalid date
        response = await async_client_auth.put(
            f"/expenses/{expense_id}",
            json={"date": "invalid-date-format"},
        )
        assert response.status_code == 422, response.json()


@pytest.mark.anyio
class TestExpenseDelete:
    async def test_specific_valid(self, async_client_auth: AsyncClient):
        # First, add an expense
        add_response = await async_client_auth.post(
            "/expenses/",
            json={
                "amount": 20.0,
                "currency": "USD",
                "category": "Shopping",
                "description": "Book purchase",
                "account_name": "Checking",
            },
        )
        assert add_response.status_code == 200, add_response.json()
        expense_id = add_response.json()["expense"]["_id"]

        # Delete the expense
        response = await async_client_auth.delete(f"/expenses/{expense_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Expense deleted successfully"

    async def test_specific_404(self, async_client_auth: AsyncClient):
        response = await async_client_auth.delete("/expenses/507f1f77bcf86cd799439011")
        assert response.status_code == 404
        assert response.json()["detail"] == "Expense not found"

    # async def test_all(self, async_client_auth: AsyncClient):
    #     """
    #     Test deleting all expenses for the authenticated user.
    #     """
    #     # Create a few expenses to ensure there is something to delete
    #     for i in range(3):
    #         response = await async_client_auth.post(
    #             "/expenses/",
    #             json={
    #                 "amount": 100.0 + i,
    #                 "currency": "USD",
    #                 "category": "Transport",
    #                 "description": f"Taxi fare {i}",
    #                 "account_name": "Checking",
    #             },
    #         )
    #         assert response.status_code == 200, response.json()
    #         assert response.json()["message"] == "Expense added successfully"

    #     # Test to delete all expenses
    #     response = await async_client_auth.delete("/expenses/all")
    #     assert response.status_code == 200, response.json()
    #     assert "expenses deleted successfully" in response.json()["message"]

    #     # Test to get all expenses to verify deletion
    #     response = await async_client_auth.get("/expenses/")
    #     assert response.status_code == 200, response.json()
    #     assert len(response.json()["expenses"]) == 0

    async def test_all(self, async_client_auth: AsyncClient):
        """
        Test deleting all expenses for the authenticated user for a specific account.
        """
        # Create an account for testing
        account_name = "1234"
        create_response = await async_client_auth.post(
            "/accounts/",
            json={"name": account_name, "balance": 500.0, "currency": "USD"},
        )
        assert create_response.status_code == 200, create_response.json()

        # Initial balance in the account
        initial_balance = 500.0

        # Sample Expenses
        total_expense_amount: int = 0
        for i in range(3):
            expense_amount: int = 10 + i
            total_expense_amount += expense_amount

            response = await async_client_auth.post(
                "/expenses/",
                json={
                    "amount": expense_amount,
                    "currency": "USD",
                    "category": "Transport",
                    "description": f"Taxi fare {i}",
                    "account_name": account_name,
                },
            )
            assert response.status_code == 200, response.json()
            assert response.json()["message"] == "Expense added successfully"

        # Calculate expected balance after expenses are added
        bal_after_expenses = initial_balance - total_expense_amount

        # Test to delete all expenses for the specified account
        response = await async_client_auth.delete(f"/expenses/all/{account_name}")
        print(response.json())
        assert response.status_code == 200, response.json()
        assert (
            f"Expenses deleted successfully from account {account_name}"
            in response.json()["message"]
        )

        # Test to get all accounts to verify deletion for the specified account
        response = await async_client_auth.get("/accounts/")
        assert response.status_code == 200, response.json()
        accounts = response.json()["accounts"]

        # Find the account with the name account_name
        checking_account = next(
            (acc for acc in accounts if acc["name"] == account_name), None
        )
        assert checking_account is not None, "Checking account should exist"

        # Test to get account balance after deleting expenses
        assert (
            checking_account["balance"] == initial_balance
        ), "Balance should revert to initial balance after deletion"

    async def test_all_but_empty(self, async_client_auth: AsyncClient):
        """
        Test deleting all expenses when no expenses exist.
        """
        # Create an account for testing
        create_response = await async_client_auth.post(
            "/accounts/",
            json={"name": "EmptyAccount", "balance": 500.0, "currency": "USD"},
        )
        assert create_response.status_code == 200, create_response.json()

        # Test to delete all expenses when there are no expenses
        response = await async_client_auth.delete("/expenses/all/EmptyAccount")
        assert response.status_code == 404, response.json()
        assert (
            response.json()["detail"]
            == "No expenses found to delete in the specified account"
        )


@pytest.mark.anyio
async def test_currency_conversion(async_client_auth: AsyncClient):
    response = await async_client_auth.post(
        "/expenses/",
        json={
            "amount": 50,
            "currency": "USD",
            "category": "Food",
            "account_name": "Checking",
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
            "account_name": "Checking",
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

# import pytest
# from fastapi.testclient import TestClient
# from httpx import AsyncClient
# from unittest.mock import patch, MagicMock
# from datetime import datetime, timedelta
# import pandas as pd
# from typing import Optional

# from api.app import app  # Import FastAPI app here

# client = TestClient(app)

# # Mock sample data for testing
# def sample_expense_data(days_ago, amount=100, category="food"):
#     return {
#         "date": datetime.now() - timedelta(days=days_ago),
#         "amount": amount,
#         "category": category
#     }

# @pytest.mark.asyncio
# async def test_get_last_7_days_expenses_success():
#     # Mock MongoDB data
#     mock_data = [
#         sample_expense_data(days_ago=2, amount=50),
#         sample_expense_data(days_ago=5, amount=75),
#     ]
#     with patch("api.routers.analytics.get_expense_data") as mock_get_expense_data:
#         mock_get_expense_data.return_value = pd.DataFrame(mock_data)
#         async with AsyncClient(app=app, base_url="http://test") as ac:
#             response = await ac.get("/analytics/last-7-days")

#     assert response.status_code == 200
#     assert "Last 7 Days Expenses" in response.text
#     assert "data:image/png;base64," in response.text  # Check for base64 image data

# @pytest.mark.asyncio
# async def test_get_last_7_days_expenses_no_data():
#     with patch("api.analytics.get_expense_data") as mock_get_expense_data:
#         mock_get_expense_data.return_value = pd.DataFrame()  # No data
#         async with AsyncClient(app=app, base_url="http://test") as ac:
#             response = await ac.get("/analytics/last-7-days")

#     assert response.status_code == 404
#     assert response.json()["detail"] == "No expenses found for the last 7 days"

# @pytest.mark.asyncio
# async def test_get_last_one_month_expenses_success():
#     # Mock MongoDB data
#     mock_data = [
#         sample_expense_data(days_ago=10, amount=200),
#         sample_expense_data(days_ago=20, amount=150),
#     ]
#     with patch("api.analytics.get_expense_data") as mock_get_expense_data:
#         mock_get_expense_data.return_value = pd.DataFrame(mock_data)
#         async with AsyncClient(app=app, base_url="http://test") as ac:
#             response = await ac.get("/analytics/last-one-month")

#     assert response.status_code == 200
#     assert "Last One Month Expenses" in response.text
#     assert "data:image/png;base64," in response.text  # Check for base64 image data

# @pytest.mark.asyncio
# async def test_get_last_one_month_expenses_no_data():
#     with patch("api.analytics.get_expense_data") as mock_get_expense_data:
#         mock_get_expense_data.return_value = pd.DataFrame()  # No data
#         async with AsyncClient(app=app, base_url="http://test") as ac:
#             response = await ac.get("/analytics/last-one-month")

#     assert response.status_code == 404
#     assert response.json()["detail"] == "No expenses found for the last one month"

# @pytest.mark.asyncio
# async def test_get_category_wise_expenses_success():
#     # Mock MongoDB data with multiple categories
#     mock_data = [
#         sample_expense_data(days_ago=15, amount=100, category="food"),
#         sample_expense_data(days_ago=10, amount=200, category="transport"),
#         sample_expense_data(days_ago=5, amount=50, category="utilities"),
#     ]
#     with patch("api.analytics.get_expense_data") as mock_get_expense_data:
#         mock_get_expense_data.return_value = pd.DataFrame(mock_data)
#         async with AsyncClient(app=app, base_url="http://test") as ac:
#             response = await ac.get("/analytics/category-wise")

#     assert response.status_code == 200
#     assert "Category Wise Expenses" in response.text
#     assert "data:image/png;base64," in response.text  # Check for base64 image data

# @pytest.mark.asyncio
# async def test_get_category_wise_expenses_no_data():
#     with patch("api.analytics.get_expense_data") as mock_get_expense_data:
#         mock_get_expense_data.return_value = pd.DataFrame()  # No data
#         async with AsyncClient(app=app, base_url="http://test") as ac:
#             response = await ac.get("/analytics/category-wise")

#     assert response.status_code == 404
#     assert response.json()["detail"] == "No expenses found"

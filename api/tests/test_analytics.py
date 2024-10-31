from datetime import datetime, timedelta
from typing import Optional
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from api.app import app  # Import FastAPI app here

client = TestClient(app)


@pytest.mark.anyio
class TestAnalyticsEndpoints:
    async def test_get_last_7_days_expenses(self, async_client_auth: AsyncClient):
        """
        Test retrieving expenses for the last 7 days.
        """
        response = await async_client_auth.get("/analytics/last-7-days")
        if response.status_code == 404:
            # Check for both custom and default 404 messages
            assert response.json()["detail"] in [
                "No expenses found for the last 7 days",
                "Not Found",
            ]
        else:
            assert response.status_code == 200
            assert "<img src=" in response.text

    async def test_get_last_one_month_expenses(self, async_client_auth: AsyncClient):
        """
        Test retrieving expenses for the last one month.
        """
        response = await async_client_auth.get("/analytics/last-one-month")
        if response.status_code == 404:
            # Check for both custom and default 404 messages
            assert response.json()["detail"] in [
                "No expenses found for the last one month",
                "Not Found",
            ]
        else:
            assert response.status_code == 200
            assert "<img src=" in response.text

    async def test_get_category_wise_expenses(self, async_client_auth: AsyncClient):
        """
        Test retrieving category-wise expenses.
        """
        response = await async_client_auth.get("/analytics/category-wise")
        if response.status_code == 404:
            # Check for both custom and default 404 messages
            assert response.json()["detail"] in ["No expenses found", "Not Found"]
        else:
            assert response.status_code == 200
            assert "<img src=" in response.text

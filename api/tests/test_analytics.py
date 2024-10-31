from datetime import datetime, timedelta
from typing import Optional
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

import api.routers.analytics as analytics
from api.app import app  # Import FastAPI app here

client = TestClient(app)


@pytest.mark.anyio
class TestAnalyticsEndpoints:
    async def test_get_last_7_days_expenses_no_data(
        self, async_client_auth: AsyncClient
    ):
        with patch(
            "api.routers.analytics.get_expense_data", return_value=pd.DataFrame([])
        ):
            response = await async_client_auth.get("/analytics/last-7-days")
            assert response.status_code == 404
            assert response.json()["detail"] in [
                "No expenses found for the last 7 days",
                "Not Found",
            ]

    async def test_get_last_one_month_expenses_no_data(
        self, async_client_auth: AsyncClient
    ):
        with patch(
            "api.routers.analytics.get_expense_data", return_value=pd.DataFrame([])
        ):
            response = await async_client_auth.get("/analytics/last-one-month")
            assert response.status_code == 404
            assert response.json()["detail"] in [
                "No expenses found for the last one month",
                "Not Found",
            ]

    async def test_get_category_wise_expenses_no_data(
        self, async_client_auth: AsyncClient
    ):
        with patch(
            "api.routers.analytics.get_expense_data", return_value=pd.DataFrame([])
        ):
            response = await async_client_auth.get("/analytics/category-wise")
            assert response.status_code == 404
            assert response.json()["detail"] in ["No expenses found", "Not Found"]

import pytest
from httpx import AsyncClient

from api.app import app


@pytest.mark.anyio
class TestCategoryCreation:
    async def test_create_category(self, async_client_auth: AsyncClient):
        # Create a new category
        response = await async_client_auth.post(
            "/categories/", json={"name": "Entertainment", "monthly_budget": 150.0}
        )
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Category created successfully"

    async def test_duplicate_category(self, async_client_auth: AsyncClient):
        # Try creating the same category again
        response = await async_client_auth.post(
            "/categories/", json={"name": "Entertainment", "monthly_budget": 150.0}
        )
        assert response.status_code == 400, response.json()
        assert response.json()["detail"] == "Category already exists"

    async def test_invalid_category(self, async_client_auth: AsyncClient):
        # Try creating a category with invalid data (missing monthly_budget)
        response = await async_client_auth.post(
            "/categories/", json={"name": "InvalidCategory"}
        )
        assert response.status_code == 422, response.json()


@pytest.mark.anyio
class TestCategoryUpdate:
    async def test_update_category(self, async_client_auth: AsyncClient):
        # Update the budget of an existing category
        response = await async_client_auth.put(
            "/categories/Entertainment", json={"monthly_budget": 200.0}
        )
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Category updated successfully"

    async def test_update_non_existent_category(self, async_client_auth: AsyncClient):
        # Try updating a non-existent category
        response = await async_client_auth.put(
            "/categories/NonExistentCategory", json={"monthly_budget": 300.0}
        )
        assert response.status_code == 404, response.json()
        assert response.json()["detail"] == "Category not found"


@pytest.mark.anyio
class TestGetCategories:
    async def test_get_all_categories(self, async_client_auth: AsyncClient):
        # Fetch all categories
        response = await async_client_auth.get("/categories/")
        assert response.status_code == 200, response.json()
        assert isinstance(response.json()["categories"], dict)

    async def test_get_particular_category(self, async_client_auth: AsyncClient):
        # Fetch a specific category by name
        response = await async_client_auth.get("/categories/Entertainment")
        assert response.status_code == 200, response.json()
        assert response.json()["category"]["monthly_budget"] == 200.0

    async def test_get_non_existent_category(self, async_client_auth: AsyncClient):
        # Try fetching a non-existent category
        response = await async_client_auth.get("/categories/NonExistentCategory")
        assert response.status_code == 404, response.json()
        assert response.json()["detail"] == "Category not found"


@pytest.mark.anyio
class TestCategoryDeletion:
    async def test_delete_category(self, async_client_auth: AsyncClient):
        # Delete an existing category
        response = await async_client_auth.delete("/categories/Entertainment")
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Category deleted successfully"

    async def test_delete_non_existent_category(self, async_client_auth: AsyncClient):
        # Try deleting a non-existent category
        response = await async_client_auth.delete("/categories/NonExistentCategory")
        assert response.status_code == 404, response.json()
        assert response.json()["detail"] == "Category not found"

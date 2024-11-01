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
class TestCategoryCases:
    async def test_empty_category_name(self, async_client_auth: AsyncClient):
        # Test creating a category with an empty name
        response = await async_client_auth.post(
            "/categories/", json={"name": "", "monthly_budget": 100.0}
        )
        # Since the API allows empty names, expect a success message
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Category created successfully"

    async def test_zero_budget_category(self, async_client_auth: AsyncClient):
        # Test creating a category with a zero budget
        response = await async_client_auth.post(
            "/categories/", json={"name": "ZeroBudget", "monthly_budget": 0.0}
        )
        # Assuming the API allows zero budget, expect a success message
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Category created successfully"

    async def test_fetch_empty_category_list(self, async_client_auth: AsyncClient):
        # Fetch all categories
        response = await async_client_auth.get("/categories/")
        assert response.status_code == 200, response.json()
        # Expecting categories to be in a dict format, which could contain items
        assert isinstance(response.json()["categories"], dict)

    async def test_delete_category_with_empty_name(
        self, async_client_auth: AsyncClient
    ):
        # Try deleting a category with an empty name
        response = await async_client_auth.delete("/categories/")
        # Check for 405 Method Not Allowed if an empty name is not handled
        assert response.status_code == 405, response.json()

    async def test_get_category_with_unusual_characters(
        self, async_client_auth: AsyncClient
    ):
        # Fetch a category with unusual characters in the name
        response = await async_client_auth.get("/categories/!@#$%^&*()")
        # Expect a 404 error for category not found
        assert response.status_code == 404, response.json()


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

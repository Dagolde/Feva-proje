"""Integration tests for dropdown configuration API endpoints.

Tests for Task 5.1 and 5.2 from admin-qa-dashboards spec.
"""
import pytest
from httpx import AsyncClient

from app.core.security import create_access_token


@pytest.mark.asyncio
class TestDropdownConfigEndpoints:
    """Test suite for dropdown configuration API endpoints."""

    async def test_list_dropdown_config_requires_admin(self, async_client: AsyncClient, enumerator_user):
        """Test that listing dropdown config requires admin role."""
        token = create_access_token({"sub": str(enumerator_user.id), "role": "enumerator"})

        response = await async_client.get(
            "/api/v1/admin/dropdown-config",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_list_dropdown_config_all(self, async_client: AsyncClient, admin_user):
        """Test GET /api/v1/admin/dropdown-config lists all dropdown options."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.get(
            "/api/v1/admin/dropdown-config",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_list_dropdown_config_with_category_filter(
        self, async_client: AsyncClient, admin_user
    ):
        """Test GET /api/v1/admin/dropdown-config with category filter."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        # Test filtering by category
        response = await async_client.get(
            "/api/v1/admin/dropdown-config?category=building_type",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All returned items should be from the building_type category
        for item in data:
            assert item["category"] == "building_type"

    async def test_create_dropdown_config(self, async_client: AsyncClient, admin_user):
        """Test POST /api/v1/admin/dropdown-config creates a new dropdown option."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.post(
            "/api/v1/admin/dropdown-config",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "category": "test_category",
                "value": "test_value",
                "label": "Test Label",
                "sort_order": 10,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "version" in data

    async def test_create_dropdown_config_empty_value_rejected(
        self, async_client: AsyncClient, admin_user
    ):
        """Test POST /api/v1/admin/dropdown-config rejects empty value."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.post(
            "/api/v1/admin/dropdown-config",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "category": "test_category",
                "value": "",
                "label": "Test Label",
                "sort_order": 1,
            },
        )
        assert response.status_code == 400
        assert "value cannot be empty" in response.json()["details"].lower()

    async def test_create_dropdown_config_whitespace_value_rejected(
        self, async_client: AsyncClient, admin_user
    ):
        """Test POST /api/v1/admin/dropdown-config rejects whitespace-only value."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.post(
            "/api/v1/admin/dropdown-config",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "category": "test_category",
                "value": "   ",
                "label": "Test Label",
                "sort_order": 1,
            },
        )
        assert response.status_code == 400
        assert "value cannot be empty" in response.json()["details"].lower()

    async def test_create_dropdown_config_empty_label_rejected(
        self, async_client: AsyncClient, admin_user
    ):
        """Test POST /api/v1/admin/dropdown-config rejects empty label."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.post(
            "/api/v1/admin/dropdown-config",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "category": "test_category",
                "value": "test_value",
                "label": "",
                "sort_order": 1,
            },
        )
        assert response.status_code == 400
        assert "label cannot be empty" in response.json()["details"].lower()

    async def test_create_dropdown_config_whitespace_label_rejected(
        self, async_client: AsyncClient, admin_user
    ):
        """Test POST /api/v1/admin/dropdown-config rejects whitespace-only label."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.post(
            "/api/v1/admin/dropdown-config",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "category": "test_category",
                "value": "test_value",
                "label": "   ",
                "sort_order": 1,
            },
        )
        assert response.status_code == 400
        assert "label cannot be empty" in response.json()["details"].lower()

    async def test_create_dropdown_config_empty_category_rejected(
        self, async_client: AsyncClient, admin_user
    ):
        """Test POST /api/v1/admin/dropdown-config rejects empty category."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.post(
            "/api/v1/admin/dropdown-config",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "category": "",
                "value": "test_value",
                "label": "Test Label",
                "sort_order": 1,
            },
        )
        assert response.status_code == 400
        assert "category cannot be empty" in response.json()["details"].lower()

    async def test_update_dropdown_config_empty_label_rejected(
        self, async_client: AsyncClient, admin_user, db_session
    ):
        """Test PATCH /api/v1/admin/dropdown-config/{id} rejects empty label."""
        from app.models.dropdown_config import DropdownConfig
        
        # Create a dropdown config to update
        dropdown = DropdownConfig(
            category="test_category",
            value="test_value",
            label="Original Label",
            sort_order=1,
            version=1,
            created_by=admin_user.id,
        )
        db_session.add(dropdown)
        await db_session.commit()
        await db_session.refresh(dropdown)
        
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.patch(
            f"/api/v1/admin/dropdown-config/{dropdown.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"label": ""},
        )
        assert response.status_code == 400
        assert "label cannot be empty" in response.json()["details"].lower()

    async def test_update_dropdown_config_whitespace_label_rejected(
        self, async_client: AsyncClient, admin_user, db_session
    ):
        """Test PATCH /api/v1/admin/dropdown-config/{id} rejects whitespace-only label."""
        from app.models.dropdown_config import DropdownConfig
        
        # Create a dropdown config to update
        dropdown = DropdownConfig(
            category="test_category",
            value="test_value",
            label="Original Label",
            sort_order=1,
            version=1,
            created_by=admin_user.id,
        )
        db_session.add(dropdown)
        await db_session.commit()
        await db_session.refresh(dropdown)
        
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.patch(
            f"/api/v1/admin/dropdown-config/{dropdown.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"label": "   "},
        )
        assert response.status_code == 400
        assert "label cannot be empty" in response.json()["details"].lower()

    async def test_update_dropdown_config_not_found(
        self, async_client: AsyncClient, admin_user
    ):
        """Test PATCH /api/v1/admin/dropdown-config/{id} returns 404 for non-existent id."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.patch(
            "/api/v1/admin/dropdown-config/99999",
            headers={"Authorization": f"Bearer {token}"},
            json={"label": "New Label"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["details"].lower()

    async def test_delete_dropdown_config_not_found(
        self, async_client: AsyncClient, admin_user
    ):
        """Test DELETE /api/v1/admin/dropdown-config/{id} returns 404 for non-existent id."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.delete(
            "/api/v1/admin/dropdown-config/99999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["details"].lower()

    async def test_dropdown_config_post_requires_admin_role(
        self, async_client: AsyncClient, enumerator_user
    ):
        """Test that POST dropdown config endpoint requires admin role."""
        token = create_access_token({"sub": str(enumerator_user.id), "role": "enumerator"})

        response = await async_client.post(
            "/api/v1/admin/dropdown-config",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "category": "test",
                "value": "test",
                "label": "Test",
                "sort_order": 1,
            },
        )
        assert response.status_code == 403

    async def test_dropdown_config_patch_requires_admin_role(
        self, async_client: AsyncClient, enumerator_user
    ):
        """Test that PATCH dropdown config endpoint requires admin role."""
        token = create_access_token({"sub": str(enumerator_user.id), "role": "enumerator"})

        response = await async_client.patch(
            "/api/v1/admin/dropdown-config/1",
            headers={"Authorization": f"Bearer {token}"},
            json={"label": "New Label"},
        )
        assert response.status_code == 403

    async def test_dropdown_config_delete_requires_admin_role(
        self, async_client: AsyncClient, enumerator_user
    ):
        """Test that DELETE dropdown config endpoint requires admin role."""
        token = create_access_token({"sub": str(enumerator_user.id), "role": "enumerator"})

        response = await async_client.delete(
            "/api/v1/admin/dropdown-config/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403



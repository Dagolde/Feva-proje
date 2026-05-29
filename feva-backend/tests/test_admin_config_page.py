"""Tests for admin system configuration page.

Requirements: 6.1, 6.2, 6.3, 6.4
"""
import pytest
from httpx import AsyncClient

from app.core.security import create_access_token


class TestAdminConfigPage:
    """Test admin system configuration page rendering and access control."""

    async def test_config_page_requires_authentication(self, async_client: AsyncClient):
        """Test that /admin/config requires authentication."""
        response = await async_client.get("/admin/config", follow_redirects=False)
        
        # Should redirect to login or return 401
        assert response.status_code in (302, 401)

    async def test_config_page_requires_admin_role(
        self, async_client: AsyncClient, qa_officer_user
    ):
        """Test that /admin/config requires admin role."""
        token = create_access_token({"sub": str(qa_officer_user.id), "role": "qa_officer"})
        
        response = await async_client.get(
            "/admin/config",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        # Should return 403 Forbidden for non-admin
        assert response.status_code == 403

    async def test_config_page_accessible_to_admin(
        self, async_client: AsyncClient, admin_user
    ):
        """Test that /admin/config is accessible to admin users."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.get(
            "/admin/config",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    async def test_config_page_contains_dropdown_section(
        self, async_client: AsyncClient, admin_user
    ):
        """Test that config page contains dropdown configuration section."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.get(
            "/admin/config",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Check for dropdown configuration elements
        assert "Dropdown Configuration" in content
        assert "dropdownTable" in content
        assert "categoryFilter" in content
        assert "Add Dropdown Option" in content

    async def test_config_page_contains_lga_section(
        self, async_client: AsyncClient, admin_user
    ):
        """Test that config page contains LGA assignment section."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.get(
            "/admin/config",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Check for LGA assignment elements
        assert "LGA Assignments" in content
        assert "lgaTable" in content
        assert "roleFilter" in content
        assert "Edit Assignment" in content or "Edit LGA Assignment" in content

    async def test_config_page_has_tab_navigation(
        self, async_client: AsyncClient, admin_user
    ):
        """Test that config page has tab navigation between sections."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.get(
            "/admin/config",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Check for tab navigation
        assert "tab-button" in content
        assert "switchTab" in content
        assert "dropdownTab" in content
        assert "lgaTab" in content

    async def test_config_page_includes_common_js(
        self, async_client: AsyncClient, admin_user
    ):
        """Test that config page includes common.js utilities."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.get(
            "/admin/config",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Check for common.js inclusion
        assert "/static/js/common.js" in content

    async def test_config_page_has_create_dropdown_modal(
        self, async_client: AsyncClient, admin_user
    ):
        """Test that config page has create dropdown modal."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.get(
            "/admin/config",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Check for create dropdown modal
        assert "createDropdownModal" in content
        assert "createDropdownForm" in content
        assert "createCategory" in content
        assert "createValue" in content
        assert "createLabel" in content
        assert "createSortOrder" in content

    async def test_config_page_has_edit_dropdown_modal(
        self, async_client: AsyncClient, admin_user
    ):
        """Test that config page has edit dropdown modal."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.get(
            "/admin/config",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Check for edit dropdown modal
        assert "editDropdownModal" in content
        assert "editDropdownForm" in content
        assert "editLabel" in content
        assert "editSortOrder" in content

    async def test_config_page_has_delete_dropdown_modal(
        self, async_client: AsyncClient, admin_user
    ):
        """Test that config page has delete dropdown confirmation modal."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.get(
            "/admin/config",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Check for delete dropdown modal
        assert "deleteDropdownModal" in content
        assert "deleteDropdownId" in content

    async def test_config_page_has_edit_lga_modal(
        self, async_client: AsyncClient, admin_user
    ):
        """Test that config page has edit LGA assignment modal."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.get(
            "/admin/config",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Check for edit LGA modal
        assert "editLgaModal" in content
        assert "editLgaForm" in content
        assert "editLgaAssignment" in content

    async def test_config_page_uses_admin_layout(
        self, async_client: AsyncClient, admin_user
    ):
        """Test that config page extends admin layout."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.get(
            "/admin/config",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Check for admin layout elements (from layout.html)
        # The page should have the standard admin navigation and structure
        assert "System Configuration" in content

    async def test_config_page_has_category_options(
        self, async_client: AsyncClient, admin_user
    ):
        """Test that config page has predefined category options."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.get(
            "/admin/config",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Check for category options
        assert "building_type" in content
        assert "street_type" in content
        assert "building_condition" in content
        assert "street_condition" in content
        assert "surface_type" in content

    async def test_config_page_has_api_integration(
        self, async_client: AsyncClient, admin_user
    ):
        """Test that config page integrates with API endpoints."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.get(
            "/admin/config",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Check for API endpoint references
        assert "/api/v1/admin/dropdown-config" in content
        assert "/api/v1/admin/users" in content
        assert "/api/v1/admin/roles" in content

    async def test_config_page_has_responsive_design(
        self, async_client: AsyncClient, admin_user
    ):
        """Test that config page has responsive CSS."""
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        response = await async_client.get(
            "/admin/config",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Check for responsive design elements
        assert "@media" in content
        assert "max-width: 768px" in content

"""Tests for admin role management page.

Requirements: 5.1, 5.2, 5.3
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_roles_page_requires_admin_role(async_client: AsyncClient, qa_token: str):
    """Test that role management page requires admin role."""
    response = await async_client.get(
        "/admin/roles",
        cookies={"access_token": qa_token}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_roles_page_accessible_to_admin(async_client: AsyncClient, admin_token: str):
    """Test that role management page is accessible to admin users."""
    response = await async_client.get(
        "/admin/roles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "Role Management" in response.text


@pytest.mark.asyncio
async def test_admin_roles_page_displays_role_list(async_client: AsyncClient, admin_token: str):
    """Test that role management page displays role list."""
    response = await async_client.get(
        "/admin/roles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "rolesContainer" in response.text
    assert "System Roles" in response.text


@pytest.mark.asyncio
async def test_admin_roles_page_has_statistics(async_client: AsyncClient, admin_token: str):
    """Test that role management page displays role statistics."""
    response = await async_client.get(
        "/admin/roles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "totalRoles" in response.text
    assert "adminCount" in response.text
    assert "qaCount" in response.text
    assert "fieldStaffCount" in response.text


@pytest.mark.asyncio
async def test_admin_roles_page_displays_permissions(async_client: AsyncClient, admin_token: str):
    """Test that role management page displays role permissions."""
    response = await async_client.get(
        "/admin/roles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "permissions-grid" in response.text
    assert "permission-item" in response.text


@pytest.mark.asyncio
async def test_admin_roles_page_has_role_descriptions(async_client: AsyncClient, admin_token: str):
    """Test that role management page includes role descriptions."""
    response = await async_client.get(
        "/admin/roles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "role-description" in response.text


@pytest.mark.asyncio
async def test_admin_roles_page_loads_common_js(async_client: AsyncClient, admin_token: str):
    """Test that role management page loads common.js utilities."""
    response = await async_client.get(
        "/admin/roles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "/static/js/common.js" in response.text


@pytest.mark.asyncio
async def test_admin_roles_page_redirects_unauthenticated(async_client: AsyncClient):
    """Test that unauthenticated users are redirected to login."""
    response = await async_client.get("/admin/roles", follow_redirects=False)
    assert response.status_code in [302, 307]
    assert "login" in response.headers.get("location", "").lower()


@pytest.mark.asyncio
async def test_admin_roles_page_has_responsive_design(async_client: AsyncClient, admin_token: str):
    """Test that role management page includes responsive design elements."""
    response = await async_client.get(
        "/admin/roles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    # Check for responsive CSS media queries
    assert "@media" in response.text


@pytest.mark.asyncio
async def test_admin_roles_page_uses_api_endpoints(async_client: AsyncClient, admin_token: str):
    """Test that role management page uses the correct API endpoints."""
    response = await async_client.get(
        "/admin/roles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    # Check that JavaScript references the correct API endpoints
    assert "/api/v1/admin/roles" in response.text
    assert "/api/v1/admin/monitoring/statistics" in response.text


@pytest.mark.asyncio
async def test_admin_roles_page_has_info_box(async_client: AsyncClient, admin_token: str):
    """Test that role management page has informational content."""
    response = await async_client.get(
        "/admin/roles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "About Role Management" in response.text
    assert "User Management" in response.text


@pytest.mark.asyncio
async def test_admin_roles_page_displays_user_counts(async_client: AsyncClient, admin_token: str):
    """Test that role management page displays user count per role."""
    response = await async_client.get(
        "/admin/roles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "user-count" in response.text


@pytest.mark.asyncio
async def test_admin_roles_page_has_role_badges(async_client: AsyncClient, admin_token: str):
    """Test that role management page displays role badges."""
    response = await async_client.get(
        "/admin/roles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "role-badge" in response.text

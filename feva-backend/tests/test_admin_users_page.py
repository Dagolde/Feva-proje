"""Tests for admin user management page.

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_users_page_requires_admin_role(async_client: AsyncClient, qa_token: str):
    """Test that user management page requires admin role."""
    response = await async_client.get(
        "/admin/users",
        cookies={"access_token": qa_token}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_users_page_accessible_to_admin(async_client: AsyncClient, admin_token: str):
    """Test that user management page is accessible to admin users."""
    response = await async_client.get(
        "/admin/users",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "User Management" in response.text


@pytest.mark.asyncio
async def test_admin_users_page_contains_user_table(async_client: AsyncClient, admin_token: str):
    """Test that user management page contains user table."""
    response = await async_client.get(
        "/admin/users",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "usersTable" in response.text
    assert "<thead>" in response.text
    assert "Username" in response.text
    assert "Email" in response.text
    assert "Role" in response.text


@pytest.mark.asyncio
async def test_admin_users_page_has_create_user_button(async_client: AsyncClient, admin_token: str):
    """Test that user management page has create user button."""
    response = await async_client.get(
        "/admin/users",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "Create User" in response.text
    assert "openCreateUserModal" in response.text


@pytest.mark.asyncio
async def test_admin_users_page_has_create_user_modal(async_client: AsyncClient, admin_token: str):
    """Test that user management page has create user modal."""
    response = await async_client.get(
        "/admin/users",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "createUserModal" in response.text
    assert "createUsername" in response.text
    assert "createEmail" in response.text
    assert "createPassword" in response.text
    assert "createRole" in response.text
    assert "createLgaAssignment" in response.text


@pytest.mark.asyncio
async def test_admin_users_page_has_edit_user_modal(async_client: AsyncClient, admin_token: str):
    """Test that user management page has edit user modal."""
    response = await async_client.get(
        "/admin/users",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "editUserModal" in response.text
    assert "editRole" in response.text
    assert "editLgaAssignment" in response.text


@pytest.mark.asyncio
async def test_admin_users_page_has_reset_password_modal(async_client: AsyncClient, admin_token: str):
    """Test that user management page has reset password modal."""
    response = await async_client.get(
        "/admin/users",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "resetPasswordModal" in response.text
    assert "newPassword" in response.text


@pytest.mark.asyncio
async def test_admin_users_page_has_deactivate_user_modal(async_client: AsyncClient, admin_token: str):
    """Test that user management page has deactivate user modal."""
    response = await async_client.get(
        "/admin/users",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "deactivateUserModal" in response.text


@pytest.mark.asyncio
async def test_admin_users_page_has_search_functionality(async_client: AsyncClient, admin_token: str):
    """Test that user management page has search functionality."""
    response = await async_client.get(
        "/admin/users",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "searchInput" in response.text
    assert "Search by username" in response.text


@pytest.mark.asyncio
async def test_admin_users_page_has_statistics(async_client: AsyncClient, admin_token: str):
    """Test that user management page displays user statistics."""
    response = await async_client.get(
        "/admin/users",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "totalUsers" in response.text
    assert "activeUsers" in response.text
    assert "lockedUsers" in response.text


@pytest.mark.asyncio
async def test_admin_users_page_loads_common_js(async_client: AsyncClient, admin_token: str):
    """Test that user management page loads common.js utilities."""
    response = await async_client.get(
        "/admin/users",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "/static/js/common.js" in response.text


@pytest.mark.asyncio
async def test_admin_users_page_redirects_unauthenticated(async_client: AsyncClient):
    """Test that unauthenticated users are redirected to login."""
    response = await async_client.get("/admin/users", follow_redirects=False)
    assert response.status_code in [302, 307]
    assert "login" in response.headers.get("location", "").lower()


@pytest.mark.asyncio
async def test_admin_users_page_has_responsive_design(async_client: AsyncClient, admin_token: str):
    """Test that user management page includes responsive design elements."""
    response = await async_client.get(
        "/admin/users",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    # Check for responsive CSS media queries
    assert "@media" in response.text or "mobile" in response.text.lower()


@pytest.mark.asyncio
async def test_admin_users_page_uses_api_endpoints(async_client: AsyncClient, admin_token: str):
    """Test that user management page uses the correct API endpoints."""
    response = await async_client.get(
        "/admin/users",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    # Check that JavaScript references the correct API endpoints
    assert "/api/v1/admin/users" in response.text
    assert "/api/v1/admin/roles" in response.text

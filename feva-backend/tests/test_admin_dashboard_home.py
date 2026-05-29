"""Tests for admin dashboard home page.

Tests the admin dashboard home page route at /admin/
Requirements: 1.1, 1.3
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_dashboard_requires_admin_role(async_client: AsyncClient, qa_token: str):
    """Test that admin dashboard requires admin role."""
    response = await async_client.get(
        "/admin/",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_dashboard_accessible_to_admin(async_client: AsyncClient, admin_token: str):
    """Test that admin dashboard is accessible to admin users."""
    response = await async_client.get(
        "/admin/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_admin_dashboard_contains_expected_content(async_client: AsyncClient, admin_token: str):
    """Test that admin dashboard contains expected content."""
    response = await async_client.get(
        "/admin/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    
    # Check for page title
    assert "Admin Dashboard" in content
    
    # Check for system overview section
    assert "System Overview" in content
    
    # Check for system health metrics
    assert "Database Status" in content
    assert "Disk Space" in content
    assert "System Uptime" in content
    
    # Check for record statistics
    assert "Record Statistics" in content
    assert "Pending Records" in content
    assert "Approved Records" in content
    assert "Rejected Records" in content
    
    # Check for quick actions
    assert "Quick Actions" in content
    assert "Manage Users" in content
    assert "View Monitoring" in content
    assert "Export Data" in content
    
    # Check for recent activity section
    assert "Recent Activity" in content


@pytest.mark.asyncio
async def test_admin_dashboard_redirects_unauthenticated(async_client: AsyncClient):
    """Test that unauthenticated users are redirected to login."""
    response = await async_client.get("/admin/", follow_redirects=False)
    
    # Should redirect to login or return 401
    assert response.status_code in (302, 401)


@pytest.mark.asyncio
async def test_admin_dashboard_has_navigation(async_client: AsyncClient, admin_token: str):
    """Test that admin dashboard has navigation sidebar."""
    response = await async_client.get(
        "/admin/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    
    # Check for navigation links
    assert "/admin/users" in content
    assert "/admin/roles" in content
    assert "/admin/config" in content
    assert "/admin/shapefiles" in content
    assert "/admin/export" in content
    assert "/admin/monitoring" in content
    assert "/admin/audit" in content


@pytest.mark.asyncio
async def test_admin_dashboard_has_logout_button(async_client: AsyncClient, admin_token: str):
    """Test that admin dashboard has logout functionality."""
    response = await async_client.get(
        "/admin/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    
    # Check for logout button
    assert "Logout" in content
    assert "handleLogout" in content


@pytest.mark.asyncio
async def test_admin_dashboard_loads_monitoring_data(async_client: AsyncClient, admin_token: str):
    """Test that admin dashboard includes JavaScript to load monitoring data."""
    response = await async_client.get(
        "/admin/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    
    # Check for JavaScript functions to load data
    assert "loadSystemHealth" in content
    assert "loadStatistics" in content
    assert "loadRecentActivity" in content
    assert "refreshDashboard" in content
    
    # Check for API endpoint calls
    assert "/api/v1/admin/monitoring/health" in content
    assert "/api/v1/admin/monitoring/statistics" in content
    assert "/api/v1/admin/audit-log" in content


@pytest.mark.asyncio
async def test_admin_dashboard_has_auto_refresh(async_client: AsyncClient, admin_token: str):
    """Test that admin dashboard has auto-refresh functionality."""
    response = await async_client.get(
        "/admin/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    
    # Check for auto-refresh functionality
    assert "startAutoRefresh" in content
    assert "stopAutoRefresh" in content
    assert "updateLastRefreshTime" in content


@pytest.mark.asyncio
async def test_admin_dashboard_responsive_design(async_client: AsyncClient, admin_token: str):
    """Test that admin dashboard includes responsive design elements."""
    response = await async_client.get(
        "/admin/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    
    # Check for mobile menu toggle
    assert "mobile-menu-toggle" in content
    assert "toggleMobileMenu" in content
    
    # Check for responsive CSS
    assert "@media" in content or "mobile" in content.lower()

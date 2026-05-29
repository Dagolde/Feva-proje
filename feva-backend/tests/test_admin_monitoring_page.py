"""Tests for admin monitoring page.

Tests the monitoring page route and ensures it:
- Requires admin role
- Returns HTML response
- Includes necessary UI elements
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_monitoring_page_requires_admin(async_client: AsyncClient, qa_token: str):
    """Test that monitoring page requires admin role."""
    response = await async_client.get(
        "/admin/monitoring",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_monitoring_page_requires_authentication(async_client: AsyncClient):
    """Test that monitoring page requires authentication."""
    response = await async_client.get("/admin/monitoring", follow_redirects=False)
    # Should redirect to login or return 401
    assert response.status_code in (302, 401)


@pytest.mark.asyncio
async def test_monitoring_page_renders_for_admin(async_client: AsyncClient, admin_token: str):
    """Test that monitoring page renders successfully for admin users."""
    response = await async_client.get(
        "/admin/monitoring",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    
    # Check for key page elements
    content = response.text
    assert "System Monitoring" in content
    assert "System Health" in content
    assert "Record Statistics" in content
    assert "Active Users by Role" in content
    assert "Recent Sync Sessions" in content


@pytest.mark.asyncio
async def test_monitoring_page_includes_health_metrics(async_client: AsyncClient, admin_token: str):
    """Test that monitoring page includes system health metric elements."""
    response = await async_client.get(
        "/admin/monitoring",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    # Check for health metric elements
    assert "databaseStatus" in content
    assert "diskSpace" in content
    assert "uptime" in content
    assert "lastCheck" in content


@pytest.mark.asyncio
async def test_monitoring_page_includes_record_statistics(async_client: AsyncClient, admin_token: str):
    """Test that monitoring page includes record statistics elements."""
    response = await async_client.get(
        "/admin/monitoring",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    # Check for record statistics elements
    assert "pendingRecords" in content
    assert "approvedRecords" in content
    assert "rejectedRecords" in content
    assert "flaggedRecords" in content


@pytest.mark.asyncio
async def test_monitoring_page_includes_user_statistics(async_client: AsyncClient, admin_token: str):
    """Test that monitoring page includes user statistics elements."""
    response = await async_client.get(
        "/admin/monitoring",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    # Check for user statistics elements
    assert "adminUsers" in content
    assert "qaUsers" in content
    assert "supervisorUsers" in content
    assert "enumeratorUsers" in content


@pytest.mark.asyncio
async def test_monitoring_page_includes_sync_sessions_table(async_client: AsyncClient, admin_token: str):
    """Test that monitoring page includes sync sessions table."""
    response = await async_client.get(
        "/admin/monitoring",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    # Check for sync sessions table elements
    assert "syncSessionsTable" in content
    assert "Device ID" in content
    assert "Status" in content
    assert "Records Synced" in content


@pytest.mark.asyncio
async def test_monitoring_page_includes_auto_refresh(async_client: AsyncClient, admin_token: str):
    """Test that monitoring page includes auto-refresh functionality."""
    response = await async_client.get(
        "/admin/monitoring",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    # Check for auto-refresh elements
    assert "lastRefreshTime" in content
    assert "refreshAllData" in content
    assert "startAutoRefresh" in content


@pytest.mark.asyncio
async def test_monitoring_page_includes_status_filter(async_client: AsyncClient, admin_token: str):
    """Test that monitoring page includes status filter for sync sessions."""
    response = await async_client.get(
        "/admin/monitoring",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    # Check for status filter
    assert "statusFilter" in content
    assert "All Statuses" in content
    assert "Completed" in content
    assert "Failed" in content


@pytest.mark.asyncio
async def test_monitoring_page_includes_pagination(async_client: AsyncClient, admin_token: str):
    """Test that monitoring page includes pagination controls."""
    response = await async_client.get(
        "/admin/monitoring",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    # Check for pagination elements
    assert "paginationControls" in content
    assert "prevPageBtn" in content
    assert "nextPageBtn" in content
    assert "paginationInfo" in content


@pytest.mark.asyncio
async def test_monitoring_page_includes_session_detail_modal(async_client: AsyncClient, admin_token: str):
    """Test that monitoring page includes session detail modal."""
    response = await async_client.get(
        "/admin/monitoring",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    # Check for modal elements
    assert "sessionDetailModal" in content
    assert "Sync Session Details" in content
    assert "closeSessionDetailModal" in content

"""Tests for admin monitoring endpoints.

Tests the three monitoring endpoints:
- GET /api/v1/admin/monitoring/health
- GET /api/v1/admin/monitoring/sync-sessions
- GET /api/v1/admin/monitoring/statistics
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint_requires_admin(async_client: AsyncClient, qa_token: str):
    """Test that health endpoint requires admin role."""
    response = await async_client.get(
        "/api/v1/admin/monitoring/health",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_health_endpoint_returns_metrics(async_client: AsyncClient, admin_token: str):
    """Test that health endpoint returns system metrics."""
    response = await async_client.get(
        "/api/v1/admin/monitoring/health",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "database" in data
    assert "disk_space_gb" in data
    assert "uptime_seconds" in data
    assert "timestamp" in data
    
    # Database should be connected
    assert data["database"] == "connected"
    
    # Disk space should be a positive number
    assert isinstance(data["disk_space_gb"], (int, float))
    assert data["disk_space_gb"] >= 0
    
    # Uptime should be a non-negative integer
    assert isinstance(data["uptime_seconds"], int)
    assert data["uptime_seconds"] >= 0



@pytest.mark.asyncio
async def test_sync_sessions_endpoint_requires_admin(async_client: AsyncClient, qa_token: str):
    """Test that sync sessions endpoint requires admin role."""
    response = await async_client.get(
        "/api/v1/admin/monitoring/sync-sessions",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_sync_sessions_endpoint_returns_sessions(async_client: AsyncClient, admin_token: str):
    """Test that sync sessions endpoint returns session data."""
    response = await async_client.get(
        "/api/v1/admin/monitoring/sync-sessions",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "items" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_sync_sessions_pagination(async_client: AsyncClient, admin_token: str):
    """Test that sync sessions endpoint supports pagination."""
    response = await async_client.get(
        "/api/v1/admin/monitoring/sync-sessions?page=1&page_size=2",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_sync_sessions_status_filter(async_client: AsyncClient, admin_token: str):
    """Test that sync sessions endpoint supports status filtering."""
    response = await async_client.get(
        "/api/v1/admin/monitoring/sync-sessions?status=completed",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    data = response.json()
    # All returned items should have completed status
    for item in data["items"]:
        assert item["status"] == "completed"



@pytest.mark.asyncio
async def test_statistics_endpoint_requires_admin(async_client: AsyncClient, qa_token: str):
    """Test that statistics endpoint requires admin role."""
    response = await async_client.get(
        "/api/v1/admin/monitoring/statistics",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_statistics_endpoint_returns_counts(async_client: AsyncClient, admin_token: str):
    """Test that statistics endpoint returns record and user counts."""
    response = await async_client.get(
        "/api/v1/admin/monitoring/statistics",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "records_by_status" in data
    assert "users_by_role" in data
    
    # Check records_by_status structure
    records_by_status = data["records_by_status"]
    assert isinstance(records_by_status, dict)
    
    # Check users_by_role structure
    users_by_role = data["users_by_role"]
    assert isinstance(users_by_role, dict)
    
    # Should have at least admin and qa_officer roles
    assert "admin" in users_by_role
    assert "qa_officer" in users_by_role
    assert users_by_role["admin"] >= 1
    assert users_by_role["qa_officer"] >= 1

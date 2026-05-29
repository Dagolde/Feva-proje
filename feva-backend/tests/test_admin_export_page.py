"""Tests for admin export page route.

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_export_page_requires_admin_role(
    client: AsyncClient,
    admin_token: str,
):
    """Test that export page requires admin role."""
    response = await client.get(
        "/admin/export",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert b"Data Export" in response.content
    assert b"Export enumeration data and audit logs" in response.content


@pytest.mark.asyncio
async def test_admin_export_page_rejects_non_admin(
    client: AsyncClient,
    enumerator_token: str,
):
    """Test that export page rejects non-admin users."""
    response = await client.get(
        "/admin/export",
        headers={"Authorization": f"Bearer {enumerator_token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_export_page_requires_authentication(
    client: AsyncClient,
):
    """Test that export page requires authentication."""
    response = await client.get("/admin/export", follow_redirects=False)
    
    # Should redirect to login (302) or return 401
    assert response.status_code in [302, 401]


@pytest.mark.asyncio
async def test_admin_export_page_contains_export_form(
    client: AsyncClient,
    admin_token: str,
):
    """Test that export page contains the export form."""
    response = await client.get(
        "/admin/export",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    content = response.content.decode()
    
    # Check for form elements
    assert 'id="exportForm"' in content
    assert 'id="exportType"' in content
    assert 'id="exportFormat"' in content
    assert 'value="building"' in content
    assert 'value="street"' in content
    assert 'value="audit_log"' in content
    assert 'value="csv"' in content
    assert 'value="geojson"' in content


@pytest.mark.asyncio
async def test_admin_export_page_contains_filter_section(
    client: AsyncClient,
    admin_token: str,
):
    """Test that export page contains filter options."""
    response = await client.get(
        "/admin/export",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    content = response.content.decode()
    
    # Check for filter fields
    assert 'id="filterLga"' in content
    assert 'id="filterWard"' in content
    assert 'id="filterStatus"' in content
    assert 'id="filterDateFrom"' in content
    assert 'id="filterDateTo"' in content


@pytest.mark.asyncio
async def test_admin_export_page_contains_tasks_table(
    client: AsyncClient,
    admin_token: str,
):
    """Test that export page contains export tasks table."""
    response = await client.get(
        "/admin/export",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    content = response.content.decode()
    
    # Check for tasks table
    assert 'id="exportTasksTable"' in content
    assert 'id="exportTasksTableBody"' in content
    assert '<th>Type</th>' in content
    assert '<th>Format</th>' in content
    assert '<th>Filters</th>' in content
    assert '<th>Status</th>' in content
    assert '<th>Created</th>' in content
    assert '<th>Completed</th>' in content
    assert '<th>Actions</th>' in content


@pytest.mark.asyncio
async def test_admin_export_page_contains_statistics(
    client: AsyncClient,
    admin_token: str,
):
    """Test that export page contains statistics cards."""
    response = await client.get(
        "/admin/export",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    content = response.content.decode()
    
    # Check for statistics
    assert 'id="totalRecords"' in content
    assert 'id="pendingExports"' in content
    assert 'id="completedToday"' in content


@pytest.mark.asyncio
async def test_admin_export_page_uses_admin_layout(
    client: AsyncClient,
    admin_token: str,
):
    """Test that export page uses admin layout template."""
    response = await client.get(
        "/admin/export",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    content = response.content.decode()
    
    # Check for admin layout elements
    assert 'Admin Dashboard' in content
    assert 'sidebar' in content.lower()
    assert '/admin/users' in content
    assert '/admin/config' in content
    assert '/admin/shapefiles' in content


@pytest.mark.asyncio
async def test_list_export_tasks_endpoint(
    client: AsyncClient,
    admin_token: str,
):
    """Test the list export tasks API endpoint."""
    response = await client.get(
        "/api/v1/admin/export/tasks",
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
async def test_list_export_tasks_pagination(
    client: AsyncClient,
    admin_token: str,
):
    """Test that list export tasks supports pagination."""
    response = await client.get(
        "/api/v1/admin/export/tasks?page=1&page_size=10",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["items"]) <= 10


@pytest.mark.asyncio
async def test_list_export_tasks_requires_admin(
    client: AsyncClient,
    enumerator_token: str,
):
    """Test that list export tasks requires admin role."""
    response = await client.get(
        "/api/v1/admin/export/tasks",
        headers={"Authorization": f"Bearer {enumerator_token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_export_tasks_requires_authentication(
    client: AsyncClient,
):
    """Test that list export tasks requires authentication."""
    response = await client.get("/api/v1/admin/export/tasks")
    
    assert response.status_code == 401

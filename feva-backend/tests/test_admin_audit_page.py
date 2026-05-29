"""Tests for admin audit log viewer page.

Tests Task 16.8: Create audit log viewer page
- Create `app/templates/admin/audit.html` with paginated audit log
- Include filters for user, operation, and date
- Create route handler at `/admin/audit` requiring admin role
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_audit_page_requires_admin_role(
    client: AsyncClient,
    enumerator_token: str,
):
    """Test that audit page requires admin role."""
    response = await client.get(
        "/admin/audit",
        headers={"Authorization": f"Bearer {enumerator_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_audit_page_requires_authentication(client: AsyncClient):
    """Test that audit page requires authentication."""
    response = await client.get("/admin/audit")
    # Should redirect to login or return 401
    assert response.status_code in [401, 307, 302]


@pytest.mark.asyncio
async def test_audit_page_renders_for_admin(
    client: AsyncClient,
    admin_token: str,
):
    """Test that audit page renders successfully for admin users."""
    response = await client.get(
        "/admin/audit",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    
    content = response.text
    
    # Check page title and header
    assert "Audit Log" in content
    assert "View system audit trail" in content
    
    # Check filter controls are present
    assert 'id="userFilter"' in content
    assert 'id="operationFilter"' in content
    assert 'id="entityTypeFilter"' in content
    assert 'id="dateFromFilter"' in content
    assert 'id="dateToFilter"' in content
    
    # Check operation filter options
    assert "Create User" in content
    assert "Update User" in content
    assert "Reset Password" in content
    assert "Deactivate User" in content
    assert "Create Dropdown" in content
    assert "Update Dropdown" in content
    assert "Delete Dropdown" in content
    assert "Upload Shapefile" in content
    assert "Activate Shapefile" in content
    assert "Approve Record" in content
    assert "Reject Record" in content
    assert "Create Export" in content
    
    # Check entity type filter options
    assert "User" in content
    assert "Dropdown Config" in content
    assert "Shapefile Version" in content
    assert "Building" in content
    assert "Street" in content
    assert "Export Task" in content
    
    # Check table structure
    assert 'id="auditLogTable"' in content
    assert "<th>Timestamp</th>" in content or "<th style=" in content
    assert "User" in content
    assert "Operation" in content
    assert "Entity Type" in content
    assert "Entity ID" in content
    assert "Details" in content
    
    # Check pagination controls
    assert 'id="paginationControls"' in content
    assert 'id="pageSizeSelect"' in content
    assert 'id="prevPageBtn"' in content
    assert 'id="nextPageBtn"' in content
    
    # Check page size options
    assert '<option value="10">10</option>' in content
    assert '<option value="25">25</option>' in content
    assert '<option value="50"' in content
    assert '<option value="100">100</option>' in content
    
    # Check modal for detail view
    assert 'id="auditDetailModal"' in content
    
    # Check JavaScript functions are present
    assert "loadAuditLog" in content
    assert "applyFilters" in content
    assert "clearFilters" in content
    assert "changePage" in content
    assert "changePageSize" in content
    assert "viewAuditDetail" in content
    
    # Check API endpoint references
    assert "/api/v1/admin/audit-log" in content
    assert "/api/v1/admin/users" in content


@pytest.mark.asyncio
async def test_audit_page_includes_common_js(
    client: AsyncClient,
    admin_token: str,
):
    """Test that audit page includes common.js for API utilities."""
    response = await client.get(
        "/admin/audit",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    assert "/static/js/common.js" in content


@pytest.mark.asyncio
async def test_audit_page_extends_admin_layout(
    client: AsyncClient,
    admin_token: str,
):
    """Test that audit page extends admin layout template."""
    response = await client.get(
        "/admin/audit",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    
    # Check for admin layout elements
    assert "Admin Dashboard" in content
    assert "sidebar" in content.lower()
    assert "Logout" in content or "logout" in content.lower()


@pytest.mark.asyncio
async def test_audit_page_has_responsive_design(
    client: AsyncClient,
    admin_token: str,
):
    """Test that audit page includes responsive CSS."""
    response = await client.get(
        "/admin/audit",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    
    # Check for responsive CSS media queries
    assert "@media" in content
    assert "max-width" in content


@pytest.mark.asyncio
async def test_audit_page_has_filter_functionality(
    client: AsyncClient,
    admin_token: str,
):
    """Test that audit page has filter functionality."""
    response = await client.get(
        "/admin/audit",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    
    # Check filter functions
    assert "applyFilters()" in content
    assert "clearFilters()" in content
    
    # Check filter state management
    assert "filters" in content
    assert "user_id" in content
    assert "operation" in content
    assert "entity_type" in content
    assert "date_from" in content
    assert "date_to" in content


@pytest.mark.asyncio
async def test_audit_page_has_pagination_functionality(
    client: AsyncClient,
    admin_token: str,
):
    """Test that audit page has pagination functionality."""
    response = await client.get(
        "/admin/audit",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    
    # Check pagination variables
    assert "currentPage" in content
    assert "pageSize" in content
    assert "totalEntries" in content
    
    # Check pagination functions
    assert "changePage" in content
    assert "changePageSize" in content
    assert "updatePaginationControls" in content


@pytest.mark.asyncio
async def test_audit_page_has_detail_modal(
    client: AsyncClient,
    admin_token: str,
):
    """Test that audit page has detail modal for viewing full entry details."""
    response = await client.get(
        "/admin/audit",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    
    # Check modal structure
    assert 'id="auditDetailModal"' in content
    assert 'class="modal"' in content
    assert 'class="modal-content"' in content
    assert 'class="modal-header"' in content
    assert 'class="modal-body"' in content
    assert 'id="auditDetailContent"' in content
    
    # Check modal functions
    assert "viewAuditDetail" in content
    assert "closeAuditDetailModal" in content


@pytest.mark.asyncio
async def test_audit_page_has_operation_badges(
    client: AsyncClient,
    admin_token: str,
):
    """Test that audit page has styled operation badges."""
    response = await client.get(
        "/admin/audit",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    
    # Check operation badge CSS classes
    assert "operation-badge" in content
    assert "operation-create" in content
    assert "operation-update" in content
    assert "operation-delete" in content
    assert "operation-approve" in content
    assert "operation-reject" in content
    assert "operation-upload" in content
    assert "operation-activate" in content


@pytest.mark.asyncio
async def test_audit_page_formats_timestamps(
    client: AsyncClient,
    admin_token: str,
):
    """Test that audit page includes timestamp formatting."""
    response = await client.get(
        "/admin/audit",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    
    # Check for formatDateTime function (from common.js)
    assert "formatDateTime" in content


@pytest.mark.asyncio
async def test_audit_page_escapes_html(
    client: AsyncClient,
    admin_token: str,
):
    """Test that audit page includes HTML escaping for security."""
    response = await client.get(
        "/admin/audit",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    content = response.text
    
    # Check for escapeHtml function
    assert "escapeHtml" in content
    assert "textContent" in content or "innerHTML" in content

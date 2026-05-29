"""Tests for QA records page.

Task 17.2: Create record list page
Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.8
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_qa_records_page_requires_authentication(client: AsyncClient):
    """Test that unauthenticated users are redirected to login."""
    response = await client.get("/qa/records", follow_redirects=False)
    assert response.status_code in (302, 401)


@pytest.mark.asyncio
async def test_qa_records_page_requires_qa_or_admin_role(
    client: AsyncClient,
    enumerator_token: str,
):
    """Test that enumerators cannot access QA records page."""
    response = await client.get(
        "/qa/records",
        cookies={"access_token": enumerator_token},
        follow_redirects=False,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_qa_records_page_accessible_by_qa_officer(
    client: AsyncClient,
    qa_officer_token: str,
):
    """Test that QA officers can access the records page."""
    response = await client.get(
        "/qa/records",
        cookies={"access_token": qa_officer_token},
    )
    assert response.status_code == 200
    assert b"QA Records" in response.content
    assert b"Filters" in response.content
    assert b"recordsTable" in response.content


@pytest.mark.asyncio
async def test_qa_records_page_accessible_by_admin(
    client: AsyncClient,
    admin_token: str,
):
    """Test that admins can access the records page."""
    response = await client.get(
        "/qa/records",
        cookies={"access_token": admin_token},
    )
    assert response.status_code == 200
    assert b"QA Records" in response.content


@pytest.mark.asyncio
async def test_qa_records_page_has_filter_controls(
    client: AsyncClient,
    qa_officer_token: str,
):
    """Test that the page includes all required filter controls."""
    response = await client.get(
        "/qa/records",
        cookies={"access_token": qa_officer_token},
    )
    assert response.status_code == 200
    
    # Check for filter controls
    assert b"filterStatus" in response.content
    assert b"filterEntityType" in response.content
    assert b"filterLga" in response.content
    assert b"filterWard" in response.content
    assert b"filterEnumerator" in response.content
    assert b"filterStartDate" in response.content
    assert b"filterEndDate" in response.content
    
    # Check for filter options
    assert b"Pending" in response.content
    assert b"Approved" in response.content
    assert b"Rejected" in response.content
    assert b"Building" in response.content
    assert b"Street" in response.content


@pytest.mark.asyncio
async def test_qa_records_page_has_pagination_controls(
    client: AsyncClient,
    qa_officer_token: str,
):
    """Test that the page includes pagination controls."""
    response = await client.get(
        "/qa/records",
        cookies={"access_token": qa_officer_token},
    )
    assert response.status_code == 200
    
    # Check for page size selector
    assert b"pageSize" in response.content
    assert b'value="10"' in response.content
    assert b'value="25"' in response.content
    assert b'value="50"' in response.content
    assert b'value="100"' in response.content
    
    # Check for pagination element
    assert b'id="pagination"' in response.content


@pytest.mark.asyncio
async def test_qa_records_page_has_statistics_cards(
    client: AsyncClient,
    qa_officer_token: str,
):
    """Test that the page displays statistics cards."""
    response = await client.get(
        "/qa/records",
        cookies={"access_token": qa_officer_token},
    )
    assert response.status_code == 200
    
    # Check for statistics elements
    assert b"totalRecords" in response.content
    assert b"pendingCount" in response.content
    assert b"approvedCount" in response.content
    assert b"rejectedCount" in response.content


@pytest.mark.asyncio
async def test_qa_records_page_has_records_table(
    client: AsyncClient,
    qa_officer_token: str,
):
    """Test that the page includes the records table with proper columns."""
    response = await client.get(
        "/qa/records",
        cookies={"access_token": qa_officer_token},
    )
    assert response.status_code == 200
    
    # Check for table structure
    assert b"recordsTable" in response.content
    assert b"recordsTableBody" in response.content
    
    # Check for table headers
    assert b"Type" in response.content
    assert b"Record ID" in response.content
    assert b"LGA" in response.content
    assert b"Ward" in response.content
    assert b"Enumerator" in response.content
    assert b"Submitted" in response.content
    assert b"Status" in response.content
    assert b"Actions" in response.content


@pytest.mark.asyncio
async def test_qa_records_page_has_auto_refresh(
    client: AsyncClient,
    qa_officer_token: str,
):
    """Test that the page includes auto-refresh functionality."""
    response = await client.get(
        "/qa/records",
        cookies={"access_token": qa_officer_token},
    )
    assert response.status_code == 200
    
    # Check for auto-refresh code
    assert b"startAutoRefresh" in response.content
    assert b"lastRefreshTime" in response.content


@pytest.mark.asyncio
async def test_qa_records_page_uses_common_js(
    client: AsyncClient,
    qa_officer_token: str,
):
    """Test that the page includes common.js utilities."""
    response = await client.get(
        "/qa/records",
        cookies={"access_token": qa_officer_token},
    )
    assert response.status_code == 200
    
    # Check for common.js inclusion
    assert b"/static/js/common.js" in response.content
    
    # Check for usage of common.js functions
    assert b"apiRequest" in response.content
    assert b"showNotification" in response.content
    assert b"getStatusBadge" in response.content
    assert b"formatDateTime" in response.content


@pytest.mark.asyncio
async def test_qa_records_page_has_view_detail_functionality(
    client: AsyncClient,
    qa_officer_token: str,
):
    """Test that the page includes functionality to view record details."""
    response = await client.get(
        "/qa/records",
        cookies={"access_token": qa_officer_token},
    )
    assert response.status_code == 200
    
    # Check for view detail function
    assert b"viewRecordDetail" in response.content
    assert b"/qa/records/" in response.content


@pytest.mark.asyncio
async def test_qa_records_page_responsive_design(
    client: AsyncClient,
    qa_officer_token: str,
):
    """Test that the page includes responsive design styles."""
    response = await client.get(
        "/qa/records",
        cookies={"access_token": qa_officer_token},
    )
    assert response.status_code == 200
    
    # Check for responsive CSS
    assert b"@media (max-width: 768px)" in response.content
    assert b"filter-grid" in response.content

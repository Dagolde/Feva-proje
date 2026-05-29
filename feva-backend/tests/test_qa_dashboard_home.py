"""Tests for QA dashboard home page.

Requirements: 2.1, 2.3, 2.4
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_qa_dashboard_home_requires_authentication(async_client: AsyncClient):
    """Test that unauthenticated users are redirected to login.
    
    Requirements: 2.2
    """
    response = await async_client.get("/qa/", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["location"]


@pytest.mark.asyncio
async def test_qa_dashboard_home_requires_qa_officer_or_admin_role(
    async_client: AsyncClient,
    enumerator_token: str,
):
    """Test that enumerators cannot access QA dashboard.
    
    Requirements: 2.5
    """
    response = await async_client.get(
        "/qa/",
        headers={"Authorization": f"Bearer {enumerator_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_qa_dashboard_home_accessible_by_qa_officer(
    async_client: AsyncClient,
    qa_token: str,
):
    """Test that QA officers can access the QA dashboard home page.
    
    Requirements: 2.1, 2.3
    """
    response = await async_client.get(
        "/qa/",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    assert b"QA Dashboard" in response.content
    assert b"Pending Records" in response.content
    assert b"Total Records" in response.content
    assert b"Approved Records" in response.content
    assert b"Rejected Records" in response.content


@pytest.mark.asyncio
async def test_qa_dashboard_home_accessible_by_admin(
    async_client: AsyncClient,
    admin_token: str,
):
    """Test that admins can access the QA dashboard home page.
    
    Requirements: 2.1, 2.4
    """
    response = await async_client.get(
        "/qa/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert b"QA Dashboard" in response.content


@pytest.mark.asyncio
async def test_qa_dashboard_home_displays_statistics_cards(
    async_client: AsyncClient,
    qa_token: str,
):
    """Test that the QA dashboard displays statistics cards.
    
    Requirements: 2.3
    """
    response = await async_client.get(
        "/qa/",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    # Check for statistics card elements
    content = response.content.decode()
    assert "pendingRecords" in content
    assert "totalRecords" in content
    assert "approvedRecords" in content
    assert "rejectedRecords" in content


@pytest.mark.asyncio
async def test_qa_dashboard_home_displays_quick_actions(
    async_client: AsyncClient,
    qa_token: str,
):
    """Test that the QA dashboard displays quick action links.
    
    Requirements: 2.3
    """
    response = await async_client.get(
        "/qa/",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    content = response.content.decode()
    # Check for quick action links
    assert "/qa/records?status=pending" in content
    assert "/qa/records" in content
    assert "/qa/flagged" in content
    assert "/qa/reports" in content
    
    # Check for quick action labels
    assert "Review Pending Records" in content
    assert "All Records" in content
    assert "Flagged Records" in content
    assert "QA Reports" in content


@pytest.mark.asyncio
async def test_qa_dashboard_home_displays_recent_activity_section(
    async_client: AsyncClient,
    qa_token: str,
):
    """Test that the QA dashboard displays recent activity section.
    
    Requirements: 2.3
    """
    response = await async_client.get(
        "/qa/",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    content = response.content.decode()
    assert "Recent QA Activity" in content
    assert "recentActivity" in content


@pytest.mark.asyncio
async def test_qa_dashboard_home_includes_auto_refresh_script(
    async_client: AsyncClient,
    qa_token: str,
):
    """Test that the QA dashboard includes auto-refresh functionality.
    
    Requirements: 17.1 (auto-refresh for real-time updates)
    """
    response = await async_client.get(
        "/qa/",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    content = response.content.decode()
    # Check for auto-refresh function call
    assert "startAutoRefresh" in content
    # Check for 60 second interval (QA dashboard requirement)
    assert "60" in content or "refreshDashboard, 60" in content


@pytest.mark.asyncio
async def test_qa_dashboard_home_includes_statistics_api_call(
    async_client: AsyncClient,
    qa_token: str,
):
    """Test that the QA dashboard includes API call to statistics endpoint.
    
    Requirements: 2.3
    """
    response = await async_client.get(
        "/qa/",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    content = response.content.decode()
    # Check for API endpoint call
    assert "/api/v1/qa/statistics" in content
    assert "loadQAStatistics" in content


@pytest.mark.asyncio
async def test_qa_dashboard_home_includes_last_update_timestamp(
    async_client: AsyncClient,
    qa_token: str,
):
    """Test that the QA dashboard displays last update timestamp.
    
    Requirements: 17.5 (display last update timestamp)
    """
    response = await async_client.get(
        "/qa/",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    content = response.content.decode()
    assert "Last updated:" in content or "lastRefreshTime" in content


@pytest.mark.asyncio
async def test_qa_dashboard_home_uses_qa_layout(
    async_client: AsyncClient,
    qa_token: str,
):
    """Test that the QA dashboard home page uses the QA layout template.
    
    Requirements: 2.1
    """
    response = await async_client.get(
        "/qa/",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    content = response.content.decode()
    # Check for QA layout elements (sidebar navigation)
    assert "Dashboard" in content
    assert "All Records" in content
    assert "Flagged Records" in content
    assert "Reports" in content

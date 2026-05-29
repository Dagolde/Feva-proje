"""Tests for QA record detail page.

Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 12.1, 12.2
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.models.building import Building
from app.models.street import Street
from app.models.user import User
from app.models.photo import Photo


@pytest.mark.asyncio
async def test_qa_record_detail_page_requires_authentication(client: AsyncClient):
    """Test that record detail page requires authentication.
    
    Requirements: 2.2
    """
    # Create a fake record ID
    record_id = str(uuid4())
    
    # Try to access without authentication
    response = await client.get(f"/qa/records/{record_id}?entity_type=building")
    
    # Should redirect to login or return 401
    assert response.status_code in (302, 401)


@pytest.mark.asyncio
async def test_qa_record_detail_page_requires_qa_or_admin_role(
    client: AsyncClient,
    db: AsyncSession,
    enumerator_token: str,
):
    """Test that record detail page requires qa_officer or admin role.
    
    Requirements: 2.5
    """
    # Create a fake record ID
    record_id = str(uuid4())
    
    # Try to access with enumerator role
    response = await client.get(
        f"/qa/records/{record_id}?entity_type=building",
        headers={"Authorization": f"Bearer {enumerator_token}"}
    )
    
    # Should return 403 Forbidden
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_qa_record_detail_page_accessible_by_qa_officer(
    client: AsyncClient,
    db: AsyncSession,
    qa_officer_token: str,
):
    """Test that QA officer can access record detail page.
    
    Requirements: 2.3
    """
    # Create a fake record ID (page should load even if record doesn't exist)
    record_id = str(uuid4())
    
    # Access with QA officer role
    response = await client.get(
        f"/qa/records/{record_id}?entity_type=building",
        headers={"Authorization": f"Bearer {qa_officer_token}"}
    )
    
    # Should return 200 OK with HTML
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_qa_record_detail_page_accessible_by_admin(
    client: AsyncClient,
    db: AsyncSession,
    admin_token: str,
):
    """Test that admin can access record detail page.
    
    Requirements: 2.4
    """
    # Create a fake record ID
    record_id = str(uuid4())
    
    # Access with admin role
    response = await client.get(
        f"/qa/records/{record_id}?entity_type=building",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Should return 200 OK with HTML
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]



@pytest.mark.asyncio
async def test_record_detail_page_contains_required_elements(
    client: AsyncClient,
    db: AsyncSession,
    qa_officer_token: str,
):
    """Test that record detail page contains all required UI elements.
    
    Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7
    """
    # Create a fake record ID
    record_id = str(uuid4())
    
    # Access the page
    response = await client.get(
        f"/qa/records/{record_id}?entity_type=building",
        headers={"Authorization": f"Bearer {qa_officer_token}"}
    )
    
    assert response.status_code == 200
    html = response.text
    
    # Check for key page elements
    assert "Record Detail" in html
    assert "recordData" in html  # Record information section
    assert "gpsData" in html  # GPS information section
    assert "recordMap" in html  # Interactive map
    assert "photoGallery" in html  # Photo gallery
    assert "auditTrail" in html  # Audit trail section
    assert "approveBtn" in html  # Approve button
    assert "rejectBtn" in html  # Reject button


@pytest.mark.asyncio
async def test_record_detail_page_has_back_to_records_link(
    client: AsyncClient,
    db: AsyncSession,
    qa_officer_token: str,
):
    """Test that record detail page has a back to records link.
    
    Requirements: 11.1
    """
    record_id = str(uuid4())
    
    response = await client.get(
        f"/qa/records/{record_id}?entity_type=building",
        headers={"Authorization": f"Bearer {qa_officer_token}"}
    )
    
    assert response.status_code == 200
    html = response.text
    
    # Check for back link
    assert "/qa/records" in html
    assert "Back to Records" in html


@pytest.mark.asyncio
async def test_record_detail_page_includes_approval_controls(
    client: AsyncClient,
    db: AsyncSession,
    qa_officer_token: str,
):
    """Test that record detail page includes approval and rejection controls.
    
    Requirements: 12.1, 12.2
    """
    record_id = str(uuid4())
    
    response = await client.get(
        f"/qa/records/{record_id}?entity_type=building",
        headers={"Authorization": f"Bearer {qa_officer_token}"}
    )
    
    assert response.status_code == 200
    html = response.text
    
    # Check for approval/rejection controls
    assert "approveRecord" in html  # Approve function
    assert "showRejectModal" in html  # Reject modal function
    assert "Approve" in html
    assert "Reject" in html


@pytest.mark.asyncio
async def test_record_detail_page_includes_rejection_modal(
    client: AsyncClient,
    db: AsyncSession,
    qa_officer_token: str,
):
    """Test that record detail page includes rejection modal with reason input.
    
    Requirements: 12.2, 12.3
    """
    record_id = str(uuid4())
    
    response = await client.get(
        f"/qa/records/{record_id}?entity_type=building",
        headers={"Authorization": f"Bearer {qa_officer_token}"}
    )
    
    assert response.status_code == 200
    html = response.text
    
    # Check for rejection modal elements
    assert "rejectModal" in html
    assert "rejectionReasonInput" in html
    assert "Enter rejection reason" in html
    assert "confirmReject" in html


@pytest.mark.asyncio
async def test_record_detail_page_loads_data_via_api(
    client: AsyncClient,
    db: AsyncSession,
    qa_officer_token: str,
):
    """Test that record detail page loads data via API endpoints.
    
    Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7
    """
    record_id = str(uuid4())
    
    response = await client.get(
        f"/qa/records/{record_id}?entity_type=building",
        headers={"Authorization": f"Bearer {qa_officer_token}"}
    )
    
    assert response.status_code == 200
    html = response.text
    
    # Check that page makes API calls to load data
    assert "/api/v1/qa/records/" in html  # Record detail API
    assert "loadRecordDetail" in html  # Function to load record
    assert "loadAuditTrail" in html  # Function to load audit trail


@pytest.mark.asyncio
async def test_record_detail_page_supports_both_entity_types(
    client: AsyncClient,
    db: AsyncSession,
    qa_officer_token: str,
):
    """Test that record detail page supports both building and street entity types.
    
    Requirements: 11.1
    """
    record_id = str(uuid4())
    
    # Test with building entity type
    response_building = await client.get(
        f"/qa/records/{record_id}?entity_type=building",
        headers={"Authorization": f"Bearer {qa_officer_token}"}
    )
    assert response_building.status_code == 200
    
    # Test with street entity type
    response_street = await client.get(
        f"/qa/records/{record_id}?entity_type=street",
        headers={"Authorization": f"Bearer {qa_officer_token}"}
    )
    assert response_street.status_code == 200


@pytest.mark.asyncio
async def test_record_detail_page_includes_photo_viewer_modal(
    client: AsyncClient,
    db: AsyncSession,
    qa_officer_token: str,
):
    """Test that record detail page includes photo viewer modal.
    
    Requirements: 11.4
    """
    record_id = str(uuid4())
    
    response = await client.get(
        f"/qa/records/{record_id}?entity_type=building",
        headers={"Authorization": f"Bearer {qa_officer_token}"}
    )
    
    assert response.status_code == 200
    html = response.text
    
    # Check for photo viewer modal
    assert "photoModal" in html
    assert "photoModalImage" in html
    assert "viewPhoto" in html
    assert "closePhotoModal" in html


@pytest.mark.asyncio
async def test_record_detail_page_displays_audit_trail(
    client: AsyncClient,
    db: AsyncSession,
    qa_officer_token: str,
):
    """Test that record detail page displays audit trail section.
    
    Requirements: 11.7, 14.1, 14.2, 14.3, 14.4
    """
    record_id = str(uuid4())
    
    response = await client.get(
        f"/qa/records/{record_id}?entity_type=building",
        headers={"Authorization": f"Bearer {qa_officer_token}"}
    )
    
    assert response.status_code == 200
    html = response.text
    
    # Check for audit trail elements
    assert "Audit Trail" in html
    assert "auditTrail" in html
    assert "renderAuditTrail" in html


@pytest.mark.asyncio
async def test_record_detail_page_responsive_design(
    client: AsyncClient,
    db: AsyncSession,
    qa_officer_token: str,
):
    """Test that record detail page includes responsive design CSS.
    
    Requirements: 15.3, 15.4
    """
    record_id = str(uuid4())
    
    response = await client.get(
        f"/qa/records/{record_id}?entity_type=building",
        headers={"Authorization": f"Bearer {qa_officer_token}"}
    )
    
    assert response.status_code == 200
    html = response.text
    
    # Check for responsive design media queries
    assert "@media" in html
    assert "max-width: 1024px" in html or "max-width: 768px" in html

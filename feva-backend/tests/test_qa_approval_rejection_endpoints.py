"""Tests for QA approval and rejection endpoints.

Task 11.10: Create approval and rejection endpoints
Requirements: 19.3, 19.4, 19.7
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building
from app.models.street import Street
from app.models.user import User


@pytest.mark.asyncio
async def test_approve_building_success(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    qa_user: User,
):
    """Test successful building approval."""
    # Create a pending building record
    building = Building(
        id=uuid4(),
        building_id="TEST-BLD-APPROVE-001",
        lga="Test LGA",
        ward="Test Ward",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
        latitude=6.5244,
        longitude=3.3792,
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Get QA token
    from app.core.security import create_access_token
    qa_token = create_access_token({"sub": str(qa_user.id), "role": "qa_officer"})
    
    # Approve the building
    response = await async_client.post(
        f"/api/v1/qa/records/{building.id}/approve?entity_type=building",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert "successfully" in data["message"].lower()
    
    # Verify the building was updated
    await async_db_session.refresh(building)
    assert building.verification_status == "approved"
    assert building.reviewed_by == qa_user.id
    assert building.reviewed_at is not None
    assert building.rejection_reason is None


@pytest.mark.asyncio
async def test_reject_building_success(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    qa_user: User,
):
    """Test successful building rejection."""
    # Create a pending building record
    building = Building(
        id=uuid4(),
        building_id="TEST-BLD-REJECT-001",
        lga="Test LGA",
        ward="Test Ward",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
        latitude=6.5244,
        longitude=3.3792,
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Get QA token
    from app.core.security import create_access_token
    qa_token = create_access_token({"sub": str(qa_user.id), "role": "qa_officer"})
    
    # Reject the building
    rejection_reason = "GPS coordinates are inaccurate"
    response = await async_client.post(
        f"/api/v1/qa/records/{building.id}/reject?entity_type=building",
        headers={"Authorization": f"Bearer {qa_token}"},
        json={"rejection_reason": rejection_reason},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert "successfully" in data["message"].lower()
    
    # Verify the building was updated
    await async_db_session.refresh(building)
    assert building.verification_status == "rejected"
    assert building.reviewed_by == qa_user.id
    assert building.reviewed_at is not None
    assert building.rejection_reason == rejection_reason


@pytest.mark.asyncio
async def test_approve_invalid_entity_type(
    async_client: AsyncClient,
    qa_user: User,
):
    """Test approval with invalid entity_type."""
    from app.core.security import create_access_token
    qa_token = create_access_token({"sub": str(qa_user.id), "role": "qa_officer"})
    
    record_id = uuid4()
    response = await async_client.post(
        f"/api/v1/qa/records/{record_id}/approve?entity_type=invalid",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    
    assert response.status_code == 400
    assert "entity_type must be" in response.json()["details"]


@pytest.mark.asyncio
async def test_approve_invalid_record_id(
    async_client: AsyncClient,
    qa_user: User,
):
    """Test approval with invalid record ID format."""
    from app.core.security import create_access_token
    qa_token = create_access_token({"sub": str(qa_user.id), "role": "qa_officer"})
    
    response = await async_client.post(
        "/api/v1/qa/records/not-a-uuid/approve?entity_type=building",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    
    assert response.status_code == 400
    assert "Invalid record ID" in response.json()["details"]


@pytest.mark.asyncio
async def test_approve_nonexistent_record(
    async_client: AsyncClient,
    qa_user: User,
):
    """Test approval of non-existent record."""
    from app.core.security import create_access_token
    qa_token = create_access_token({"sub": str(qa_user.id), "role": "qa_officer"})
    
    record_id = uuid4()
    response = await async_client.post(
        f"/api/v1/qa/records/{record_id}/approve?entity_type=building",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["details"].lower()


@pytest.mark.asyncio
async def test_approve_already_reviewed_record(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    qa_user: User,
):
    """Test approval of already reviewed record."""
    # Create an already approved building
    building = Building(
        id=uuid4(),
        building_id="TEST-BLD-ALREADY-APPROVED",
        lga="Test LGA",
        ward="Test Ward",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="approved",
        reviewed_by=qa_user.id,
        reviewed_at=datetime.now(timezone.utc),
        latitude=6.5244,
        longitude=3.3792,
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Get QA token
    from app.core.security import create_access_token
    qa_token = create_access_token({"sub": str(qa_user.id), "role": "qa_officer"})
    
    # Try to approve again
    response = await async_client.post(
        f"/api/v1/qa/records/{building.id}/approve?entity_type=building",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    
    assert response.status_code == 409
    assert "already reviewed" in response.json()["details"].lower()


@pytest.mark.asyncio
async def test_reject_empty_reason(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    qa_user: User,
):
    """Test rejection with empty reason."""
    # Create a pending building
    building = Building(
        id=uuid4(),
        building_id="TEST-BLD-EMPTY-REASON",
        lga="Test LGA",
        ward="Test Ward",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
        latitude=6.5244,
        longitude=3.3792,
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Get QA token
    from app.core.security import create_access_token
    qa_token = create_access_token({"sub": str(qa_user.id), "role": "qa_officer"})
    
    # Try to reject with empty reason
    response = await async_client.post(
        f"/api/v1/qa/records/{building.id}/reject?entity_type=building",
        headers={"Authorization": f"Bearer {qa_token}"},
        json={"rejection_reason": ""},
    )
    
    assert response.status_code == 400
    assert "empty" in response.json()["details"].lower()


@pytest.mark.asyncio
async def test_admin_can_approve(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
):
    """Test that admin users can approve records."""
    # Create a pending building
    building = Building(
        id=uuid4(),
        building_id="TEST-BLD-ADMIN-APPROVE",
        lga="Test LGA",
        ward="Test Ward",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
        latitude=6.5244,
        longitude=3.3792,
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Get admin token
    from app.core.security import create_access_token
    admin_token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
    
    # Approve as admin
    response = await async_client.post(
        f"/api/v1/qa/records/{building.id}/approve?entity_type=building",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    
    # Verify the building was updated
    await async_db_session.refresh(building)
    assert building.verification_status == "approved"
    assert building.reviewed_by == admin_user.id


@pytest.mark.asyncio
async def test_admin_can_reject(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
):
    """Test that admin users can reject records."""
    # Create a pending building
    building = Building(
        id=uuid4(),
        building_id="TEST-BLD-ADMIN-REJECT",
        lga="Test LGA",
        ward="Test Ward",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
        latitude=6.5244,
        longitude=3.3792,
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Get admin token
    from app.core.security import create_access_token
    admin_token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
    
    # Reject as admin
    response = await async_client.post(
        f"/api/v1/qa/records/{building.id}/reject?entity_type=building",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"rejection_reason": "Admin rejection"},
    )
    
    assert response.status_code == 200
    
    # Verify the building was updated
    await async_db_session.refresh(building)
    assert building.verification_status == "rejected"
    assert building.reviewed_by == admin_user.id
    assert building.rejection_reason == "Admin rejection"


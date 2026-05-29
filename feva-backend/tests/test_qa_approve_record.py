"""Unit tests for QA record approval operation.

Tests the approve_record() function in QAService to ensure:
- Records are approved correctly
- Status and metadata are updated
- Already-reviewed records cannot be re-reviewed
- Audit logs are created
- Invalid inputs are rejected

Requirements: 12.1, 12.4, 12.6, 12.7
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry import Point, LineString
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.building import Building
from app.models.street import Street
from app.models.user import User
from app.services.qa_service import approve_record


@pytest.mark.asyncio
async def test_approve_building_record_success(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test successful approval of a building record."""
    # Create a pending building record
    building = Building(
        building_id=f"BLD-{uuid.uuid4().hex[:8]}",
        street_id="STR-TEST-001",
        building_type="residential",
        number_of_floors=2,
        number_of_units=4,
        building_condition="good",
        has_signage=False,
        geom=from_shape(Point(3.3792, 6.5244), srid=4326),
        gps_accuracy_m=Decimal("5.0"),
        lga="Lagos",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
        rejection_reason="Previous rejection",  # Should be cleared
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Approve the record
    await approve_record(
        db=async_db_session,
        record_id=building.id,
        entity_type="building",
        reviewer_id=qa_user.id,
    )
    
    # Verify the building was updated
    result = await async_db_session.execute(select(Building).where(Building.id == building.id))
    updated_building = result.scalar_one()
    
    assert updated_building.verification_status == "approved"
    assert updated_building.reviewed_by == qa_user.id
    assert updated_building.reviewed_at is not None
    assert updated_building.rejection_reason is None  # Should be cleared
    
    # Verify audit log was created
    audit_result = await async_db_session.execute(
        select(AuditLog).where(
            AuditLog.operation == "approve_record",
            AuditLog.entity_type == "building",
            AuditLog.entity_id == str(building.id),
        )
    )
    audit = audit_result.scalar_one()
    assert audit.user_id == qa_user.id


@pytest.mark.asyncio
async def test_approve_street_record_success(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test successful approval of a street record."""
    # Create a pending street record
    street = Street(
        street_id=f"STR-{uuid.uuid4().hex[:8]}",
        street_name="Test Avenue",
        street_type="commercial",
        surface_type="paved",
        street_condition="excellent",
        geom=from_shape(LineString([(3.3792, 6.5244), (3.3793, 6.5245)]), srid=4326),
        lga="Lagos",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
        rejection_reason="Old rejection",  # Should be cleared
    )
    async_db_session.add(street)
    await async_db_session.commit()
    
    # Approve the record
    await approve_record(
        db=async_db_session,
        record_id=street.id,
        entity_type="street",
        reviewer_id=qa_user.id,
    )
    
    # Verify the street was updated
    result = await async_db_session.execute(select(Street).where(Street.id == street.id))
    updated_street = result.scalar_one()
    
    assert updated_street.verification_status == "approved"
    assert updated_street.reviewed_by == qa_user.id
    assert updated_street.reviewed_at is not None
    assert updated_street.rejection_reason is None  # Should be cleared
    
    # Verify audit log was created
    audit_result = await async_db_session.execute(
        select(AuditLog).where(
            AuditLog.operation == "approve_record",
            AuditLog.entity_type == "street",
            AuditLog.entity_id == str(street.id),
        )
    )
    audit = audit_result.scalar_one()
    assert audit.user_id == qa_user.id


@pytest.mark.asyncio
async def test_approve_already_approved_record_fails(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test that approving an already-approved record raises an error."""
    # Create an already-approved building record
    building = Building(
        building_id=f"BLD-{uuid.uuid4().hex[:8]}",
        street_id="STR-TEST-002",
        building_type="commercial",
        number_of_floors=3,
        number_of_units=6,
        building_condition="good",
        has_signage=True,
        geom=from_shape(Point(3.3792, 6.5244), srid=4326),
        gps_accuracy_m=Decimal("4.5"),
        lga="Lagos",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="approved",  # Already approved
        reviewed_by=qa_user.id,
        reviewed_at=datetime.now(timezone.utc),
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Attempt to approve again should fail
    with pytest.raises(ValueError, match="Record already reviewed"):
        await approve_record(
            db=async_db_session,
            record_id=building.id,
            entity_type="building",
            reviewer_id=qa_user.id,
        )


@pytest.mark.asyncio
async def test_approve_already_rejected_record_fails(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test that approving an already-rejected record raises an error."""
    # Create an already-rejected street record
    street = Street(
        street_id=f"STR-{uuid.uuid4().hex[:8]}",
        street_name="Rejected Street",
        street_type="residential",
        surface_type="unpaved",
        street_condition="poor",
        geom=from_shape(LineString([(3.3792, 6.5244), (3.3793, 6.5245)]), srid=4326),
        lga="Lagos",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="rejected",  # Already rejected
        reviewed_by=qa_user.id,
        reviewed_at=datetime.now(timezone.utc),
        rejection_reason="Poor data quality",
    )
    async_db_session.add(street)
    await async_db_session.commit()
    
    # Attempt to approve should fail
    with pytest.raises(ValueError, match="Record already reviewed"):
        await approve_record(
            db=async_db_session,
            record_id=street.id,
            entity_type="street",
            reviewer_id=qa_user.id,
        )


@pytest.mark.asyncio
async def test_approve_nonexistent_building_fails(async_db_session: AsyncSession, qa_user: User):
    """Test that approving a non-existent building raises an error."""
    nonexistent_id = uuid.uuid4()
    
    with pytest.raises(ValueError, match="Building not found"):
        await approve_record(
            db=async_db_session,
            record_id=nonexistent_id,
            entity_type="building",
            reviewer_id=qa_user.id,
        )


@pytest.mark.asyncio
async def test_approve_nonexistent_street_fails(async_db_session: AsyncSession, qa_user: User):
    """Test that approving a non-existent street raises an error."""
    nonexistent_id = uuid.uuid4()
    
    with pytest.raises(ValueError, match="Street not found"):
        await approve_record(
            db=async_db_session,
            record_id=nonexistent_id,
            entity_type="street",
            reviewer_id=qa_user.id,
        )


@pytest.mark.asyncio
async def test_approve_invalid_entity_type_fails(async_db_session: AsyncSession, qa_user: User):
    """Test that approving with invalid entity_type raises an error."""
    record_id = uuid.uuid4()
    
    with pytest.raises(ValueError, match="Invalid entity_type"):
        await approve_record(
            db=async_db_session,
            record_id=record_id,
            entity_type="invalid_type",
            reviewer_id=qa_user.id,
        )

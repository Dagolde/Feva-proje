"""Unit tests for QA record rejection operation.

Tests the reject_record() function in QAService to ensure:
- Records are rejected correctly with valid reasons
- Empty/whitespace rejection reasons are rejected
- Status and metadata are updated
- Already-reviewed records cannot be re-rejected
- Audit logs are created

Requirements: 12.2, 12.3, 12.5, 12.6, 12.7
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
from app.services.qa_service import reject_record


@pytest.mark.asyncio
async def test_reject_building_record_success(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test successful rejection of a building record."""
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
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Reject the record
    await reject_record(
        db=async_db_session,
        record_id=building.id,
        entity_type="building",
        reviewer_id=qa_user.id,
        rejection_reason="GPS accuracy is too low",
    )
    
    # Verify the building was updated
    result = await async_db_session.execute(select(Building).where(Building.id == building.id))
    updated_building = result.scalar_one()
    
    assert updated_building.verification_status == "rejected"
    assert updated_building.reviewed_by == qa_user.id
    assert updated_building.reviewed_at is not None
    assert updated_building.rejection_reason == "GPS accuracy is too low"
    
    # Verify audit log was created
    audit_result = await async_db_session.execute(
        select(AuditLog).where(
            AuditLog.operation == "reject_record",
            AuditLog.entity_type == "building",
            AuditLog.entity_id == str(building.id),
        )
    )
    audit = audit_result.scalar_one()
    assert audit.user_id == qa_user.id


@pytest.mark.asyncio
async def test_reject_street_record_success(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test successful rejection of a street record."""
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
    )
    async_db_session.add(street)
    await async_db_session.commit()
    
    # Reject the record
    await reject_record(
        db=async_db_session,
        record_id=street.id,
        entity_type="street",
        reviewer_id=qa_user.id,
        rejection_reason="Street name is incorrect",
    )
    
    # Verify the street was updated
    result = await async_db_session.execute(select(Street).where(Street.id == street.id))
    updated_street = result.scalar_one()
    
    assert updated_street.verification_status == "rejected"
    assert updated_street.reviewed_by == qa_user.id
    assert updated_street.reviewed_at is not None
    assert updated_street.rejection_reason == "Street name is incorrect"
    
    # Verify audit log was created
    audit_result = await async_db_session.execute(
        select(AuditLog).where(
            AuditLog.operation == "reject_record",
            AuditLog.entity_type == "street",
            AuditLog.entity_id == str(street.id),
        )
    )
    audit = audit_result.scalar_one()
    assert audit.user_id == qa_user.id


@pytest.mark.asyncio
async def test_reject_record_empty_reason_fails(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test that rejection with empty reason fails."""
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
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Try to reject with empty reason
    with pytest.raises(ValueError, match="Rejection reason cannot be empty"):
        await reject_record(
            db=async_db_session,
            record_id=building.id,
            entity_type="building",
            reviewer_id=qa_user.id,
            rejection_reason="",
        )
    
    # Try to reject with whitespace-only reason
    with pytest.raises(ValueError, match="Rejection reason cannot be empty"):
        await reject_record(
            db=async_db_session,
            record_id=building.id,
            entity_type="building",
            reviewer_id=qa_user.id,
            rejection_reason="   ",
        )


@pytest.mark.asyncio
async def test_reject_already_approved_record_fails(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test that rejecting an already-approved record fails."""
    # Create an already-approved building record
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
        verification_status="approved",
        reviewed_by=qa_user.id,
        reviewed_at=datetime.now(timezone.utc),
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Try to reject the already-approved record
    with pytest.raises(ValueError, match="Record already reviewed with status: approved"):
        await reject_record(
            db=async_db_session,
            record_id=building.id,
            entity_type="building",
            reviewer_id=qa_user.id,
            rejection_reason="Trying to reject approved record",
        )


@pytest.mark.asyncio
async def test_reject_already_rejected_record_fails(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test that rejecting an already-rejected record fails."""
    # Create an already-rejected building record
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
        verification_status="rejected",
        reviewed_by=qa_user.id,
        reviewed_at=datetime.now(timezone.utc),
        rejection_reason="Initial rejection",
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Try to reject the already-rejected record
    with pytest.raises(ValueError, match="Record already reviewed with status: rejected"):
        await reject_record(
            db=async_db_session,
            record_id=building.id,
            entity_type="building",
            reviewer_id=qa_user.id,
            rejection_reason="Trying to reject again",
        )


@pytest.mark.asyncio
async def test_reject_record_strips_whitespace(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test that rejection reason is stripped of leading/trailing whitespace."""
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
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Reject with whitespace around reason
    await reject_record(
        db=async_db_session,
        record_id=building.id,
        entity_type="building",
        reviewer_id=qa_user.id,
        rejection_reason="  GPS accuracy is too low  ",
    )
    
    # Verify whitespace was stripped
    result = await async_db_session.execute(select(Building).where(Building.id == building.id))
    updated_building = result.scalar_one()
    
    assert updated_building.rejection_reason == "GPS accuracy is too low"

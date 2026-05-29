"""Tests for QA record rejection functionality.

Tests the reject_record() function in QAService to ensure:
- Records can be rejected with valid rejection reasons
- Empty/whitespace rejection reasons are rejected
- Already-reviewed records cannot be re-rejected
- Audit logs are created for rejection actions
- Both building and street records can be rejected
"""
import uuid
from datetime import datetime, timezone

import pytest
from geoalchemy2.elements import WKTElement
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.building import Building
from app.models.street import Street
from app.models.user import User
from app.services.qa_service import reject_record


def _make_users(suffix: str):
    """Create enumerator and reviewer users with unique names."""
    enumerator = User(
        id=uuid.uuid4(),
        username=f"enum_rej_{suffix}",
        email=f"enum_rej_{suffix}@test.com",
        password_hash="hash",
        role_id=2,
    )
    reviewer = User(
        id=uuid.uuid4(),
        username=f"qa_rej_{suffix}",
        email=f"qa_rej_{suffix}@test.com",
        password_hash="hash",
        role_id=4,
    )
    return enumerator, reviewer


def _make_street(suffix: str, enumerator_id: uuid.UUID) -> Street:
    return Street(
        street_id=f"STR-REJ-{suffix}",
        street_name="Test Street",
        street_type="Primary",
        surface_type="Asphalt",
        street_condition="Good",
        geom=WKTElement("LINESTRING(3.3792 6.5244, 3.3793 6.5245)", srid=4326),
        lga="Lagos",
        enumerator_id=enumerator_id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
    )


def _make_building(suffix: str, street_id: str, enumerator_id: uuid.UUID, **kwargs) -> Building:
    return Building(
        id=uuid.uuid4(),
        building_id=f"BLD-REJ-{suffix}",
        street_id=street_id,
        building_type="Residential",
        number_of_floors=2,
        number_of_units=4,
        building_condition="Good",
        has_signage=False,
        geom=WKTElement("POINT(3.3792 6.5244)", srid=4326),
        gps_accuracy_m=5.0,
        lga="Lagos",
        enumerator_id=enumerator_id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
        **kwargs,
    )


@pytest.mark.asyncio
async def test_reject_building_record_success(async_db_session: AsyncSession):
    """Test successful rejection of a building record."""
    suffix = uuid.uuid4().hex[:8]
    enumerator, reviewer = _make_users(suffix)
    async_db_session.add_all([enumerator, reviewer])
    await async_db_session.flush()

    street = _make_street(suffix, enumerator.id)
    async_db_session.add(street)
    await async_db_session.flush()

    building = _make_building(suffix, street.street_id, enumerator.id)
    async_db_session.add(building)
    await async_db_session.commit()

    await reject_record(
        db=async_db_session,
        record_id=building.id,
        entity_type="building",
        reviewer_id=reviewer.id,
        rejection_reason="GPS accuracy is too low",
    )

    result = await async_db_session.execute(select(Building).where(Building.id == building.id))
    updated = result.scalar_one()

    assert updated.verification_status == "rejected"
    assert updated.reviewed_by == reviewer.id
    assert updated.reviewed_at is not None
    assert updated.rejection_reason == "GPS accuracy is too low"

    audit_result = await async_db_session.execute(
        select(AuditLog).where(
            AuditLog.operation == "reject_record",
            AuditLog.entity_type == "building",
            AuditLog.entity_id == str(building.id),
        )
    )
    audit = audit_result.scalar_one()
    assert audit.user_id == reviewer.id


@pytest.mark.asyncio
async def test_reject_street_record_success(async_db_session: AsyncSession):
    """Test successful rejection of a street record."""
    suffix = uuid.uuid4().hex[:8]
    enumerator, reviewer = _make_users(suffix)
    async_db_session.add_all([enumerator, reviewer])
    await async_db_session.flush()

    street = _make_street(suffix, enumerator.id)
    async_db_session.add(street)
    await async_db_session.commit()

    await reject_record(
        db=async_db_session,
        record_id=street.id,
        entity_type="street",
        reviewer_id=reviewer.id,
        rejection_reason="Street name is incorrect",
    )

    result = await async_db_session.execute(select(Street).where(Street.id == street.id))
    updated = result.scalar_one()

    assert updated.verification_status == "rejected"
    assert updated.reviewed_by == reviewer.id
    assert updated.reviewed_at is not None
    assert updated.rejection_reason == "Street name is incorrect"

    audit_result = await async_db_session.execute(
        select(AuditLog).where(
            AuditLog.operation == "reject_record",
            AuditLog.entity_type == "street",
            AuditLog.entity_id == str(street.id),
        )
    )
    audit = audit_result.scalar_one()
    assert audit.user_id == reviewer.id


@pytest.mark.asyncio
async def test_reject_record_empty_reason_fails(async_db_session: AsyncSession):
    """Test that rejection with empty reason fails."""
    suffix = uuid.uuid4().hex[:8]
    enumerator, reviewer = _make_users(suffix)
    async_db_session.add_all([enumerator, reviewer])
    await async_db_session.flush()

    street = _make_street(suffix, enumerator.id)
    async_db_session.add(street)
    await async_db_session.flush()

    building = _make_building(suffix, street.street_id, enumerator.id)
    async_db_session.add(building)
    await async_db_session.commit()

    with pytest.raises(ValueError, match="Rejection reason cannot be empty"):
        await reject_record(
            db=async_db_session,
            record_id=building.id,
            entity_type="building",
            reviewer_id=reviewer.id,
            rejection_reason="",
        )

    with pytest.raises(ValueError, match="Rejection reason cannot be empty"):
        await reject_record(
            db=async_db_session,
            record_id=building.id,
            entity_type="building",
            reviewer_id=reviewer.id,
            rejection_reason="   ",
        )


@pytest.mark.asyncio
async def test_reject_already_approved_record_fails(async_db_session: AsyncSession):
    """Test that rejecting an already-approved record fails."""
    suffix = uuid.uuid4().hex[:8]
    enumerator, reviewer = _make_users(suffix)
    async_db_session.add_all([enumerator, reviewer])
    await async_db_session.flush()

    street = _make_street(suffix, enumerator.id)
    async_db_session.add(street)
    await async_db_session.flush()

    building = _make_building(
        suffix, street.street_id, enumerator.id,
        verification_status="approved",
        reviewed_by=reviewer.id,
        reviewed_at=datetime.now(timezone.utc),
    )
    async_db_session.add(building)
    await async_db_session.commit()

    with pytest.raises(ValueError, match="Record already reviewed with status: approved"):
        await reject_record(
            db=async_db_session,
            record_id=building.id,
            entity_type="building",
            reviewer_id=reviewer.id,
            rejection_reason="Trying to reject approved record",
        )


@pytest.mark.asyncio
async def test_reject_already_rejected_record_fails(async_db_session: AsyncSession):
    """Test that rejecting an already-rejected record fails."""
    suffix = uuid.uuid4().hex[:8]
    enumerator, reviewer = _make_users(suffix)
    async_db_session.add_all([enumerator, reviewer])
    await async_db_session.flush()

    street = _make_street(suffix, enumerator.id)
    async_db_session.add(street)
    await async_db_session.flush()

    building = _make_building(
        suffix, street.street_id, enumerator.id,
        verification_status="rejected",
        reviewed_by=reviewer.id,
        reviewed_at=datetime.now(timezone.utc),
        rejection_reason="Initial rejection",
    )
    async_db_session.add(building)
    await async_db_session.commit()

    with pytest.raises(ValueError, match="Record already reviewed with status: rejected"):
        await reject_record(
            db=async_db_session,
            record_id=building.id,
            entity_type="building",
            reviewer_id=reviewer.id,
            rejection_reason="Trying to reject again",
        )


@pytest.mark.asyncio
async def test_reject_record_invalid_entity_type(async_db_session: AsyncSession):
    """Test that invalid entity_type raises error."""
    reviewer_id = uuid.uuid4()
    record_id = uuid.uuid4()

    with pytest.raises(ValueError, match="Invalid entity_type: invalid"):
        await reject_record(
            db=async_db_session,
            record_id=record_id,
            entity_type="invalid",
            reviewer_id=reviewer_id,
            rejection_reason="Test reason",
        )


@pytest.mark.asyncio
async def test_reject_record_not_found(async_db_session: AsyncSession):
    """Test that rejecting non-existent record raises error."""
    reviewer_id = uuid.uuid4()
    non_existent_id = uuid.uuid4()

    with pytest.raises(ValueError, match="Building not found"):
        await reject_record(
            db=async_db_session,
            record_id=non_existent_id,
            entity_type="building",
            reviewer_id=reviewer_id,
            rejection_reason="Test reason",
        )


@pytest.mark.asyncio
async def test_reject_record_strips_whitespace(async_db_session: AsyncSession):
    """Test that rejection reason is stripped of leading/trailing whitespace."""
    suffix = uuid.uuid4().hex[:8]
    enumerator, reviewer = _make_users(suffix)
    async_db_session.add_all([enumerator, reviewer])
    await async_db_session.flush()

    street = _make_street(suffix, enumerator.id)
    async_db_session.add(street)
    await async_db_session.flush()

    building = _make_building(suffix, street.street_id, enumerator.id)
    async_db_session.add(building)
    await async_db_session.commit()

    await reject_record(
        db=async_db_session,
        record_id=building.id,
        entity_type="building",
        reviewer_id=reviewer.id,
        rejection_reason="  GPS accuracy is too low  ",
    )

    result = await async_db_session.execute(select(Building).where(Building.id == building.id))
    updated = result.scalar_one()

    assert updated.rejection_reason == "GPS accuracy is too low"

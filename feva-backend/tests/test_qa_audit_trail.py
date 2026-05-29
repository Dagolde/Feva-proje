"""Tests for QA audit trail retrieval.

Requirements: 14.1, 14.2, 14.3, 14.4
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.building import Building
from app.models.user import User
from app.services.qa_service import get_audit_trail


@pytest.fixture
async def test_building(db: AsyncSession, enumerator_user: User):
    """Create a test building for audit trail tests."""
    point = Point(3.3792, 6.5244)  # Lagos coordinates
    wkb_geom = from_shape(point, srid=4326)
    
    building = Building(
        building_id="TEST-BLD-001",
        street_id="TEST-STR-001",
        building_type="residential",
        number_of_floors=2,
        number_of_units=4,
        building_condition="good",
        has_signage=True,
        lga="Lagos",
        ward="Ward 1",
        enumerator_id=enumerator_user.id,
        geom=wkb_geom,
        gps_accuracy_m=5.0,
        verification_status="pending",
        enumeration_date=datetime.now(timezone.utc),
    )
    db.add(building)
    await db.commit()
    await db.refresh(building)
    return building


@pytest.mark.asyncio
async def test_get_audit_trail_returns_entries_for_record(
    db: AsyncSession,
    qa_user: User,
    test_building: Building,
):
    """Test that get_audit_trail returns all audit entries for a specific record.
    
    Requirements: 14.1, 14.3
    """
    # Create audit log entries for the building
    audit1 = AuditLog(
        user_id=qa_user.id,
        operation="approve_record",
        entity_type="building",
        entity_id=str(test_building.id),
    )
    db.add(audit1)
    
    audit2 = AuditLog(
        user_id=qa_user.id,
        operation="reject_record",
        entity_type="building",
        entity_id=str(test_building.id),
        detail={"reason": "Missing information"},
    )
    db.add(audit2)
    
    await db.commit()
    
    # Get audit trail
    trail = await get_audit_trail(db, test_building.id, "building")
    
    # Verify we got both entries
    assert len(trail) == 2
    
    # Verify entries contain required fields
    for entry in trail:
        assert "timestamp" in entry
        assert "user" in entry
        assert "action" in entry
        assert "detail" in entry


@pytest.mark.asyncio
async def test_get_audit_trail_includes_required_fields(
    db: AsyncSession,
    qa_user: User,
    test_building: Building,
):
    """Test that audit entries include timestamp, user, action, and detail fields.
    
    Requirements: 14.2
    """
    # Create an audit log entry
    audit = AuditLog(
        user_id=qa_user.id,
        operation="approve_record",
        entity_type="building",
        entity_id=str(test_building.id),
        detail={"test": "data"},
    )
    db.add(audit)
    await db.commit()
    
    # Get audit trail
    trail = await get_audit_trail(db, test_building.id, "building")
    
    # Verify entry has all required fields
    assert len(trail) == 1
    entry = trail[0]
    
    assert entry["timestamp"] is not None
    assert entry["user"] == qa_user.username
    assert entry["action"] == "approve_record"
    assert entry["detail"] == {"test": "data"}


@pytest.mark.asyncio
async def test_get_audit_trail_sorted_chronologically_descending(
    db: AsyncSession,
    qa_user: User,
    test_building: Building,
):
    """Test that audit trail is sorted chronologically descending (newest first).
    
    Requirements: 14.4
    """
    # Create audit log entries with different timestamps
    # Note: We rely on the database's server_default=func.now() for timestamps
    audit1 = AuditLog(
        user_id=qa_user.id,
        operation="create_record",
        entity_type="building",
        entity_id=str(test_building.id),
    )
    db.add(audit1)
    await db.flush()
    
    audit2 = AuditLog(
        user_id=qa_user.id,
        operation="approve_record",
        entity_type="building",
        entity_id=str(test_building.id),
    )
    db.add(audit2)
    await db.flush()
    
    audit3 = AuditLog(
        user_id=qa_user.id,
        operation="reject_record",
        entity_type="building",
        entity_id=str(test_building.id),
    )
    db.add(audit3)
    await db.commit()
    
    # Get audit trail
    trail = await get_audit_trail(db, test_building.id, "building")
    
    # Verify entries are sorted newest first
    assert len(trail) == 3
    assert trail[0]["action"] == "reject_record"  # Most recent
    assert trail[1]["action"] == "approve_record"  # Middle
    assert trail[2]["action"] == "create_record"  # Oldest


@pytest.mark.asyncio
async def test_get_audit_trail_returns_empty_for_no_entries(
    db: AsyncSession,
    test_building: Building,
):
    """Test that get_audit_trail returns empty list when no audit entries exist."""
    # Get audit trail for a building with no audit entries
    trail = await get_audit_trail(db, test_building.id, "building")
    
    # Verify empty list is returned
    assert trail == []


@pytest.mark.asyncio
async def test_get_audit_trail_filters_by_entity_type(
    db: AsyncSession,
    qa_user: User,
    test_building: Building,
):
    """Test that get_audit_trail only returns entries for the specified entity type."""
    # Create audit entries for different entity types with same ID
    audit_building = AuditLog(
        user_id=qa_user.id,
        operation="approve_record",
        entity_type="building",
        entity_id=str(test_building.id),
    )
    db.add(audit_building)
    
    audit_street = AuditLog(
        user_id=qa_user.id,
        operation="approve_record",
        entity_type="street",
        entity_id=str(test_building.id),  # Same ID but different entity type
    )
    db.add(audit_street)
    
    await db.commit()
    
    # Get audit trail for building
    trail = await get_audit_trail(db, test_building.id, "building")
    
    # Verify only building entry is returned
    assert len(trail) == 1
    assert trail[0]["action"] == "approve_record"


@pytest.mark.asyncio
async def test_get_audit_trail_handles_system_user(
    db: AsyncSession,
    test_building: Building,
):
    """Test that get_audit_trail handles entries with no user_id (system actions)."""
    # Create audit entry with no user_id
    audit = AuditLog(
        user_id=None,
        operation="system_action",
        entity_type="building",
        entity_id=str(test_building.id),
    )
    db.add(audit)
    await db.commit()
    
    # Get audit trail
    trail = await get_audit_trail(db, test_building.id, "building")
    
    # Verify system user is returned
    assert len(trail) == 1
    assert trail[0]["user"] == "system"
    assert trail[0]["action"] == "system_action"

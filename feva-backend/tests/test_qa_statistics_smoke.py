"""Smoke test for QA statistics calculation.

Simple test to verify the get_statistics() function works correctly.

Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6
"""
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry import Point, LineString
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building
from app.models.street import Street
from app.models.user import User
from app.services.qa_service import get_statistics, StatisticsFilters


@pytest.mark.asyncio
async def test_get_statistics_smoke(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Smoke test for get_statistics function."""
    now = datetime.now(timezone.utc)
    
    # Create a few test records
    building1 = Building(
        building_id=f"BLD-SMOKE-{uuid.uuid4().hex[:8]}",
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
        enumeration_date=now,
        verification_status="pending",
    )
    async_db_session.add(building1)
    
    building2 = Building(
        building_id=f"BLD-SMOKE-{uuid.uuid4().hex[:8]}",
        street_id="STR-TEST-001",
        building_type="commercial",
        number_of_floors=3,
        number_of_units=6,
        building_condition="excellent",
        has_signage=True,
        geom=from_shape(Point(3.3793, 6.5245), srid=4326),
        gps_accuracy_m=Decimal("4.5"),
        lga="Lagos",
        enumerator_id=admin_user.id,
        enumeration_date=now,
        verification_status="approved",
        reviewed_by=qa_user.id,
        reviewed_at=now + timedelta(hours=2),
    )
    async_db_session.add(building2)
    
    street1 = Street(
        street_id=f"STR-SMOKE-{uuid.uuid4().hex[:8]}",
        street_name="Test Street",
        street_type="residential",
        surface_type="paved",
        street_condition="good",
        geom=from_shape(LineString([(3.3792, 6.5244), (3.3793, 6.5245)]), srid=4326),
        lga="Lagos",
        enumerator_id=admin_user.id,
        enumeration_date=now,
        verification_status="rejected",
        reviewed_by=qa_user.id,
        reviewed_at=now + timedelta(hours=1),
        rejection_reason="Poor quality",
    )
    async_db_session.add(street1)
    
    await async_db_session.commit()
    
    # Get statistics
    stats = await get_statistics(db=async_db_session)
    
    # Verify basic structure
    assert stats.total_records >= 3
    assert stats.pending_records >= 1
    assert stats.approved_records >= 1
    assert stats.rejected_records >= 1
    assert isinstance(stats.approval_rate_by_enumerator, dict)
    assert isinstance(stats.daily_volumes, list)
    
    # Verify approval rate is calculated
    if admin_user.username in stats.approval_rate_by_enumerator:
        rate = stats.approval_rate_by_enumerator[admin_user.username]
        assert 0.0 <= rate <= 1.0
    
    # Verify average review time is calculated or None
    if stats.average_review_time_seconds is not None:
        assert stats.average_review_time_seconds > 0
    
    print(f"✓ Statistics calculated successfully:")
    print(f"  Total records: {stats.total_records}")
    print(f"  Pending: {stats.pending_records}")
    print(f"  Approved: {stats.approved_records}")
    print(f"  Rejected: {stats.rejected_records}")
    print(f"  Approval rates: {stats.approval_rate_by_enumerator}")
    print(f"  Avg review time: {stats.average_review_time_seconds}")
    print(f"  Daily volumes: {len(stats.daily_volumes)} days")


@pytest.mark.asyncio
async def test_get_statistics_with_lga_filter(async_db_session: AsyncSession, admin_user: User):
    """Test statistics with LGA filter."""
    now = datetime.now(timezone.utc)
    
    # Create a building in a specific LGA
    building = Building(
        building_id=f"BLD-FILTER-{uuid.uuid4().hex[:8]}",
        street_id="STR-TEST-001",
        building_type="residential",
        number_of_floors=2,
        number_of_units=4,
        building_condition="good",
        has_signage=False,
        geom=from_shape(Point(3.3792, 6.5244), srid=4326),
        gps_accuracy_m=Decimal("5.0"),
        lga="TestLGA",
        enumerator_id=admin_user.id,
        enumeration_date=now,
        verification_status="pending",
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Get statistics filtered by LGA
    filters = StatisticsFilters(lga="TestLGA")
    stats = await get_statistics(db=async_db_session, filters=filters)
    
    # Should include at least our test record
    assert stats.total_records >= 1
    
    print(f"✓ LGA filter works: {stats.total_records} records in TestLGA")


@pytest.mark.asyncio
async def test_get_statistics_empty_database(async_db_session: AsyncSession):
    """Test statistics when filtering returns no records."""
    # Get statistics with filter that matches nothing
    filters = StatisticsFilters(lga="NonexistentLGA123456")
    stats = await get_statistics(db=async_db_session, filters=filters)
    
    # All counts should be zero
    assert stats.total_records == 0
    assert stats.pending_records == 0
    assert stats.approved_records == 0
    assert stats.rejected_records == 0
    assert len(stats.approval_rate_by_enumerator) == 0
    assert stats.average_review_time_seconds is None
    assert len(stats.daily_volumes) == 0
    
    print("✓ Empty result handling works correctly")

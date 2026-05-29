"""Unit tests for QA statistics calculation.

Tests the get_statistics() function in QAService to ensure:
- Total, pending, approved, rejected record counts are accurate
- Approval rate by enumerator is calculated correctly
- Average review time is calculated correctly
- Daily submission and review volumes are generated correctly
- Filtering by LGA, ward, and date range works correctly
- Handles cases where no records match filters

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
async def test_get_statistics_basic_counts(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test basic record counts in statistics."""
    now = datetime.now(timezone.utc)
    
    # Create test records with different statuses
    # 2 pending buildings
    for i in range(2):
        building = Building(
            building_id=f"BLD-PENDING-{i}",
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
        async_db_session.add(building)
    
    # 3 approved buildings
    for i in range(3):
        building = Building(
            building_id=f"BLD-APPROVED-{i}",
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
        async_db_session.add(building)
    
    # 1 rejected building
    building = Building(
        building_id="BLD-REJECTED-0",
        street_id="STR-TEST-001",
        building_type="industrial",
        number_of_floors=1,
        number_of_units=1,
        building_condition="poor",
        has_signage=False,
        geom=from_shape(Point(3.3794, 6.5246), srid=4326),
        gps_accuracy_m=Decimal("6.0"),
        lga="Lagos",
        enumerator_id=admin_user.id,
        enumeration_date=now,
        verification_status="rejected",
        reviewed_by=qa_user.id,
        reviewed_at=now + timedelta(hours=1),
        rejection_reason="Poor quality",
    )
    async_db_session.add(building)
    
    # 1 pending street
    street = Street(
        street_id="STR-PENDING-0",
        street_name="Pending Street",
        street_type="residential",
        surface_type="paved",
        street_condition="good",
        geom=from_shape(LineString([(3.3792, 6.5244), (3.3793, 6.5245)]), srid=4326),
        lga="Lagos",
        enumerator_id=admin_user.id,
        enumeration_date=now,
        verification_status="pending",
    )
    async_db_session.add(street)
    
    # 2 approved streets
    for i in range(2):
        street = Street(
            street_id=f"STR-APPROVED-{i}",
            street_name=f"Approved Street {i}",
            street_type="commercial",
            surface_type="paved",
            street_condition="excellent",
            geom=from_shape(LineString([(3.3792 + i*0.001, 6.5244), (3.3793 + i*0.001, 6.5245)]), srid=4326),
            lga="Lagos",
            enumerator_id=admin_user.id,
            enumeration_date=now,
            verification_status="approved",
            reviewed_by=qa_user.id,
            reviewed_at=now + timedelta(hours=3),
        )
        async_db_session.add(street)
    
    await async_db_session.commit()
    
    # Get statistics
    stats = await get_statistics(db=async_db_session)
    
    # Verify counts
    assert stats.total_records == 9  # 6 buildings + 3 streets
    assert stats.pending_records == 3  # 2 buildings + 1 street
    assert stats.approved_records == 5  # 3 buildings + 2 streets
    assert stats.rejected_records == 1  # 1 building


@pytest.mark.asyncio
async def test_get_statistics_approval_rate_by_enumerator(async_db_session: AsyncSession, admin_user: User, qa_user: User, enumerator_user: User):
    """Test approval rate calculation by enumerator."""
    now = datetime.now(timezone.utc)
    
    # Admin user: 3 approved, 1 rejected = 75% approval rate
    for i in range(3):
        building = Building(
            building_id=f"BLD-ADMIN-APPROVED-{i}",
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
            verification_status="approved",
            reviewed_by=qa_user.id,
            reviewed_at=now + timedelta(hours=1),
        )
        async_db_session.add(building)
    
    building = Building(
        building_id="BLD-ADMIN-REJECTED-0",
        street_id="STR-TEST-001",
        building_type="commercial",
        number_of_floors=3,
        number_of_units=6,
        building_condition="poor",
        has_signage=False,
        geom=from_shape(Point(3.3793, 6.5245), srid=4326),
        gps_accuracy_m=Decimal("5.5"),
        lga="Lagos",
        enumerator_id=admin_user.id,
        enumeration_date=now,
        verification_status="rejected",
        reviewed_by=qa_user.id,
        reviewed_at=now + timedelta(hours=1),
        rejection_reason="Poor quality",
    )
    async_db_session.add(building)
    
    # Enumerator user: 1 approved, 1 rejected = 50% approval rate
    building = Building(
        building_id="BLD-ENUM-APPROVED-0",
        street_id="STR-TEST-001",
        building_type="residential",
        number_of_floors=2,
        number_of_units=4,
        building_condition="good",
        has_signage=False,
        geom=from_shape(Point(3.3794, 6.5246), srid=4326),
        gps_accuracy_m=Decimal("4.8"),
        lga="Lagos",
        enumerator_id=enumerator_user.id,
        enumeration_date=now,
        verification_status="approved",
        reviewed_by=qa_user.id,
        reviewed_at=now + timedelta(hours=2),
    )
    async_db_session.add(building)
    
    building = Building(
        building_id="BLD-ENUM-REJECTED-0",
        street_id="STR-TEST-001",
        building_type="industrial",
        number_of_floors=1,
        number_of_units=1,
        building_condition="poor",
        has_signage=False,
        geom=from_shape(Point(3.3795, 6.5247), srid=4326),
        gps_accuracy_m=Decimal("6.2"),
        lga="Lagos",
        enumerator_id=enumerator_user.id,
        enumeration_date=now,
        verification_status="rejected",
        reviewed_by=qa_user.id,
        reviewed_at=now + timedelta(hours=2),
        rejection_reason="Incomplete data",
    )
    async_db_session.add(building)
    
    await async_db_session.commit()
    
    # Get statistics
    stats = await get_statistics(db=async_db_session)
    
    # Verify approval rates
    assert len(stats.approval_rate_by_enumerator) == 2
    assert stats.approval_rate_by_enumerator[admin_user.username] == 0.75  # 3/4
    assert stats.approval_rate_by_enumerator[enumerator_user.username] == 0.5  # 1/2


@pytest.mark.asyncio
async def test_get_statistics_average_review_time(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test average review time calculation."""
    now = datetime.now(timezone.utc)
    
    # Building reviewed after 2 hours (7200 seconds)
    building1 = Building(
        building_id="BLD-REVIEW-1",
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
        verification_status="approved",
        reviewed_by=qa_user.id,
        reviewed_at=now + timedelta(hours=2),
    )
    async_db_session.add(building1)
    
    # Building reviewed after 4 hours (14400 seconds)
    building2 = Building(
        building_id="BLD-REVIEW-2",
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
        verification_status="rejected",
        reviewed_by=qa_user.id,
        reviewed_at=now + timedelta(hours=4),
        rejection_reason="Issues found",
    )
    async_db_session.add(building2)
    
    # Street reviewed after 3 hours (10800 seconds)
    street = Street(
        street_id="STR-REVIEW-1",
        street_name="Review Street",
        street_type="residential",
        surface_type="paved",
        street_condition="good",
        geom=from_shape(LineString([(3.3792, 6.5244), (3.3793, 6.5245)]), srid=4326),
        lga="Lagos",
        enumerator_id=admin_user.id,
        enumeration_date=now,
        verification_status="approved",
        reviewed_by=qa_user.id,
        reviewed_at=now + timedelta(hours=3),
    )
    async_db_session.add(street)
    
    # Pending building (should not be included in average)
    building3 = Building(
        building_id="BLD-PENDING-1",
        street_id="STR-TEST-001",
        building_type="residential",
        number_of_floors=2,
        number_of_units=4,
        building_condition="good",
        has_signage=False,
        geom=from_shape(Point(3.3794, 6.5246), srid=4326),
        gps_accuracy_m=Decimal("5.2"),
        lga="Lagos",
        enumerator_id=admin_user.id,
        enumeration_date=now,
        verification_status="pending",
    )
    async_db_session.add(building3)
    
    await async_db_session.commit()
    
    # Get statistics
    stats = await get_statistics(db=async_db_session)
    
    # Average should be (7200 + 14400 + 10800) / 3 = 10800 seconds (3 hours)
    assert stats.average_review_time_seconds is not None
    assert abs(stats.average_review_time_seconds - 10800.0) < 1.0  # Allow small floating point difference


@pytest.mark.asyncio
async def test_get_statistics_daily_volumes(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test daily submission and review volume calculation."""
    base_date = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    # Day 1: 2 submissions, 0 reviews
    for i in range(2):
        building = Building(
            building_id=f"BLD-DAY1-{i}",
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
            enumeration_date=base_date,
            verification_status="pending",
        )
        async_db_session.add(building)
    
    # Day 2: 3 submissions, 2 reviews (from day 1 submissions)
    day2 = base_date + timedelta(days=1)
    for i in range(3):
        building = Building(
            building_id=f"BLD-DAY2-{i}",
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
            enumeration_date=day2,
            verification_status="pending" if i == 2 else "approved",
            reviewed_by=qa_user.id if i < 2 else None,
            reviewed_at=day2 if i < 2 else None,
        )
        async_db_session.add(building)
    
    # Day 3: 1 submission, 1 review
    day3 = base_date + timedelta(days=2)
    building = Building(
        building_id="BLD-DAY3-0",
        street_id="STR-TEST-001",
        building_type="industrial",
        number_of_floors=1,
        number_of_units=1,
        building_condition="good",
        has_signage=False,
        geom=from_shape(Point(3.3794, 6.5246), srid=4326),
        gps_accuracy_m=Decimal("5.5"),
        lga="Lagos",
        enumerator_id=admin_user.id,
        enumeration_date=day3,
        verification_status="approved",
        reviewed_by=qa_user.id,
        reviewed_at=day3,
    )
    async_db_session.add(building)
    
    await async_db_session.commit()
    
    # Get statistics
    stats = await get_statistics(db=async_db_session)
    
    # Verify daily volumes
    assert len(stats.daily_volumes) == 3
    
    # Day 1
    day1_data = next(d for d in stats.daily_volumes if d["date"] == "2024-01-01")
    assert day1_data["submitted"] == 2
    assert day1_data["reviewed"] == 0
    
    # Day 2
    day2_data = next(d for d in stats.daily_volumes if d["date"] == "2024-01-02")
    assert day2_data["submitted"] == 3
    assert day2_data["reviewed"] == 2
    
    # Day 3
    day3_data = next(d for d in stats.daily_volumes if d["date"] == "2024-01-03")
    assert day3_data["submitted"] == 1
    assert day3_data["reviewed"] == 1


@pytest.mark.asyncio
async def test_get_statistics_filter_by_lga(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test filtering statistics by LGA."""
    now = datetime.now(timezone.utc)
    
    # Create records in Lagos
    for i in range(3):
        building = Building(
            building_id=f"BLD-LAGOS-{i}",
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
            verification_status="approved",
            reviewed_by=qa_user.id,
            reviewed_at=now + timedelta(hours=1),
        )
        async_db_session.add(building)
    
    # Create records in Abuja
    for i in range(2):
        building = Building(
            building_id=f"BLD-ABUJA-{i}",
            street_id="STR-TEST-001",
            building_type="commercial",
            number_of_floors=3,
            number_of_units=6,
            building_condition="excellent",
            has_signage=True,
            geom=from_shape(Point(3.3793, 6.5245), srid=4326),
            gps_accuracy_m=Decimal("4.5"),
            lga="Abuja",
            enumerator_id=admin_user.id,
            enumeration_date=now,
            verification_status="pending",
        )
        async_db_session.add(building)
    
    await async_db_session.commit()
    
    # Get statistics filtered by Lagos
    filters = StatisticsFilters(lga="Lagos")
    stats = await get_statistics(db=async_db_session, filters=filters)
    
    # Should only include Lagos records
    assert stats.total_records == 3
    assert stats.approved_records == 3
    assert stats.pending_records == 0


@pytest.mark.asyncio
async def test_get_statistics_filter_by_ward(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test filtering statistics by ward."""
    now = datetime.now(timezone.utc)
    
    # Create records in Ward 1
    for i in range(2):
        building = Building(
            building_id=f"BLD-WARD1-{i}",
            street_id="STR-TEST-001",
            building_type="residential",
            number_of_floors=2,
            number_of_units=4,
            building_condition="good",
            has_signage=False,
            geom=from_shape(Point(3.3792, 6.5244), srid=4326),
            gps_accuracy_m=Decimal("5.0"),
            lga="Lagos",
            ward="Ward 1",
            enumerator_id=admin_user.id,
            enumeration_date=now,
            verification_status="approved",
            reviewed_by=qa_user.id,
            reviewed_at=now + timedelta(hours=1),
        )
        async_db_session.add(building)
    
    # Create records in Ward 2
    for i in range(3):
        building = Building(
            building_id=f"BLD-WARD2-{i}",
            street_id="STR-TEST-001",
            building_type="commercial",
            number_of_floors=3,
            number_of_units=6,
            building_condition="excellent",
            has_signage=True,
            geom=from_shape(Point(3.3793, 6.5245), srid=4326),
            gps_accuracy_m=Decimal("4.5"),
            lga="Lagos",
            ward="Ward 2",
            enumerator_id=admin_user.id,
            enumeration_date=now,
            verification_status="pending",
        )
        async_db_session.add(building)
    
    await async_db_session.commit()
    
    # Get statistics filtered by Ward 1
    filters = StatisticsFilters(ward="Ward 1")
    stats = await get_statistics(db=async_db_session, filters=filters)
    
    # Should only include Ward 1 records
    assert stats.total_records == 2
    assert stats.approved_records == 2
    assert stats.pending_records == 0


@pytest.mark.asyncio
async def test_get_statistics_filter_by_date_range(async_db_session: AsyncSession, admin_user: User, qa_user: User):
    """Test filtering statistics by date range."""
    base_date = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    # Records on Jan 1
    for i in range(2):
        building = Building(
            building_id=f"BLD-JAN1-{i}",
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
            enumeration_date=base_date,
            verification_status="approved",
            reviewed_by=qa_user.id,
            reviewed_at=base_date + timedelta(hours=1),
        )
        async_db_session.add(building)
    
    # Records on Jan 5
    for i in range(3):
        building = Building(
            building_id=f"BLD-JAN5-{i}",
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
            enumeration_date=base_date + timedelta(days=4),
            verification_status="pending",
        )
        async_db_session.add(building)
    
    # Records on Jan 10
    building = Building(
        building_id="BLD-JAN10-0",
        street_id="STR-TEST-001",
        building_type="industrial",
        number_of_floors=1,
        number_of_units=1,
        building_condition="good",
        has_signage=False,
        geom=from_shape(Point(3.3794, 6.5246), srid=4326),
        gps_accuracy_m=Decimal("5.5"),
        lga="Lagos",
        enumerator_id=admin_user.id,
        enumeration_date=base_date + timedelta(days=9),
        verification_status="rejected",
        reviewed_by=qa_user.id,
        reviewed_at=base_date + timedelta(days=9, hours=2),
        rejection_reason="Poor quality",
    )
    async_db_session.add(building)
    
    await async_db_session.commit()
    
    # Get statistics for Jan 1-6 (should include Jan 1 and Jan 5 records)
    filters = StatisticsFilters(
        start_date=base_date,
        end_date=base_date + timedelta(days=6)
    )
    stats = await get_statistics(db=async_db_session, filters=filters)
    
    # Should include 5 records (2 from Jan 1, 3 from Jan 5)
    assert stats.total_records == 5
    assert stats.approved_records == 2
    assert stats.pending_records == 3
    assert stats.rejected_records == 0


@pytest.mark.asyncio
async def test_get_statistics_no_matching_records(async_db_session: AsyncSession):
    """Test statistics when no records match filters."""
    # Get statistics with filter that matches nothing
    filters = StatisticsFilters(lga="NonexistentLGA")
    stats = await get_statistics(db=async_db_session, filters=filters)
    
    # All counts should be zero
    assert stats.total_records == 0
    assert stats.pending_records == 0
    assert stats.approved_records == 0
    assert stats.rejected_records == 0
    assert len(stats.approval_rate_by_enumerator) == 0
    assert stats.average_review_time_seconds is None
    assert len(stats.daily_volumes) == 0


@pytest.mark.asyncio
async def test_get_statistics_no_reviewed_records(async_db_session: AsyncSession, admin_user: User):
    """Test statistics when there are no reviewed records (average review time should be None)."""
    now = datetime.now(timezone.utc)
    
    # Create only pending records
    for i in range(3):
        building = Building(
            building_id=f"BLD-PENDING-{i}",
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
        async_db_session.add(building)
    
    await async_db_session.commit()
    
    # Get statistics
    stats = await get_statistics(db=async_db_session)
    
    # Average review time should be None
    assert stats.total_records == 3
    assert stats.pending_records == 3
    assert stats.average_review_time_seconds is None
    assert len(stats.approval_rate_by_enumerator) == 0

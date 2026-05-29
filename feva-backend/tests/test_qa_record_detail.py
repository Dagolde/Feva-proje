"""Tests for QA record detail retrieval.

Tests the get_record_detail service function for fetching complete record information.
Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import from_shape
from shapely.geometry import Point, LineString
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building
from app.models.photo import Photo
from app.models.street import Street
from app.models.user import User
from app.services.qa_service import get_record_detail


@pytest.fixture
async def test_street(async_db_session: AsyncSession, admin_user: User) -> Street:
    """Get or create a test street for building FK references."""
    from sqlalchemy import select
    result = await async_db_session.execute(
        select(Street).where(Street.street_id == "STR-TEST-001")
    )
    street = result.scalar_one_or_none()
    if not street:
        street = Street(
            street_id="STR-TEST-001",
            street_name="Test Street",
            street_type="Primary",
            surface_type="Asphalt",
            street_condition="Good",
            geom=from_shape(LineString([(3.3792, 6.5244), (3.3800, 6.5250)]), srid=4326),
            lga="TestLGA",
            enumerator_id=admin_user.id,
            enumeration_date=datetime.now(timezone.utc),
            verification_status="pending",
        )
        async_db_session.add(street)
        await async_db_session.flush()
    return street


@pytest.mark.asyncio
async def test_get_building_record_detail(async_db_session: AsyncSession, admin_user: User, test_street: Street):
    """Test retrieving complete building record details."""
    # Create a building record
    building_id = str(uuid.uuid4())
    building = Building(
        building_id=f"BLD-{building_id[:8]}",
        street_id=test_street.street_id,
        building_type="Residential",
        number_of_floors=2,
        number_of_units=4,
        building_condition="Good",
        has_signage=True,
        business_names=["Test Business"],
        notes="Test building notes",
        geom=from_shape(Point(3.3792, 6.5244), srid=4326),
        gps_accuracy_m=Decimal("5.5"),
        lga="TestLGA",
        ward="TestWard",
        postcode="100001",
        postcode_status="resolved",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
        boundary_flag=False,
        gps_accuracy_flag=False,
        duplicate_flag=False,
        qa_flags={"GPS_LOW_ACCURACY": {"accuracy_m": 5.5}},
    )
    async_db_session.add(building)
    await async_db_session.flush()
    
    # Create associated photos
    photo1 = Photo(
        photo_id=f"PHT-{uuid.uuid4()}",
        record_type="building",
        record_id=building.id,
        storage_path="/photos/test1.jpg",
        is_frontage=True,
        captured_at=datetime.now(timezone.utc),
    )
    photo2 = Photo(
        photo_id=f"PHT-{uuid.uuid4()}",
        record_type="building",
        record_id=building.id,
        storage_path="/photos/test2.jpg",
        is_frontage=False,
        captured_at=datetime.now(timezone.utc),
    )
    async_db_session.add(photo1)
    async_db_session.add(photo2)
    await async_db_session.commit()
    
    # Retrieve record detail
    detail = await get_record_detail(async_db_session, building.id, "building")
    
    # Verify all required fields are present
    assert detail.id == building.id
    assert detail.entity_type == "building"
    assert detail.status == "pending"
    assert detail.enumerator.id == admin_user.id
    assert detail.reviewed_by is None
    assert detail.reviewed_at is None
    assert detail.rejection_reason is None
    
    # Verify data dictionary contains all form fields
    assert detail.data["building_id"] == building.building_id
    assert detail.data["street_id"] == test_street.street_id
    assert detail.data["building_type"] == "Residential"
    assert detail.data["number_of_floors"] == 2
    assert detail.data["number_of_units"] == 4
    assert detail.data["building_condition"] == "Good"
    assert detail.data["has_signage"] is True
    assert detail.data["business_names"] == ["Test Business"]
    assert detail.data["notes"] == "Test building notes"
    assert detail.data["lga"] == "TestLGA"
    assert detail.data["ward"] == "TestWard"
    assert detail.data["postcode"] == "100001"
    assert detail.data["postcode_status"] == "resolved"
    assert detail.data["gps_accuracy_m"] == 5.5
    assert detail.data["boundary_flag"] is False
    assert detail.data["duplicate_flag"] is False
    assert detail.data["qa_flags"] == {"GPS_LOW_ACCURACY": {"accuracy_m": 5.5}}
    
    # Verify GPS coordinates are included in geometry
    assert detail.geometry["type"] == "Point"
    assert len(detail.geometry["coordinates"]) == 2
    assert isinstance(detail.geometry["coordinates"][0], float)
    assert isinstance(detail.geometry["coordinates"][1], float)
    
    # Verify photos are included
    assert len(detail.photos) == 2
    photo_ids = {p.photo_id for p in detail.photos}
    assert photo1.photo_id in photo_ids
    assert photo2.photo_id in photo_ids


@pytest.mark.asyncio
async def test_get_street_record_detail(async_db_session: AsyncSession, admin_user: User):
    """Test retrieving complete street record details."""
    # Create a street record
    street_id = str(uuid.uuid4())
    street = Street(
        street_id=f"STR-{street_id[:8]}",
        street_name="Test Street",
        street_type="Primary",
        surface_type="Asphalt",
        street_condition="Good",
        notes="Test street notes",
        geom=from_shape(LineString([(3.3792, 6.5244), (3.3800, 6.5250)]), srid=4326),
        lga="TestLGA",
        ward="TestWard",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
        boundary_flag=False,
        gps_accuracy_flag=False,
        qa_flags={},
    )
    async_db_session.add(street)
    await async_db_session.flush()
    
    # Create associated photo
    photo = Photo(
        photo_id=f"PHT-{uuid.uuid4()}",
        record_type="street",
        record_id=street.id,
        storage_path="/photos/street1.jpg",
        is_frontage=False,
        captured_at=datetime.now(timezone.utc),
    )
    async_db_session.add(photo)
    await async_db_session.commit()
    
    # Retrieve record detail
    detail = await get_record_detail(async_db_session, street.id, "street")
    
    # Verify all required fields are present
    assert detail.id == street.id
    assert detail.entity_type == "street"
    assert detail.status == "pending"
    assert detail.enumerator.id == admin_user.id
    assert detail.reviewed_by is None
    assert detail.reviewed_at is None
    assert detail.rejection_reason is None
    
    # Verify data dictionary contains all form fields
    assert detail.data["street_id"] == street.street_id
    assert detail.data["street_name"] == "Test Street"
    assert detail.data["street_type"] == "Primary"
    assert detail.data["surface_type"] == "Asphalt"
    assert detail.data["street_condition"] == "Good"
    assert detail.data["notes"] == "Test street notes"
    assert detail.data["lga"] == "TestLGA"
    assert detail.data["ward"] == "TestWard"
    assert detail.data["boundary_flag"] is False
    assert detail.data["qa_flags"] == {}
    
    # Verify geometry is LineString
    assert detail.geometry["type"] == "LineString"
    assert len(detail.geometry["coordinates"]) == 2
    assert len(detail.geometry["coordinates"][0]) == 2
    
    # Verify photo is included
    assert len(detail.photos) == 1
    assert detail.photos[0].photo_id == photo.photo_id


@pytest.mark.asyncio
async def test_get_record_detail_with_reviewer(async_db_session: AsyncSession, admin_user: User, qa_user: User, test_street: Street):
    """Test retrieving record detail that has been reviewed."""
    # Create a reviewed building record
    building = Building(
        building_id=f"BLD-{uuid.uuid4()}",
        street_id=test_street.street_id,
        building_type="Commercial",
        number_of_floors=1,
        number_of_units=1,
        building_condition="Fair",
        has_signage=False,
        geom=from_shape(Point(3.3792, 6.5244), srid=4326),
        gps_accuracy_m=Decimal("3.2"),
        lga="TestLGA",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="rejected",
        reviewed_by=qa_user.id,
        reviewed_at=datetime.now(timezone.utc),
        rejection_reason="Incomplete information",
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Retrieve record detail
    detail = await get_record_detail(async_db_session, building.id, "building")
    
    # Verify reviewer information is included
    assert detail.reviewed_by is not None
    assert detail.reviewed_by.id == qa_user.id
    assert detail.reviewed_at is not None
    assert detail.rejection_reason == "Incomplete information"
    assert detail.status == "rejected"


@pytest.mark.asyncio
async def test_get_record_detail_building_not_found(async_db_session: AsyncSession):
    """Test that ValueError is raised when building record is not found."""
    non_existent_id = uuid.uuid4()
    
    with pytest.raises(ValueError, match="Building not found"):
        await get_record_detail(async_db_session, non_existent_id, "building")


@pytest.mark.asyncio
async def test_get_record_detail_street_not_found(async_db_session: AsyncSession):
    """Test that ValueError is raised when street record is not found."""
    non_existent_id = uuid.uuid4()
    
    with pytest.raises(ValueError, match="Street not found"):
        await get_record_detail(async_db_session, non_existent_id, "street")


@pytest.mark.asyncio
async def test_get_record_detail_invalid_entity_type(async_db_session: AsyncSession):
    """Test that ValueError is raised for invalid entity_type."""
    record_id = uuid.uuid4()
    
    with pytest.raises(ValueError, match="Invalid entity_type"):
        await get_record_detail(async_db_session, record_id, "invalid_type")


@pytest.mark.asyncio
async def test_get_record_detail_no_photos(async_db_session: AsyncSession, admin_user: User, test_street: Street):
    """Test retrieving record detail when no photos are associated."""
    # Create a building without photos
    building = Building(
        building_id=f"BLD-{uuid.uuid4()}",
        street_id=test_street.street_id,
        building_type="Residential",
        number_of_floors=1,
        number_of_units=2,
        building_condition="Good",
        has_signage=False,
        geom=from_shape(Point(3.3792, 6.5244), srid=4326),
        gps_accuracy_m=Decimal("4.0"),
        lga="TestLGA",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Retrieve record detail
    detail = await get_record_detail(async_db_session, building.id, "building")
    
    # Verify photos list is empty
    assert len(detail.photos) == 0
    assert detail.photos == []

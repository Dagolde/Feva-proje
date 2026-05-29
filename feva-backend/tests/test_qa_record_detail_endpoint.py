"""Tests for QA record detail API endpoint.

Tests the GET /api/v1/qa/records/{id} endpoint for fetching complete record information.
Requirements: 19.2, 19.7
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from geoalchemy2.shape import from_shape
from httpx import AsyncClient
from shapely.geometry import Point, LineString
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building
from app.models.photo import Photo
from app.models.street import Street
from app.models.user import User


@pytest.mark.asyncio
async def test_get_building_record_detail_endpoint(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test GET /api/v1/qa/records/{id} endpoint for building records."""
    # Create a building record
    building = Building(
        building_id=f"BLD-{uuid.uuid4()}",
        street_id="STR-TEST-001",
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
    
    # Create associated photo
    photo = Photo(
        photo_id=f"PHT-{uuid.uuid4()}",
        record_type="building",
        record_id=building.id,
        storage_path="/photos/test1.jpg",
        is_frontage=True,
        captured_at=datetime.now(timezone.utc),
    )
    async_db_session.add(photo)
    await async_db_session.commit()
    
    # Make request to endpoint
    response = await async_client.get(
        f"/api/v1/qa/records/{building.id}",
        params={"entity_type": "building"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    # Verify all required fields are present
    assert data["id"] == str(building.id)
    assert data["entity_type"] == "building"
    assert data["status"] == "pending"
    assert data["enumerator"]["id"] == str(admin_user.id)
    assert data["enumerator"]["username"] == admin_user.username
    assert data["reviewed_by"] is None
    assert data["reviewed_at"] is None
    assert data["rejection_reason"] is None
    
    # Verify data dictionary contains all form fields
    assert data["data"]["building_id"] == building.building_id
    assert data["data"]["street_id"] == "STR-TEST-001"
    assert data["data"]["building_type"] == "Residential"
    assert data["data"]["number_of_floors"] == 2
    assert data["data"]["number_of_units"] == 4
    assert data["data"]["lga"] == "TestLGA"
    assert data["data"]["ward"] == "TestWard"
    
    # Verify geometry
    assert data["geometry"]["type"] == "Point"
    assert len(data["geometry"]["coordinates"]) == 2
    
    # Verify photos
    assert len(data["photos"]) == 1
    assert data["photos"][0]["id"] == str(photo.id)
    assert data["photos"][0]["storage_path"] == "/photos/test1.jpg"


@pytest.mark.asyncio
async def test_get_street_record_detail_endpoint(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test GET /api/v1/qa/records/{id} endpoint for street records."""
    # Create a street record
    street = Street(
        street_id=f"STR-{uuid.uuid4()}",
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
    await async_db_session.commit()
    
    # Make request to endpoint
    response = await async_client.get(
        f"/api/v1/qa/records/{street.id}",
        params={"entity_type": "street"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    # Verify all required fields are present
    assert data["id"] == str(street.id)
    assert data["entity_type"] == "street"
    assert data["status"] == "pending"
    
    # Verify data dictionary
    assert data["data"]["street_id"] == street.street_id
    assert data["data"]["street_name"] == "Test Street"
    assert data["data"]["street_type"] == "Primary"
    
    # Verify geometry is LineString
    assert data["geometry"]["type"] == "LineString"
    assert len(data["geometry"]["coordinates"]) == 2


@pytest.mark.asyncio
async def test_get_record_detail_endpoint_missing_entity_type(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test that endpoint returns 422 when entity_type is missing."""
    record_id = uuid.uuid4()
    
    response = await async_client.get(
        f"/api/v1/qa/records/{record_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    # Should return 422 Unprocessable Entity for missing required query parameter
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_record_detail_endpoint_invalid_entity_type(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test that endpoint returns 400 for invalid entity_type."""
    record_id = uuid.uuid4()
    
    response = await async_client.get(
        f"/api/v1/qa/records/{record_id}",
        params={"entity_type": "invalid_type"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 400
    assert "entity_type must be 'building' or 'street'" in response.json()["details"]


@pytest.mark.asyncio
async def test_get_record_detail_endpoint_not_found(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test that endpoint returns 404 when record is not found."""
    non_existent_id = uuid.uuid4()
    
    response = await async_client.get(
        f"/api/v1/qa/records/{non_existent_id}",
        params={"entity_type": "building"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["details"].lower()


@pytest.mark.asyncio
async def test_get_record_detail_endpoint_invalid_uuid(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test that endpoint returns 400 for invalid UUID format."""
    response = await async_client.get(
        f"/api/v1/qa/records/not-a-uuid",
        params={"entity_type": "building"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 400
    assert "Invalid record ID format" in response.json()["details"]


@pytest.mark.asyncio
async def test_get_record_detail_endpoint_requires_auth(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
):
    """Test that endpoint requires authentication."""
    record_id = uuid.uuid4()
    
    response = await async_client.get(
        f"/api/v1/qa/records/{record_id}",
        params={"entity_type": "building"},
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_record_detail_endpoint_requires_qa_or_admin_role(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
    enumerator_user: User,
    enumerator_token: str,
):
    """Test that endpoint requires qa_officer or admin role."""
    record_id = uuid.uuid4()
    
    response = await async_client.get(
        f"/api/v1/qa/records/{record_id}",
        params={"entity_type": "building"},
        headers={"Authorization": f"Bearer {enumerator_token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_record_detail_endpoint_with_qa_user(
    async_client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    qa_user: User,
    qa_token: str,
):
    """Test that QA officer can access the endpoint."""
    # Create a building record
    building = Building(
        building_id=f"BLD-{uuid.uuid4()}",
        street_id="STR-TEST-001",
        building_type="Residential",
        number_of_floors=1,
        number_of_units=1,
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
    
    # Make request with QA user token
    response = await async_client.get(
        f"/api/v1/qa/records/{building.id}",
        params={"entity_type": "building"},
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(building.id)


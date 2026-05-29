"""Tests for Task 7.4: Export filtering and metadata inclusion.

Validates Requirements 8.5 and 8.7:
- 8.5: Filtering exports by date range, LGA, ward, and Record_Status
- 8.7: Including all metadata (GPS coordinates, photos, timestamps, enumerator info, verification status)
"""
import csv
import json
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from io import StringIO
from pathlib import Path

import pytest
from geoalchemy2.elements import WKTElement
from sqlalchemy import select

from app.models.building import Building
from app.models.export_task import ExportTask
from app.models.photo import Photo
from app.models.role import Role
from app.models.street import Street
from app.models.user import User
from app.services.export_service import (
    create_export_task,
    generate_csv_export,
    generate_geojson_export,
    get_export_status,
)


@pytest.fixture
async def enumerator_user(async_db_session):
    """Create an enumerator user."""
    from app.core.security import hash_password
    
    result = await async_db_session.execute(select(Role).where(Role.name == "enumerator"))
    role = result.scalar_one_or_none()
    
    if not role:
        role = Role(id=2, name="enumerator")
        async_db_session.add(role)
        await async_db_session.flush()
    
    user = User(
        username="enumerator_test",
        email="enum@test.com",
        password_hash=hash_password("testpass123"),
        role_id=role.id,
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    return user


@pytest.fixture
async def reviewer_user(async_db_session):
    """Create a QA reviewer user."""
    from app.core.security import hash_password
    
    result = await async_db_session.execute(select(Role).where(Role.name == "qa_officer"))
    role = result.scalar_one_or_none()
    
    if not role:
        role = Role(id=4, name="qa_officer")
        async_db_session.add(role)
        await async_db_session.flush()
    
    user = User(
        username="qa_reviewer",
        email="qa@test.com",
        password_hash=hash_password("testpass123"),
        role_id=role.id,
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    return user


@pytest.fixture
async def test_buildings_with_metadata(async_db_session, enumerator_user, reviewer_user):
    """Create test buildings with comprehensive metadata for filtering tests."""
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    two_days_ago = now - timedelta(days=2)
    
    buildings = [
        # Building 1: Lagos, Ward 1, pending, recent
        Building(
            building_id="BLD001",
            street_id="ST001",
            building_type="residential",
            number_of_floors=2,
            number_of_units=4,
            building_condition="good",
            lga="Lagos",
            ward="Ward 1",
            geom=WKTElement("POINT(3.3792 6.5244)", srid=4326),
            gps_accuracy_m=Decimal("5.0"),
            enumerator_id=enumerator_user.id,
            enumeration_date=now,
            verification_status="pending",
            has_signage=True,
            business_names=["Shop A", "Shop B"],
            notes="Test building 1",
        ),
        # Building 2: Lagos, Ward 2, approved, yesterday
        Building(
            building_id="BLD002",
            street_id="ST002",
            building_type="commercial",
            number_of_floors=3,
            number_of_units=6,
            building_condition="excellent",
            lga="Lagos",
            ward="Ward 2",
            geom=WKTElement("POINT(3.3793 6.5245)", srid=4326),
            gps_accuracy_m=Decimal("3.5"),
            enumerator_id=enumerator_user.id,
            enumeration_date=yesterday,
            verification_status="approved",
            reviewed_by=reviewer_user.id,
            reviewed_at=yesterday + timedelta(hours=2),
            has_signage=False,
            notes="Test building 2",
        ),
        # Building 3: Abuja, Ward 1, rejected, two days ago
        Building(
            building_id="BLD003",
            street_id="ST003",
            building_type="residential",
            number_of_floors=1,
            number_of_units=1,
            building_condition="poor",
            lga="Abuja",
            ward="Ward 1",
            geom=WKTElement("POINT(7.4905 9.0579)", srid=4326),
            gps_accuracy_m=Decimal("10.0"),
            enumerator_id=enumerator_user.id,
            enumeration_date=two_days_ago,
            verification_status="rejected",
            reviewed_by=reviewer_user.id,
            reviewed_at=two_days_ago + timedelta(hours=1),
            rejection_reason="Incomplete data",
            has_signage=True,
            notes="Test building 3",
        ),
    ]
    
    for building in buildings:
        async_db_session.add(building)
    
    await async_db_session.commit()
    
    for building in buildings:
        await async_db_session.refresh(building)
    
    return buildings


@pytest.mark.asyncio
async def test_csv_export_filter_by_lga(async_db_session, enumerator_user, test_buildings_with_metadata):
    """Test CSV export filtering by LGA (Requirement 8.5)."""
    # Create export task with LGA filter
    filters = {"lga": "Lagos"}
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters=filters,
        created_by=enumerator_user.id,
    )
    
    # Generate export
    await generate_csv_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters=filters,
    )
    
    # Read and verify CSV content
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    csv_content = Path(task.file_path).read_text()
    
    # Parse CSV
    reader = csv.DictReader(StringIO(csv_content))
    rows = list(reader)
    
    # Should only have Lagos buildings (BLD001, BLD002)
    assert len(rows) == 2
    assert all(row["lga"] == "Lagos" for row in rows)
    assert "BLD001" in [row["building_id"] for row in rows]
    assert "BLD002" in [row["building_id"] for row in rows]
    assert "BLD003" not in [row["building_id"] for row in rows]
    
    # Cleanup
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_csv_export_filter_by_ward(async_db_session, enumerator_user, test_buildings_with_metadata):
    """Test CSV export filtering by ward (Requirement 8.5)."""
    filters = {"ward": "Ward 1"}
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters=filters,
        created_by=enumerator_user.id,
    )
    
    await generate_csv_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters=filters,
    )
    
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    csv_content = Path(task.file_path).read_text()
    
    reader = csv.DictReader(StringIO(csv_content))
    rows = list(reader)
    
    # Should only have Ward 1 buildings (BLD001, BLD003)
    assert len(rows) == 2
    assert all(row["ward"] == "Ward 1" for row in rows)
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_csv_export_filter_by_status(async_db_session, enumerator_user, test_buildings_with_metadata):
    """Test CSV export filtering by verification status (Requirement 8.5)."""
    filters = {"status": "approved"}
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters=filters,
        created_by=enumerator_user.id,
    )
    
    await generate_csv_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters=filters,
    )
    
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    csv_content = Path(task.file_path).read_text()
    
    reader = csv.DictReader(StringIO(csv_content))
    rows = list(reader)
    
    # Should only have approved buildings (BLD002)
    assert len(rows) == 1
    assert rows[0]["verification_status"] == "approved"
    assert rows[0]["building_id"] == "BLD002"
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_csv_export_filter_by_date_range(async_db_session, enumerator_user, test_buildings_with_metadata):
    """Test CSV export filtering by date range (Requirement 8.5)."""
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    
    # Filter for records from yesterday onwards
    filters = {
        "date_from": yesterday.isoformat(),
        "date_to": now.isoformat(),
    }
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters=filters,
        created_by=enumerator_user.id,
    )
    
    await generate_csv_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters=filters,
    )
    
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    csv_content = Path(task.file_path).read_text()
    
    reader = csv.DictReader(StringIO(csv_content))
    rows = list(reader)
    
    # Should have BLD001 (today) and BLD002 (yesterday), but not BLD003 (2 days ago)
    assert len(rows) == 2
    building_ids = [row["building_id"] for row in rows]
    assert "BLD001" in building_ids
    assert "BLD002" in building_ids
    assert "BLD003" not in building_ids
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_csv_export_combined_filters(async_db_session, enumerator_user, test_buildings_with_metadata):
    """Test CSV export with multiple filters combined (Requirement 8.5)."""
    # Filter for Lagos + approved status
    filters = {"lga": "Lagos", "status": "approved"}
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters=filters,
        created_by=enumerator_user.id,
    )
    
    await generate_csv_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters=filters,
    )
    
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    csv_content = Path(task.file_path).read_text()
    
    reader = csv.DictReader(StringIO(csv_content))
    rows = list(reader)
    
    # Should only have BLD002 (Lagos + approved)
    assert len(rows) == 1
    assert rows[0]["building_id"] == "BLD002"
    assert rows[0]["lga"] == "Lagos"
    assert rows[0]["verification_status"] == "approved"
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_csv_export_includes_gps_coordinates(async_db_session, enumerator_user, test_buildings_with_metadata):
    """Test CSV export includes GPS coordinates (Requirement 8.7)."""
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters={},
        created_by=enumerator_user.id,
    )
    
    await generate_csv_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters={},
    )
    
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    csv_content = Path(task.file_path).read_text()
    
    reader = csv.DictReader(StringIO(csv_content))
    rows = list(reader)
    
    # Verify GPS metadata is present
    for row in rows:
        assert "longitude" in row
        assert "latitude" in row
        assert "gps_accuracy_m" in row
        
        # Verify values are not empty
        assert row["longitude"] != ""
        assert row["latitude"] != ""
        assert row["gps_accuracy_m"] != ""
        
        # Verify values are numeric
        float(row["longitude"])
        float(row["latitude"])
        float(row["gps_accuracy_m"])
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_csv_export_includes_timestamps(async_db_session, enumerator_user, test_buildings_with_metadata):
    """Test CSV export includes all timestamps (Requirement 8.7)."""
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters={},
        created_by=enumerator_user.id,
    )
    
    await generate_csv_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters={},
    )
    
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    csv_content = Path(task.file_path).read_text()
    
    reader = csv.DictReader(StringIO(csv_content))
    rows = list(reader)
    
    # Verify timestamp fields are present
    for row in rows:
        assert "enumeration_date" in row
        assert "created_at" in row
        assert "updated_at" in row
        assert "reviewed_at" in row
        
        # Verify enumeration_date is not empty
        assert row["enumeration_date"] != ""
        
        # Verify reviewed_at is populated for reviewed records
        if row["verification_status"] in ("approved", "rejected"):
            assert row["reviewed_at"] != ""
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_csv_export_includes_enumerator_info(async_db_session, enumerator_user, test_buildings_with_metadata):
    """Test CSV export includes enumerator information (Requirement 8.7)."""
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters={},
        created_by=enumerator_user.id,
    )
    
    await generate_csv_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters={},
    )
    
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    csv_content = Path(task.file_path).read_text()
    
    reader = csv.DictReader(StringIO(csv_content))
    rows = list(reader)
    
    # Verify enumerator information is present
    for row in rows:
        assert "enumerator_id" in row
        assert "enumerator_username" in row
        
        # Verify values are not empty
        assert row["enumerator_id"] != ""
        assert row["enumerator_username"] != ""
        
        # Verify enumerator username matches our test user
        assert row["enumerator_username"] == "enumerator_test"
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_csv_export_includes_verification_status(async_db_session, enumerator_user, test_buildings_with_metadata):
    """Test CSV export includes verification status and review info (Requirement 8.7)."""
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters={},
        created_by=enumerator_user.id,
    )
    
    await generate_csv_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters={},
    )
    
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    csv_content = Path(task.file_path).read_text()
    
    reader = csv.DictReader(StringIO(csv_content))
    rows = list(reader)
    
    # Verify verification status fields are present
    for row in rows:
        assert "verification_status" in row
        assert "reviewed_by" in row
        assert "rejection_reason" in row
        
        # Verify status values
        assert row["verification_status"] in ("pending", "approved", "rejected")
        
        # For rejected records, verify rejection reason is present
        if row["verification_status"] == "rejected":
            assert row["rejection_reason"] != ""
            assert row["reviewed_by"] != ""
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_geojson_export_filter_by_lga(async_db_session, enumerator_user, test_buildings_with_metadata):
    """Test GeoJSON export filtering by LGA (Requirement 8.5)."""
    filters = {"lga": "Lagos"}
    task_id = await create_export_task(
        db=async_db_session,
        format="geojson",
        entity_type="building",
        filters=filters,
        created_by=enumerator_user.id,
    )
    
    await generate_geojson_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters=filters,
    )
    
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    geojson_content = json.loads(Path(task.file_path).read_text())
    
    # Verify only Lagos buildings are included
    features = geojson_content["features"]
    assert len(features) == 2
    
    for feature in features:
        assert feature["properties"]["lga"] == "Lagos"
    
    building_ids = [f["properties"]["building_id"] for f in features]
    assert "BLD001" in building_ids
    assert "BLD002" in building_ids
    assert "BLD003" not in building_ids
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_geojson_export_includes_metadata(async_db_session, enumerator_user, test_buildings_with_metadata):
    """Test GeoJSON export includes all metadata (Requirement 8.7)."""
    task_id = await create_export_task(
        db=async_db_session,
        format="geojson",
        entity_type="building",
        filters={},
        created_by=enumerator_user.id,
    )
    
    await generate_geojson_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters={},
    )
    
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    geojson_content = json.loads(Path(task.file_path).read_text())
    
    features = geojson_content["features"]
    
    # Verify metadata is present in each feature
    for feature in features:
        props = feature["properties"]
        
        # GPS coordinates are in geometry
        assert feature["geometry"]["type"] == "Point"
        assert len(feature["geometry"]["coordinates"]) == 2
        
        # Enumerator info
        assert "enumerator_id" in props
        assert props["enumerator_id"] != ""
        
        # Timestamps
        assert "enumeration_date" in props
        assert props["enumeration_date"] != ""
        
        # Verification status
        assert "verification_status" in props
        assert props["verification_status"] in ("pending", "approved", "rejected")
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_street_export_filter_by_status(async_db_session, enumerator_user):
    """Test street export filtering by status (Requirement 8.5)."""
    # Create test streets with different statuses
    now = datetime.now(timezone.utc)
    
    streets = [
        Street(
            street_id="ST001",
            street_name="Pending Street",
            street_type="residential",
            surface_type="asphalt",
            street_condition="good",
            lga="Lagos",
            ward="Ward 1",
            geom=WKTElement("LINESTRING(3.3792 6.5244, 3.3793 6.5245)", srid=4326),
            enumerator_id=enumerator_user.id,
            enumeration_date=now,
            verification_status="pending",
        ),
        Street(
            street_id="ST002",
            street_name="Approved Street",
            street_type="main_road",
            surface_type="concrete",
            street_condition="excellent",
            lga="Lagos",
            ward="Ward 1",
            geom=WKTElement("LINESTRING(3.3794 6.5246, 3.3795 6.5247)", srid=4326),
            enumerator_id=enumerator_user.id,
            enumeration_date=now,
            verification_status="approved",
        ),
    ]
    
    for street in streets:
        async_db_session.add(street)
    await async_db_session.commit()
    
    # Export only approved streets
    filters = {"status": "approved"}
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="street",
        filters=filters,
        created_by=enumerator_user.id,
    )
    
    await generate_csv_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="street",
        filters=filters,
    )
    
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    csv_content = Path(task.file_path).read_text()
    
    reader = csv.DictReader(StringIO(csv_content))
    rows = list(reader)
    
    # Should only have approved street
    assert len(rows) == 1
    assert rows[0]["street_id"] == "ST002"
    assert rows[0]["verification_status"] == "approved"
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_csv_export_all_metadata_fields_present(async_db_session, enumerator_user, test_buildings_with_metadata):
    """Comprehensive test that all required metadata fields are present (Requirement 8.7)."""
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters={},
        created_by=enumerator_user.id,
    )
    
    await generate_csv_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters={},
    )
    
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    csv_content = Path(task.file_path).read_text()
    
    reader = csv.DictReader(StringIO(csv_content))
    fieldnames = reader.fieldnames
    
    # Verify all required metadata fields are present
    required_fields = [
        # GPS coordinates
        "longitude", "latitude", "gps_accuracy_m",
        # Timestamps
        "enumeration_date", "created_at", "updated_at", "reviewed_at",
        # Enumerator info
        "enumerator_id", "enumerator_username",
        # Verification status
        "verification_status", "reviewed_by", "rejection_reason",
        # Record identifiers
        "building_id", "street_id",
        # Location info
        "lga", "ward", "zone", "postcode",
        # Building details
        "building_type", "number_of_floors", "number_of_units",
        "building_condition", "has_signage", "business_names", "notes",
        # Flags
        "boundary_flag", "gps_accuracy_flag", "duplicate_flag", "qa_flags",
    ]
    
    for field in required_fields:
        assert field in fieldnames, f"Required field '{field}' missing from CSV export"
    
    Path(task.file_path).unlink()

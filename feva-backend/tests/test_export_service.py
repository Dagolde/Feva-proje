"""Tests for ExportService functionality.

Tests the new ExportService methods for Task 7.2:
- create_export_task()
- get_export_status()
- generate_csv_export()
- generate_geojson_export()
"""
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest
from geoalchemy2.elements import WKTElement
from sqlalchemy import select

from app.models.building import Building
from app.models.export_task import ExportTask
from app.models.role import Role
from app.models.street import Street
from app.models.user import User
from app.services.export_service import (
    EXPORT_DIR,
    create_export_task,
    generate_csv_export,
    generate_geojson_export,
    get_export_status,
)


@pytest.fixture
async def test_user(async_db_session):
    """Get or create a test user (enumerator)."""
    from app.core.security import hash_password

    # Get or create enumerator role
    result = await async_db_session.execute(select(Role).where(Role.name == "enumerator"))
    role = result.scalar_one_or_none()
    if not role:
        role = Role(id=2, name="enumerator")
        async_db_session.add(role)
        await async_db_session.flush()

    # Get or create enumerator user
    result = await async_db_session.execute(select(User).where(User.username == "test_enumerator"))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            username="test_enumerator",
            email="enumerator@test.com",
            password_hash=hash_password("testpass123"),
            role_id=role.id,
        )
        async_db_session.add(user)
        await async_db_session.commit()
        await async_db_session.refresh(user)
    else:
        await async_db_session.refresh(user)

    return user


@pytest.fixture
async def test_street(async_db_session, test_user):
    """Create a test street record."""
    street = Street(
        street_id="ST001",
        street_name="Test Street",
        street_type="residential",
        surface_type="asphalt",
        street_condition="good",
        lga="Lagos",
        ward="Ward 1",
        geom=WKTElement("LINESTRING(3.3792 6.5244, 3.3793 6.5245)", srid=4326),
        enumerator_id=test_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
    )
    async_db_session.add(street)
    await async_db_session.commit()
    await async_db_session.refresh(street)
    
    return street


@pytest.fixture
async def test_building(async_db_session, test_user, test_street):
    """Create a test building record."""
    building = Building(
        building_id="BLD001",
        street_id=test_street.street_id,
        building_type="residential",
        number_of_floors=2,
        number_of_units=4,
        building_condition="good",
        lga="Lagos",
        ward="Ward 1",
        geom=WKTElement("POINT(3.3792 6.5244)", srid=4326),
        gps_accuracy_m=Decimal("5.0"),
        enumerator_id=test_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
    )
    async_db_session.add(building)
    await async_db_session.commit()
    await async_db_session.refresh(building)
    
    return building


@pytest.mark.asyncio
async def test_create_export_task(async_db_session, test_user):
    """Test creating an export task."""
    filters = {"lga": "Lagos", "status": "approved"}
    
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters=filters,
        created_by=test_user.id,
    )
    
    assert task_id is not None
    assert isinstance(task_id, uuid.UUID)
    
    # Verify task was created in database
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    
    assert task.format == "csv"
    assert task.entity_type == "building"
    assert task.filters == filters
    assert task.status == "pending"
    assert task.created_by == test_user.id


@pytest.mark.asyncio
async def test_get_export_status_pending(async_db_session, test_user):
    """Test getting status of a pending export task."""
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters={},
        created_by=test_user.id,
    )
    
    status = await get_export_status(db=async_db_session, task_id=task_id)
    
    assert status["task_id"] == str(task_id)
    assert status["status"] == "pending"
    assert "created_at" in status
    assert "download_url" not in status
    assert "error" not in status


@pytest.mark.asyncio
async def test_get_export_status_not_found(async_db_session):
    """Test getting status of non-existent task."""
    fake_id = uuid.uuid4()
    
    with pytest.raises(ValueError, match="not found"):
        await get_export_status(db=async_db_session, task_id=fake_id)


@pytest.mark.asyncio
async def test_generate_csv_export_buildings(async_db_session, test_user, test_building):
    """Test generating CSV export for buildings."""
    # Create export task
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters={},
        created_by=test_user.id,
    )
    
    # Generate export
    await generate_csv_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters={},
    )
    
    # Verify task status updated
    status = await get_export_status(db=async_db_session, task_id=task_id)
    assert status["status"] == "completed"
    assert "download_url" in status
    
    # Verify file was created
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    assert task.file_path is not None
    
    file_path = Path(task.file_path)
    assert file_path.exists()
    
    # Verify CSV content
    csv_content = file_path.read_text()
    assert "building_id" in csv_content
    assert test_building.building_id in csv_content
    
    # Cleanup
    file_path.unlink()


@pytest.mark.asyncio
async def test_generate_csv_export_streets(async_db_session, test_user, test_street):
    """Test generating CSV export for streets."""
    # Create export task
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="street",
        filters={},
        created_by=test_user.id,
    )
    
    # Generate export
    await generate_csv_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="street",
        filters={},
    )
    
    # Verify task status updated
    status = await get_export_status(db=async_db_session, task_id=task_id)
    assert status["status"] == "completed"
    
    # Verify file was created
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    file_path = Path(task.file_path)
    assert file_path.exists()
    
    # Verify CSV content
    csv_content = file_path.read_text()
    assert "street_id" in csv_content
    assert test_street.street_id in csv_content
    
    # Cleanup
    file_path.unlink()


@pytest.mark.asyncio
async def test_generate_csv_export_with_filters(async_db_session, test_user, test_building):
    """Test generating CSV export with filters."""
    # Create export task with filters
    filters = {"lga": test_building.lga, "status": test_building.verification_status}
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters=filters,
        created_by=test_user.id,
    )
    
    # Generate export
    await generate_csv_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters=filters,
    )
    
    # Verify task completed
    status = await get_export_status(db=async_db_session, task_id=task_id)
    assert status["status"] == "completed"
    
    # Cleanup
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_generate_geojson_export(async_db_session, test_user, test_building):
    """Test generating GeoJSON export."""
    # Create export task
    task_id = await create_export_task(
        db=async_db_session,
        format="geojson",
        entity_type="building",
        filters={},
        created_by=test_user.id,
    )
    
    # Generate export
    await generate_geojson_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters={},
    )
    
    # Verify task status updated
    status = await get_export_status(db=async_db_session, task_id=task_id)
    assert status["status"] == "completed"
    
    # Verify file was created
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    file_path = Path(task.file_path)
    assert file_path.exists()
    
    # Verify GeoJSON content
    geojson_content = json.loads(file_path.read_text())
    assert geojson_content["type"] == "FeatureCollection"
    assert "features" in geojson_content
    assert len(geojson_content["features"]) > 0
    
    # Verify building is in export
    building_ids = [f["properties"]["building_id"] for f in geojson_content["features"]]
    assert test_building.building_id in building_ids
    
    # Cleanup
    file_path.unlink()


@pytest.mark.asyncio
async def test_generate_csv_export_error_handling(async_db_session, test_user):
    """Test error handling in CSV export."""
    # Create export task with invalid entity type
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="invalid",
        filters={},
        created_by=test_user.id,
    )
    
    # Generate export should fail
    with pytest.raises(ValueError, match="Unsupported entity_type"):
        await generate_csv_export(
            db=async_db_session,
            task_id=task_id,
            entity_type="invalid",
            filters={},
        )
    
    # Verify task status updated to failed
    status = await get_export_status(db=async_db_session, task_id=task_id)
    assert status["status"] == "failed"
    assert "error" in status



# Task 7.4: Export filtering and metadata inclusion tests
# Requirements 8.5 and 8.7


@pytest.mark.asyncio
async def test_csv_export_filter_by_lga_requirement_8_5(async_db_session, test_user, test_street):
    """Test CSV export filtering by LGA (Requirement 8.5)."""
    # Create buildings in different LGAs
    buildings = [
        Building(
            building_id="BLD_LAGOS_1",
            street_id=test_street.street_id,
            building_type="residential",
            number_of_floors=2,
            number_of_units=4,
            building_condition="good",
            lga="Lagos",
            ward="Ward 1",
            geom=WKTElement("POINT(3.3792 6.5244)", srid=4326),
            gps_accuracy_m=Decimal("5.0"),
            enumerator_id=test_user.id,
            enumeration_date=datetime.now(timezone.utc),
            verification_status="pending",
        ),
        Building(
            building_id="BLD_ABUJA_1",
            street_id=test_street.street_id,
            building_type="commercial",
            number_of_floors=3,
            number_of_units=6,
            building_condition="excellent",
            lga="Abuja",
            ward="Ward 1",
            geom=WKTElement("POINT(7.4905 9.0579)", srid=4326),
            gps_accuracy_m=Decimal("3.5"),
            enumerator_id=test_user.id,
            enumeration_date=datetime.now(timezone.utc),
            verification_status="pending",
        ),
    ]
    
    for building in buildings:
        async_db_session.add(building)
    await async_db_session.commit()
    
    # Export only Lagos buildings
    filters = {"lga": "Lagos"}
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters=filters,
        created_by=test_user.id,
    )
    
    await generate_csv_export(
        db=async_db_session,
        task_id=task_id,
        entity_type="building",
        filters=filters,
    )
    
    # Verify only Lagos buildings are in export
    result = await async_db_session.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one()
    csv_content = Path(task.file_path).read_text()
    
    assert "BLD_LAGOS_1" in csv_content
    assert "BLD_ABUJA_1" not in csv_content
    assert "Lagos" in csv_content
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_csv_export_filter_by_ward_requirement_8_5(async_db_session, test_user, test_street):
    """Test CSV export filtering by ward (Requirement 8.5)."""
    buildings = [
        Building(
            building_id="BLD_WARD1",
            street_id=test_street.street_id,
            building_type="residential",
            number_of_floors=2,
            number_of_units=4,
            building_condition="good",
            lga="Lagos",
            ward="Ward 1",
            geom=WKTElement("POINT(3.3792 6.5244)", srid=4326),
            gps_accuracy_m=Decimal("5.0"),
            enumerator_id=test_user.id,
            enumeration_date=datetime.now(timezone.utc),
            verification_status="pending",
        ),
        Building(
            building_id="BLD_WARD2",
            street_id=test_street.street_id,
            building_type="commercial",
            number_of_floors=3,
            number_of_units=6,
            building_condition="excellent",
            lga="Lagos",
            ward="Ward 2",
            geom=WKTElement("POINT(3.3793 6.5245)", srid=4326),
            gps_accuracy_m=Decimal("3.5"),
            enumerator_id=test_user.id,
            enumeration_date=datetime.now(timezone.utc),
            verification_status="pending",
        ),
    ]
    
    for building in buildings:
        async_db_session.add(building)
    await async_db_session.commit()
    
    # Export only Ward 1 buildings
    filters = {"ward": "Ward 1"}
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters=filters,
        created_by=test_user.id,
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
    
    assert "BLD_WARD1" in csv_content
    assert "BLD_WARD2" not in csv_content
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_csv_export_filter_by_status_requirement_8_5(async_db_session, test_user, test_street):
    """Test CSV export filtering by verification status (Requirement 8.5)."""
    buildings = [
        Building(
            building_id="BLD_PENDING",
            street_id=test_street.street_id,
            building_type="residential",
            number_of_floors=2,
            number_of_units=4,
            building_condition="good",
            lga="Lagos",
            ward="Ward 1",
            geom=WKTElement("POINT(3.3792 6.5244)", srid=4326),
            gps_accuracy_m=Decimal("5.0"),
            enumerator_id=test_user.id,
            enumeration_date=datetime.now(timezone.utc),
            verification_status="pending",
        ),
        Building(
            building_id="BLD_APPROVED",
            street_id=test_street.street_id,
            building_type="commercial",
            number_of_floors=3,
            number_of_units=6,
            building_condition="excellent",
            lga="Lagos",
            ward="Ward 1",
            geom=WKTElement("POINT(3.3793 6.5245)", srid=4326),
            gps_accuracy_m=Decimal("3.5"),
            enumerator_id=test_user.id,
            enumeration_date=datetime.now(timezone.utc),
            verification_status="approved",
        ),
    ]
    
    for building in buildings:
        async_db_session.add(building)
    await async_db_session.commit()
    
    # Export only approved buildings
    filters = {"status": "approved"}
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters=filters,
        created_by=test_user.id,
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
    
    assert "BLD_APPROVED" in csv_content
    assert "BLD_PENDING" not in csv_content
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_csv_export_includes_all_metadata_requirement_8_7(async_db_session, test_user, test_building):
    """Test CSV export includes all required metadata (Requirement 8.7)."""
    from io import StringIO
    import csv
    
    task_id = await create_export_task(
        db=async_db_session,
        format="csv",
        entity_type="building",
        filters={},
        created_by=test_user.id,
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
    
    # Parse CSV and check for required metadata fields
    reader = csv.DictReader(StringIO(csv_content))
    fieldnames = reader.fieldnames
    
    # GPS coordinates (Requirement 8.7)
    assert "longitude" in fieldnames
    assert "latitude" in fieldnames
    assert "gps_accuracy_m" in fieldnames
    
    # Timestamps (Requirement 8.7)
    assert "enumeration_date" in fieldnames
    assert "created_at" in fieldnames
    assert "updated_at" in fieldnames
    assert "reviewed_at" in fieldnames
    
    # Enumerator info (Requirement 8.7)
    assert "enumerator_id" in fieldnames
    assert "enumerator_username" in fieldnames
    
    # Verification status (Requirement 8.7)
    assert "verification_status" in fieldnames
    assert "reviewed_by" in fieldnames
    assert "rejection_reason" in fieldnames
    
    # Verify data is populated
    rows = list(reader)
    assert len(rows) > 0
    
    for row in rows:
        # GPS coordinates should have values
        assert row["longitude"] != ""
        assert row["latitude"] != ""
        assert row["gps_accuracy_m"] != ""
        
        # Enumerator info should have values
        assert row["enumerator_id"] != ""
        assert row["enumerator_username"] != ""
        
        # Verification status should have value
        assert row["verification_status"] in ("pending", "approved", "rejected")
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_geojson_export_filter_by_lga_requirement_8_5(async_db_session, test_user, test_street):
    """Test GeoJSON export filtering by LGA (Requirement 8.5)."""
    buildings = [
        Building(
            building_id="BLD_GEO_LAGOS",
            street_id=test_street.street_id,
            building_type="residential",
            number_of_floors=2,
            number_of_units=4,
            building_condition="good",
            lga="Lagos",
            ward="Ward 1",
            geom=WKTElement("POINT(3.3792 6.5244)", srid=4326),
            gps_accuracy_m=Decimal("5.0"),
            enumerator_id=test_user.id,
            enumeration_date=datetime.now(timezone.utc),
            verification_status="pending",
        ),
        Building(
            building_id="BLD_GEO_ABUJA",
            street_id=test_street.street_id,
            building_type="commercial",
            number_of_floors=3,
            number_of_units=6,
            building_condition="excellent",
            lga="Abuja",
            ward="Ward 1",
            geom=WKTElement("POINT(7.4905 9.0579)", srid=4326),
            gps_accuracy_m=Decimal("3.5"),
            enumerator_id=test_user.id,
            enumeration_date=datetime.now(timezone.utc),
            verification_status="pending",
        ),
    ]
    
    for building in buildings:
        async_db_session.add(building)
    await async_db_session.commit()
    
    # Export only Lagos buildings
    filters = {"lga": "Lagos"}
    task_id = await create_export_task(
        db=async_db_session,
        format="geojson",
        entity_type="building",
        filters=filters,
        created_by=test_user.id,
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
    
    # Verify only Lagos buildings are in export
    features = geojson_content["features"]
    assert len(features) == 1
    assert features[0]["properties"]["building_id"] == "BLD_GEO_LAGOS"
    assert features[0]["properties"]["lga"] == "Lagos"
    
    Path(task.file_path).unlink()


@pytest.mark.asyncio
async def test_geojson_export_includes_metadata_requirement_8_7(async_db_session, test_user, test_building):
    """Test GeoJSON export includes all metadata (Requirement 8.7)."""
    task_id = await create_export_task(
        db=async_db_session,
        format="geojson",
        entity_type="building",
        filters={},
        created_by=test_user.id,
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
    assert len(features) > 0
    
    for feature in features:
        # GPS coordinates in geometry (Requirement 8.7)
        assert feature["geometry"]["type"] == "Point"
        assert len(feature["geometry"]["coordinates"]) == 2
        
        props = feature["properties"]
        
        # Enumerator info (Requirement 8.7)
        assert "enumerator_id" in props
        assert props["enumerator_id"] != ""
        
        # Timestamps (Requirement 8.7)
        assert "enumeration_date" in props
        assert props["enumeration_date"] != ""
        
        # Verification status (Requirement 8.7)
        assert "verification_status" in props
        assert props["verification_status"] in ("pending", "approved", "rejected")
    
    Path(task.file_path).unlink()

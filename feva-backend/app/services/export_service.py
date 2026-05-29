"""Async export service — GeoJSON, CSV, and Shapefile export pipeline.

Requirements: 8.1, 8.2, 8.3, 8.6, 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 21.6
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import fiona
from geoalchemy2.functions import ST_AsGeoJSON, ST_X, ST_Y
from shapely.geometry import mapping, shape
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.boundary_discrepancy import BoundaryDiscrepancy
from app.models.building import Building
from app.models.export_task import ExportTask
from app.models.street import Street
from app.models.user import User
from app.services.geojson_service import (
    BuildingRecord,
    GeoJSONParser,
    GeoJSONSerialiser,
    StreetRecord,
)


# Export directory configuration
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)


async def create_export_task(
    db: AsyncSession,
    format: str,
    entity_type: str,
    filters: dict[str, Any],
    created_by: uuid.UUID,
) -> uuid.UUID:
    """Create a new export task and return its task_id.
    
    Args:
        db: Database session
        format: Export format (csv, geojson)
        entity_type: Entity type to export (building, street, audit_log)
        filters: Filter criteria (lga, ward, status, date_from, date_to)
        created_by: User ID creating the export
        
    Returns:
        UUID of the created export task
    """
    task = ExportTask(
        created_by=created_by,
        format=format,
        entity_type=entity_type,
        filters=filters,
        status="pending",
    )
    db.add(task)
    await db.flush()
    await db.commit()
    return task.id


async def get_export_status(
    db: AsyncSession,
    task_id: uuid.UUID,
) -> dict[str, Any]:
    """Get the status of an export task.
    
    Args:
        db: Database session
        task_id: UUID of the export task
        
    Returns:
        Dictionary with status, download_url (if completed), and error_message (if failed)
    """
    result = await db.execute(
        select(ExportTask).where(ExportTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise ValueError(f"Export task {task_id} not found")
    
    response = {
        "task_id": str(task.id),
        "status": task.status,
        "created_at": task.created_at.isoformat() if hasattr(task.created_at, 'isoformat') else str(task.created_at),
    }
    
    if task.status == "completed" and task.file_path:
        # Generate download URL
        response["download_url"] = f"/api/v1/admin/export/download/{task.id}"
    
    if task.status == "failed" and task.error_message:
        response["error"] = task.error_message
    
    return response


async def generate_csv_export(
    db: AsyncSession,
    task_id: uuid.UUID,
    entity_type: str,
    filters: dict[str, Any],
) -> None:
    """Generate CSV export for buildings or streets.
    
    Args:
        db: Database session
        task_id: UUID of the export task
        entity_type: Entity type to export (building, street)
        filters: Filter criteria (lga, ward, status, date_from, date_to)
    """
    try:
        # Update task status to processing
        result = await db.execute(
            select(ExportTask).where(ExportTask.id == task_id)
        )
        task = result.scalar_one()
        task.status = "processing"
        await db.commit()
        
        # Generate CSV content
        csv_buffer = io.StringIO()
        
        if entity_type == "building":
            await _generate_building_csv(db, csv_buffer, filters)
        elif entity_type == "street":
            await _generate_street_csv(db, csv_buffer, filters)
        elif entity_type == "audit_log":
            await _generate_audit_log_csv(db, csv_buffer, filters)
        else:
            raise ValueError(f"Unsupported entity_type for CSV export: {entity_type}")
        
        # Save to file
        csv_content = csv_buffer.getvalue()
        file_path = EXPORT_DIR / f"{task_id}.csv"
        file_path.write_text(csv_content, encoding="utf-8")
        
        # Update task with completion
        task.status = "completed"
        task.file_path = str(file_path)
        task.completed_at = datetime.now(timezone.utc)
        await db.commit()
        
    except Exception as exc:
        # Update task with error
        result = await db.execute(
            select(ExportTask).where(ExportTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task:
            task.status = "failed"
            task.error_message = str(exc)
            task.completed_at = datetime.now(timezone.utc)
            await db.commit()
        raise


async def generate_geojson_export(
    db: AsyncSession,
    task_id: uuid.UUID,
    entity_type: str,
    filters: dict[str, Any],
) -> None:
    """Generate GeoJSON export for buildings or streets.
    
    Args:
        db: Database session
        task_id: UUID of the export task
        entity_type: Entity type to export (building, street)
        filters: Filter criteria (lga, ward, status, date_from, date_to)
    """
    try:
        # Update task status to processing
        result = await db.execute(
            select(ExportTask).where(ExportTask.id == task_id)
        )
        task = result.scalar_one()
        task.status = "processing"
        await db.commit()
        
        # Fetch records based on filters
        records = await _fetch_filtered_records(db, entity_type, filters)
        
        # Serialize to GeoJSON
        serialiser = GeoJSONSerialiser()
        feature_collection = serialiser.serialise_feature_collection(records)
        
        # Round-trip verification (Requirement 14.6)
        geojson_str = json.dumps(feature_collection, indent=2)
        parser = GeoJSONParser()
        parser.parse_feature_collection(json.loads(geojson_str))
        
        # Save to file
        file_path = EXPORT_DIR / f"{task_id}.geojson"
        file_path.write_text(geojson_str, encoding="utf-8")
        
        # Update task with completion
        task.status = "completed"
        task.file_path = str(file_path)
        task.completed_at = datetime.now(timezone.utc)
        await db.commit()
        
    except Exception as exc:
        # Update task with error
        result = await db.execute(
            select(ExportTask).where(ExportTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task:
            task.status = "failed"
            task.error_message = str(exc)
            task.completed_at = datetime.now(timezone.utc)
            await db.commit()
        raise


async def run_geojson_export(
    db: AsyncSession,
    job_id: str,
    current_user: User,
    year: int | None = None,
    month: int | None = None,
) -> None:
    """Background task: query approved records, serialise to GeoJSON, verify round-trip.

    Bundles GeoJSON + boundary_discrepancies.csv into a ZIP package.

    DEPRECATED: Use generate_geojson_export with ExportTask instead.
    """
    # This is kept for backward compatibility with existing code
    try:
        records = await _fetch_approved_records(db, year=year, month=month)
        serialiser = GeoJSONSerialiser()
        feature_collection = serialiser.serialise_feature_collection(records)

        # Round-trip verification (Requirement 14.6)
        geojson_str = json.dumps(feature_collection)
        parser = GeoJSONParser()
        parser.parse_feature_collection(json.loads(geojson_str))

        # Bundle GeoJSON + boundary_discrepancies.csv into ZIP (Requirement 21.6)
        discrepancies_csv = await _generate_boundary_discrepancies_csv(db)
        zip_bytes = _bundle_into_zip(
            {
                f"{job_id}.geojson": geojson_str.encode("utf-8"),
                "boundary_discrepancies.csv": discrepancies_csv,
            }
        )
        zip_path = EXPORT_DIR / f"{job_id}.zip"
        zip_path.write_bytes(zip_bytes)

        # Write audit log
        await _write_audit(db, current_user.id, "export_geojson", job_id)
        await db.commit()

    except Exception as exc:
        raise


async def run_shapefile_export(
    db: AsyncSession,
    job_id: str,
    current_user: User,
    year: int | None = None,
    month: int | None = None,
) -> None:
    """Background task: export approved records to Shapefile via Fiona.

    Bundles Shapefile + boundary_discrepancies.csv into a ZIP package.
    """
    job = _jobs.get(job_id)
    if job is None:
        return

    try:
        _jobs[job_id]["status"] = "running"

        records = await _fetch_approved_records(db, year=year, month=month)

        with tempfile.TemporaryDirectory() as tmpdir:
            shp_path = Path(tmpdir) / f"{job_id}.shp"
            _write_shapefile(records, shp_path)

            # Read back for round-trip verification (Requirement 14.7)
            _verify_shapefile_roundtrip(records, shp_path)

            shp_bytes = shp_path.read_bytes()

        # Bundle Shapefile + boundary_discrepancies.csv into ZIP (Requirement 21.6)
        discrepancies_csv = await _generate_boundary_discrepancies_csv(db)
        zip_bytes = _bundle_into_zip(
            {
                f"{job_id}.shp": shp_bytes,
                "boundary_discrepancies.csv": discrepancies_csv,
            }
        )
        zip_path = EXPORT_DIR / f"{job_id}.zip"
        zip_path.write_bytes(zip_bytes)

        url = await _store_export(zip_bytes, f"{job_id}.zip")

        await _write_audit(db, current_user.id, "export_shapefile", job_id)
        await db.commit()

        _jobs[job_id]["status"] = "completed"
        _jobs[job_id]["download_url"] = url

    except Exception as exc:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = str(exc)


async def _generate_building_csv(
    db: AsyncSession,
    csv_buffer: io.StringIO,
    filters: dict[str, Any],
) -> None:
    """Generate CSV for building records with filters."""
    # Define CSV columns
    fieldnames = [
        "building_id", "street_id", "street_address", "building_type", "number_of_floors",
        "number_of_units", "building_condition", "has_signage", "business_names",
        "notes", "longitude", "latitude", "gps_accuracy_m", "zone", "lga", "ward",
        "postcode", "postcode_status", "enumerator_id", "enumerator_username",
        "enumeration_date", "verification_status", "reviewed_by", "reviewed_at",
        "rejection_reason", "boundary_flag", "gps_accuracy_flag", "duplicate_flag",
        "qa_flags", "created_at", "updated_at"
    ]
    
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    writer.writeheader()
    
    # Build query with filters
    query = select(
        Building,
        ST_X(Building.geom).label("longitude"),
        ST_Y(Building.geom).label("latitude"),
        User.username.label("enumerator_username")
    ).join(User, Building.enumerator_id == User.id)
    
    conditions = []
    if filters.get("lga"):
        conditions.append(Building.lga == filters["lga"])
    if filters.get("ward"):
        conditions.append(Building.ward == filters["ward"])
    if filters.get("status"):
        conditions.append(Building.verification_status == filters["status"])
    if filters.get("date_from"):
        conditions.append(Building.enumeration_date >= filters["date_from"])
    if filters.get("date_to"):
        conditions.append(Building.enumeration_date <= filters["date_to"])
    
    if conditions:
        query = query.where(and_(*conditions))
    
    result = await db.execute(query)
    
    for building, lon, lat, enumerator_username in result:
        # Get reviewer username if exists
        reviewer_username = None
        if building.reviewed_by:
            reviewer_result = await db.execute(
                select(User.username).where(User.id == building.reviewed_by)
            )
            reviewer_username = reviewer_result.scalar_one_or_none()
        
        writer.writerow({
            "building_id": building.building_id,
            "street_id": building.street_id,
            "street_address": building.street_address or "",
            "building_type": building.building_type,
            "number_of_floors": building.number_of_floors,
            "number_of_units": building.number_of_units,
            "building_condition": building.building_condition,
            "has_signage": building.has_signage,
            "business_names": json.dumps(building.business_names) if building.business_names else "",
            "notes": building.notes or "",
            "longitude": float(lon),
            "latitude": float(lat),
            "gps_accuracy_m": float(building.gps_accuracy_m),
            "zone": building.zone or "",
            "lga": building.lga,
            "ward": building.ward or "",
            "postcode": building.postcode or "",
            "postcode_status": building.postcode_status,
            "enumerator_id": str(building.enumerator_id),
            "enumerator_username": enumerator_username,
            "enumeration_date": building.enumeration_date.isoformat() if hasattr(building.enumeration_date, 'isoformat') else str(building.enumeration_date),
            "verification_status": building.verification_status,
            "reviewed_by": reviewer_username or "",
            "reviewed_at": building.reviewed_at.isoformat() if building.reviewed_at and hasattr(building.reviewed_at, 'isoformat') else (str(building.reviewed_at) if building.reviewed_at else ""),
            "rejection_reason": building.rejection_reason or "",
            "boundary_flag": building.boundary_flag,
            "gps_accuracy_flag": building.gps_accuracy_flag,
            "duplicate_flag": building.duplicate_flag,
            "qa_flags": json.dumps(building.qa_flags) if building.qa_flags else "",
            "created_at": building.created_at.isoformat() if hasattr(building.created_at, 'isoformat') else str(building.created_at),
            "updated_at": building.updated_at.isoformat() if hasattr(building.updated_at, 'isoformat') else str(building.updated_at),
        })


async def _generate_street_csv(
    db: AsyncSession,
    csv_buffer: io.StringIO,
    filters: dict[str, Any],
) -> None:
    """Generate CSV for street records with filters."""
    # Define CSV columns
    fieldnames = [
        "street_id", "street_name", "street_address", "street_type", "surface_type",
        "street_condition", "notes", "geometry_wkt", "zone", "lga", "ward",
        "enumerator_id", "enumerator_username", "enumeration_date",
        "verification_status", "reviewed_by", "reviewed_at", "rejection_reason",
        "boundary_flag", "gps_accuracy_flag", "qa_flags", "created_at", "updated_at"
    ]
    
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    writer.writeheader()
    
    # Build query with filters
    query = select(
        Street,
        ST_AsGeoJSON(Street.geom).label("geojson"),
        User.username.label("enumerator_username")
    ).join(User, Street.enumerator_id == User.id)
    
    conditions = []
    if filters.get("lga"):
        conditions.append(Street.lga == filters["lga"])
    if filters.get("ward"):
        conditions.append(Street.ward == filters["ward"])
    if filters.get("status"):
        conditions.append(Street.verification_status == filters["status"])
    if filters.get("date_from"):
        conditions.append(Street.enumeration_date >= filters["date_from"])
    if filters.get("date_to"):
        conditions.append(Street.enumeration_date <= filters["date_to"])
    
    if conditions:
        query = query.where(and_(*conditions))
    
    result = await db.execute(query)
    
    for street, geojson_str, enumerator_username in result:
        # Get reviewer username if exists
        reviewer_username = None
        if street.reviewed_by:
            reviewer_result = await db.execute(
                select(User.username).where(User.id == street.reviewed_by)
            )
            reviewer_username = reviewer_result.scalar_one_or_none()
        
        # Parse GeoJSON to get WKT-like representation
        geom = json.loads(geojson_str)
        coords_str = json.dumps(geom.get("coordinates", []))
        
        writer.writerow({
            "street_id": street.street_id,
            "street_name": street.street_name,
            "street_address": street.street_address or "",
            "street_type": street.street_type,
            "surface_type": street.surface_type,
            "street_condition": street.street_condition,
            "notes": street.notes or "",
            "geometry_wkt": coords_str,
            "zone": street.zone or "",
            "lga": street.lga,
            "ward": street.ward or "",
            "enumerator_id": str(street.enumerator_id),
            "enumerator_username": enumerator_username,
            "enumeration_date": street.enumeration_date.isoformat() if hasattr(street.enumeration_date, 'isoformat') else str(street.enumeration_date),
            "verification_status": street.verification_status,
            "reviewed_by": reviewer_username or "",
            "reviewed_at": street.reviewed_at.isoformat() if street.reviewed_at and hasattr(street.reviewed_at, 'isoformat') else (str(street.reviewed_at) if street.reviewed_at else ""),
            "rejection_reason": street.rejection_reason or "",
            "boundary_flag": street.boundary_flag,
            "gps_accuracy_flag": street.gps_accuracy_flag,
            "qa_flags": json.dumps(street.qa_flags) if street.qa_flags else "",
            "created_at": street.created_at.isoformat() if hasattr(street.created_at, 'isoformat') else str(street.created_at),
            "updated_at": street.updated_at.isoformat() if hasattr(street.updated_at, 'isoformat') else str(street.updated_at),
        })


async def _generate_audit_log_csv(
    db: AsyncSession,
    csv_buffer: io.StringIO,
    filters: dict[str, Any],
) -> None:
    """Generate CSV for audit log records with filters."""
    # Define CSV columns
    fieldnames = [
        "id", "user_id", "username", "operation", "entity_type",
        "entity_id", "detail", "occurred_at"
    ]
    
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    writer.writeheader()
    
    # Build query with filters
    query = select(AuditLog, User.username).outerjoin(
        User, AuditLog.user_id == User.id
    ).order_by(AuditLog.occurred_at.desc())
    
    conditions = []
    if filters.get("user_id"):
        conditions.append(AuditLog.user_id == filters["user_id"])
    if filters.get("operation"):
        conditions.append(AuditLog.operation == filters["operation"])
    if filters.get("entity_type"):
        conditions.append(AuditLog.entity_type == filters["entity_type"])
    if filters.get("date_from"):
        conditions.append(AuditLog.occurred_at >= filters["date_from"])
    if filters.get("date_to"):
        conditions.append(AuditLog.occurred_at <= filters["date_to"])
    
    if conditions:
        query = query.where(and_(*conditions))
    
    result = await db.execute(query)
    
    for audit_log, username in result:
        writer.writerow({
            "id": str(audit_log.id),
            "user_id": str(audit_log.user_id) if audit_log.user_id else "",
            "username": username or "",
            "operation": audit_log.operation,
            "entity_type": audit_log.entity_type,
            "entity_id": audit_log.entity_id or "",
            "detail": json.dumps(audit_log.detail) if audit_log.detail else "",
            "occurred_at": audit_log.occurred_at.isoformat() if hasattr(audit_log.occurred_at, 'isoformat') else str(audit_log.occurred_at),
        })


async def _fetch_filtered_records(
    db: AsyncSession,
    entity_type: str,
    filters: dict[str, Any],
) -> list[StreetRecord | BuildingRecord]:
    """Fetch records based on entity type and filters."""
    records: list[StreetRecord | BuildingRecord] = []
    
    if entity_type in ("street", "both"):
        # Query streets
        street_q = select(Street, ST_AsGeoJSON(Street.geom).label("geojson"))
        
        conditions = []
        if filters.get("lga"):
            conditions.append(Street.lga == filters["lga"])
        if filters.get("ward"):
            conditions.append(Street.ward == filters["ward"])
        if filters.get("status"):
            conditions.append(Street.verification_status == filters["status"])
        if filters.get("date_from"):
            conditions.append(Street.enumeration_date >= filters["date_from"])
        if filters.get("date_to"):
            conditions.append(Street.enumeration_date <= filters["date_to"])
        
        if conditions:
            street_q = street_q.where(and_(*conditions))
        
        street_result = await db.execute(street_q)
        for street, geojson_str in street_result:
            geom = json.loads(geojson_str)
            coords = geom.get("coordinates", [])
            records.append(StreetRecord(
                street_id=street.street_id,
                street_name=street.street_name,
                street_address=street.street_address or "",
                street_type=street.street_type,
                surface_type=street.surface_type,
                street_condition=street.street_condition,
                lga=street.lga,
                coordinates=coords,
                zone=street.zone,
                ward=street.ward,
                notes=street.notes,
                verification_status=street.verification_status,
                enumerator_id=str(street.enumerator_id),
                enumeration_date=str(street.enumeration_date),
                boundary_flag=street.boundary_flag,
                gps_accuracy_flag=street.gps_accuracy_flag,
                qa_flags=list(street.qa_flags or []) if isinstance(street.qa_flags, (list, dict)) else [],
            ))
    
    if entity_type in ("building", "both"):
        # Query buildings
        building_q = select(Building, ST_AsGeoJSON(Building.geom).label("geojson"))
        
        conditions = []
        if filters.get("lga"):
            conditions.append(Building.lga == filters["lga"])
        if filters.get("ward"):
            conditions.append(Building.ward == filters["ward"])
        if filters.get("status"):
            conditions.append(Building.verification_status == filters["status"])
        if filters.get("date_from"):
            conditions.append(Building.enumeration_date >= filters["date_from"])
        if filters.get("date_to"):
            conditions.append(Building.enumeration_date <= filters["date_to"])
        
        if conditions:
            building_q = building_q.where(and_(*conditions))
        
        building_result = await db.execute(building_q)
        for building, geojson_str in building_result:
            geom = json.loads(geojson_str)
            coords = geom.get("coordinates", [])
            records.append(BuildingRecord(
                building_id=building.building_id,
                street_id=building.street_id,
                street_address=building.street_address,
                building_type=building.building_type,
                number_of_floors=building.number_of_floors,
                number_of_units=building.number_of_units,
                building_condition=building.building_condition,
                lga=building.lga,
                coordinates=coords,
                zone=building.zone,
                ward=building.ward,
                postcode=building.postcode,
                postcode_status=building.postcode_status or "resolved",
                has_signage=building.has_signage,
                business_names=list(building.business_names or []),
                notes=building.notes,
                verification_status=building.verification_status,
                enumerator_id=str(building.enumerator_id),
                enumeration_date=str(building.enumeration_date),
                boundary_flag=building.boundary_flag,
                gps_accuracy_flag=building.gps_accuracy_flag,
                duplicate_flag=building.duplicate_flag,
                qa_flags=list(building.qa_flags or []) if isinstance(building.qa_flags, (list, dict)) else [],
            ))
    
    return records


async def _fetch_approved_records(
    db: AsyncSession,
    year: int | None = None,
    month: int | None = None,
) -> list[StreetRecord | BuildingRecord]:
    """Fetch only approved records, optionally filtered by year/month."""
    records: list[StreetRecord | BuildingRecord] = []

    # Streets
    street_q = select(Street, ST_AsGeoJSON(Street.geom).label("geojson")).where(
        Street.verification_status == "approved"
    )
    street_result = await db.execute(street_q)
    for street, geojson_str in street_result:
        geom = json.loads(geojson_str)
        coords = geom.get("coordinates", [])
        records.append(StreetRecord(
            street_id=street.street_id,
            street_name=street.street_name,
            street_address=street.street_address or "",
            street_type=street.street_type,
            surface_type=street.surface_type,
            street_condition=street.street_condition,
            lga=street.lga,
            coordinates=coords,
            zone=street.zone,
            ward=street.ward,
            notes=street.notes,
            verification_status=street.verification_status,
            enumerator_id=str(street.enumerator_id),
            enumeration_date=str(street.enumeration_date),
            boundary_flag=street.boundary_flag,
            gps_accuracy_flag=street.gps_accuracy_flag,
            qa_flags=list(street.qa_flags or []),
        ))

    # Buildings
    building_q = select(Building, ST_AsGeoJSON(Building.geom).label("geojson")).where(
        Building.verification_status == "approved"
    )
    building_result = await db.execute(building_q)
    for building, geojson_str in building_result:
        geom = json.loads(geojson_str)
        coords = geom.get("coordinates", [])
        records.append(BuildingRecord(
            building_id=building.building_id,
            street_id=building.street_id,
            street_address=building.street_address,
            building_type=building.building_type,
            number_of_floors=building.number_of_floors,
            number_of_units=building.number_of_units,
            building_condition=building.building_condition,
            lga=building.lga,
            coordinates=coords,
            zone=building.zone,
            ward=building.ward,
            postcode=building.postcode,
            postcode_status=building.postcode_status or "resolved",
            has_signage=building.has_signage,
            business_names=list(building.business_names or []),
            notes=building.notes,
            verification_status=building.verification_status,
            enumerator_id=str(building.enumerator_id),
            enumeration_date=str(building.enumeration_date),
            boundary_flag=building.boundary_flag,
            gps_accuracy_flag=building.gps_accuracy_flag,
            duplicate_flag=building.duplicate_flag,
            qa_flags=list(building.qa_flags or []),
        ))

    return records


def _write_shapefile(
    records: list[StreetRecord | BuildingRecord], path: Path
) -> None:
    """Write records to a Shapefile using Fiona."""
    schema = {
        "geometry": "Unknown",
        "properties": {
            "record_id": "str",
            "lga": "str",
            "ward": "str",
            "verification_status": "str",
            "enumerator_id": "str",
        },
    }
    with fiona.open(str(path), "w", driver="ESRI Shapefile", schema=schema, crs="EPSG:4326") as dst:
        for r in records:
            if isinstance(r, StreetRecord):
                geom = {"type": "LineString", "coordinates": r.coordinates}
                props = {
                    "record_id": r.street_id,
                    "lga": r.lga,
                    "ward": r.ward or "",
                    "verification_status": r.verification_status,
                    "enumerator_id": r.enumerator_id,
                }
            else:
                geom = {"type": "Point", "coordinates": r.coordinates}
                props = {
                    "record_id": r.building_id,
                    "lga": r.lga,
                    "ward": r.ward or "",
                    "verification_status": r.verification_status,
                    "enumerator_id": r.enumerator_id,
                }
            dst.write({"geometry": geom, "properties": props})


def _verify_shapefile_roundtrip(
    original: list[StreetRecord | BuildingRecord], path: Path
) -> None:
    """Re-read Shapefile and assert record count matches original."""
    with fiona.open(str(path)) as src:
        count = len(list(src))
    if count != len(original):
        raise ValueError(
            f"Shapefile round-trip failed: wrote {len(original)} records, read back {count}"
        )


async def _write_audit(
    db: AsyncSession, user_id: uuid.UUID, operation: str, job_id: str
) -> None:
    log = AuditLog(
        user_id=user_id,
        operation=operation,
        entity_type="export_job",
        entity_id=job_id,
        detail={"job_id": job_id},
    )
    db.add(log)
    await db.flush()


async def _generate_boundary_discrepancies_csv(db: AsyncSession) -> bytes:
    """Query all boundary_discrepancies rows and return them as CSV bytes.

    Columns: postcode_polygon_id, admin_polygon_id, admin_type, overlap_area_m2, detected_at

    Requirements: 21.6
    """
    result = await db.execute(
        select(BoundaryDiscrepancy).order_by(BoundaryDiscrepancy.detected_at.desc())
    )
    rows = result.scalars().all()

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "postcode_polygon_id",
            "admin_polygon_id",
            "admin_type",
            "overlap_area_m2",
            "detected_at",
        ],
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "postcode_polygon_id": row.postcode_polygon_id,
                "admin_polygon_id": row.admin_polygon_id,
                "admin_type": row.admin_type,
                "overlap_area_m2": float(row.overlap_area_m2),
                "detected_at": row.detected_at.isoformat() if row.detected_at else "",
            }
        )
    return output.getvalue().encode("utf-8")


def _bundle_into_zip(files: dict[str, bytes]) -> bytes:
    """Bundle a dict of {filename: bytes} into an in-memory ZIP archive."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    return buf.getvalue()


async def generate_coverage_report_csv(
    db: AsyncSession,
    year: int,
    month: int,
    lga: str | None = None,
    verification_status: str | None = None,
) -> bytes:
    """Generate coverage_report.csv: street/building counts per LGA and enumerator.

    Includes zero-count rows for all known LGAs and enumerators with no records
    in the given month (Requirement 22.6).

    Requirements: 22.1, 22.3, 22.6
    """
    from calendar import monthrange
    from datetime import date

    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    # Build date-range + optional filters
    def _base_conditions(model):
        conds = [
            model.enumeration_date >= first_day,
            model.enumeration_date <= last_day,
        ]
        if lga:
            conds.append(model.lga == lga)
        if verification_status:
            conds.append(model.verification_status == verification_status)
        return conds

    # All known LGAs (from both tables, not just this month)
    lga_result = await db.execute(
        select(Building.lga).distinct().union(select(Street.lga).distinct())
    )
    all_lgas: set[str] = {row[0] for row in lga_result.fetchall() if row[0]}

    # All known enumerators
    enum_result = await db.execute(select(User.id, User.username))
    all_enumerators: dict[str, str] = {str(r.id): r.username for r in enum_result.fetchall()}

    # Street counts per LGA + enumerator for the month
    street_lga_q = (
        select(Street.lga, func.count().label("cnt"))
        .where(and_(*_base_conditions(Street)))
        .group_by(Street.lga)
    )
    street_enum_q = (
        select(Street.enumerator_id, func.count().label("cnt"))
        .where(and_(*_base_conditions(Street)))
        .group_by(Street.enumerator_id)
    )

    # Building counts per LGA + enumerator for the month
    bldg_lga_q = (
        select(Building.lga, func.count().label("cnt"))
        .where(and_(*_base_conditions(Building)))
        .group_by(Building.lga)
    )
    bldg_enum_q = (
        select(Building.enumerator_id, func.count().label("cnt"))
        .where(and_(*_base_conditions(Building)))
        .group_by(Building.enumerator_id)
    )

    street_by_lga = {r.lga: r.cnt for r in (await db.execute(street_lga_q)).fetchall()}
    bldg_by_lga = {r.lga: r.cnt for r in (await db.execute(bldg_lga_q)).fetchall()}
    street_by_enum = {str(r.enumerator_id): r.cnt for r in (await db.execute(street_enum_q)).fetchall()}
    bldg_by_enum = {str(r.enumerator_id): r.cnt for r in (await db.execute(bldg_enum_q)).fetchall()}

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["dimension", "identifier", "streets", "buildings", "total"],
    )
    writer.writeheader()

    # Per-LGA rows (zero-count rows included for all known LGAs)
    for lga_name in sorted(all_lgas):
        streets = street_by_lga.get(lga_name, 0)
        buildings = bldg_by_lga.get(lga_name, 0)
        writer.writerow({
            "dimension": "lga",
            "identifier": lga_name,
            "streets": streets,
            "buildings": buildings,
            "total": streets + buildings,
        })

    # Per-enumerator rows (zero-count rows included for all known enumerators)
    for enum_id, username in sorted(all_enumerators.items(), key=lambda x: x[1]):
        streets = street_by_enum.get(enum_id, 0)
        buildings = bldg_by_enum.get(enum_id, 0)
        writer.writerow({
            "dimension": "enumerator",
            "identifier": username,
            "streets": streets,
            "buildings": buildings,
            "total": streets + buildings,
        })

    return output.getvalue().encode("utf-8")


async def generate_dq_metrics_snapshot_csv(
    db: AsyncSession,
    year: int,
    month: int,
    lga: str | None = None,
    verification_status: str | None = None,
) -> bytes:
    """Generate dq_metrics_snapshot.csv: 5 QA metrics for the given month.

    Metrics:
    1. median_gps_accuracy_m
    2. boundary_containment_pct
    3. mandatory_field_completion_pct
    4. duplicate_flag_pct
    5. verification_approval_pct

    Requirements: 22.2, 22.3
    """
    from calendar import monthrange
    from datetime import date

    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    def _bldg_conds():
        conds = [
            Building.enumeration_date >= first_day,
            Building.enumeration_date <= last_day,
        ]
        if lga:
            conds.append(Building.lga == lga)
        if verification_status:
            conds.append(Building.verification_status == verification_status)
        return conds

    def _street_conds():
        conds = [
            Street.enumeration_date >= first_day,
            Street.enumeration_date <= last_day,
        ]
        if lga:
            conds.append(Street.lga == lga)
        if verification_status:
            conds.append(Street.verification_status == verification_status)
        return conds

    total_buildings = (await db.execute(
        select(func.count()).select_from(Building).where(and_(*_bldg_conds()))
    )).scalar() or 0

    total_streets = (await db.execute(
        select(func.count()).select_from(Street).where(and_(*_street_conds()))
    )).scalar() or 0

    total_records = total_buildings + total_streets

    # 1. Median GPS accuracy (buildings only)
    median_gps = 0.0
    if total_buildings > 0:
        result = await db.execute(
            select(func.percentile_cont(0.5).within_group(Building.gps_accuracy_m))
            .where(and_(*_bldg_conds()))
        )
        median_gps = float(result.scalar() or 0.0)

    # 2. Boundary containment %
    boundary_flagged_b = (await db.execute(
        select(func.count()).select_from(Building)
        .where(and_(*_bldg_conds(), Building.boundary_flag.is_(True)))
    )).scalar() or 0
    boundary_flagged_s = (await db.execute(
        select(func.count()).select_from(Street)
        .where(and_(*_street_conds(), Street.boundary_flag.is_(True)))
    )).scalar() or 0
    boundary_containment_pct = (
        round((1 - (boundary_flagged_b + boundary_flagged_s) / total_records) * 100, 2)
        if total_records > 0 else 100.0
    )

    # 3. Mandatory field completion % — buildings must have building_type, lga, ward
    incomplete_b = (await db.execute(
        select(func.count()).select_from(Building)
        .where(and_(
            *_bldg_conds(),
            (Building.building_type.is_(None)) | (Building.lga.is_(None)) | (Building.ward.is_(None)),
        ))
    )).scalar() or 0
    incomplete_s = (await db.execute(
        select(func.count()).select_from(Street)
        .where(and_(
            *_street_conds(),
            (Street.street_name.is_(None)) | (Street.lga.is_(None)),
        ))
    )).scalar() or 0
    mandatory_completion_pct = (
        round((1 - (incomplete_b + incomplete_s) / total_records) * 100, 2)
        if total_records > 0 else 100.0
    )

    # 4. Duplicate flag %
    duplicate_flagged = (await db.execute(
        select(func.count()).select_from(Building)
        .where(and_(*_bldg_conds(), Building.duplicate_flag.is_(True)))
    )).scalar() or 0
    duplicate_flag_pct = (
        round(duplicate_flagged / total_buildings * 100, 2)
        if total_buildings > 0 else 0.0
    )

    # 5. Verification approval %
    approved_b = (await db.execute(
        select(func.count()).select_from(Building)
        .where(and_(*_bldg_conds(), Building.verification_status == "approved"))
    )).scalar() or 0
    approved_s = (await db.execute(
        select(func.count()).select_from(Street)
        .where(and_(*_street_conds(), Street.verification_status == "approved"))
    )).scalar() or 0
    verification_approval_pct = (
        round((approved_b + approved_s) / total_records * 100, 2)
        if total_records > 0 else 0.0
    )

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["metric", "value", "year", "month"],
    )
    writer.writeheader()
    for metric, value in [
        ("median_gps_accuracy_m", median_gps),
        ("boundary_containment_pct", boundary_containment_pct),
        ("mandatory_field_completion_pct", mandatory_completion_pct),
        ("duplicate_flag_pct", duplicate_flag_pct),
        ("verification_approval_pct", verification_approval_pct),
    ]:
        writer.writerow({"metric": metric, "value": value, "year": year, "month": month})

    return output.getvalue().encode("utf-8")

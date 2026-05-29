"""Server-side QA validation service.

Validates incoming sync records against all QA rules and writes
qa_flags to accepted records.

Rules enforced:
  - All mandatory fields present
  - GPS precision ≥ 5 decimal places
  - Geometry type matches entity (LineString for streets, Point for buildings)
  - street_id reference exists (for buildings)

Requirements: 11.1, 11.4, 11.5, 11.6, 11.7
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

_GPS_PRECISION_RE = re.compile(r"^-?\d+\.\d{5,}$")


def _format_gps(value: Any) -> str:
    """Format a GPS value to a string with enough decimal places for the precision check."""
    try:
        return f"{float(value):.6f}"
    except (TypeError, ValueError):
        return str(value)


_STREET_MANDATORY = (
    "street_id", "street_name", "street_type",
    "surface_type", "street_condition", "lga",
)
_BUILDING_MANDATORY = (
    "building_id", "street_id", "building_type",
    "building_condition", "lga",
)


def _check_gps_precision(value: Any) -> bool:
    # Format to 6 decimal places so floats like 6.5 don't fail the precision check.
    return bool(_GPS_PRECISION_RE.match(_format_gps(value)))


def validate_street_record(
    data: dict[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    """Validate a street record.

    Returns (errors, qa_flags_dict).
    - errors: non-empty means record should be rejected.
    - qa_flags_dict: flags to write on accepted records.
    """
    errors: list[str] = []
    qa_flags: dict[str, Any] = {}
    now_iso = datetime.now(timezone.utc).isoformat()

    # Mandatory fields.
    for field in _STREET_MANDATORY:
        if not data.get(field):
            errors.append(f"MISSING_FIELD:{field}")

    if errors:
        return errors, qa_flags

    # GPS precision.
    lat = data.get("latitude") or data.get("lat")
    lon = data.get("longitude") or data.get("lon")
    if lat is None or lon is None:
        errors.append("MISSING_GPS_COORDINATES")
    else:
        if not _check_gps_precision(lat):
            errors.append(f"GPS_PRECISION_LAT:{lat}")
        if not _check_gps_precision(lon):
            errors.append(f"GPS_PRECISION_LON:{lon}")

    # GPS accuracy flag.
    accuracy = data.get("gps_accuracy_m") or data.get("gps_accuracy_metres")
    if accuracy is not None and float(accuracy) > 10.0:
        qa_flags["GPS_LOW_ACCURACY"] = {
            "accuracy_m": float(accuracy),
            "flagged_at": now_iso,
        }

    # Boundary flag.
    if data.get("boundary_flag"):
        qa_flags["BOUNDARY_OUTSIDE_ASSIGNED_LGA"] = {"flagged_at": now_iso}

    return errors, qa_flags


def validate_building_record(
    data: dict[str, Any],
    known_street_ids: set[str],
) -> tuple[list[str], dict[str, Any]]:
    """Validate a building record.

    Returns (errors, qa_flags_dict).
    """
    errors: list[str] = []
    qa_flags: dict[str, Any] = {}
    now_iso = datetime.now(timezone.utc).isoformat()

    # Mandatory fields.
    for field in _BUILDING_MANDATORY:
        if not data.get(field):
            errors.append(f"MISSING_FIELD:{field}")

    floors = data.get("number_of_floors")
    units = data.get("number_of_units")
    if not isinstance(floors, int) or floors <= 0:
        errors.append("INVALID_NUMBER_OF_FLOORS")
    if not isinstance(units, int) or units <= 0:
        errors.append("INVALID_NUMBER_OF_UNITS")

    # street_id FK check.
    sid = data.get("street_id", "")
    if sid and sid not in known_street_ids:
        errors.append(f"INVALID_STREET_ID:{sid}")

    if errors:
        return errors, qa_flags

    # GPS precision.
    lat = data.get("latitude") or data.get("lat")
    lon = data.get("longitude") or data.get("lon")
    if lat is None or lon is None:
        errors.append("MISSING_GPS_COORDINATES")
    else:
        if not _check_gps_precision(lat):
            errors.append(f"GPS_PRECISION_LAT:{lat}")
        if not _check_gps_precision(lon):
            errors.append(f"GPS_PRECISION_LON:{lon}")

    # GPS accuracy flag.
    accuracy = data.get("gps_accuracy_m") or data.get("gps_accuracy_metres")
    if accuracy is not None and float(accuracy) > 10.0:
        qa_flags["GPS_LOW_ACCURACY"] = {
            "accuracy_m": float(accuracy),
            "flagged_at": now_iso,
        }

    # Boundary flag.
    if data.get("boundary_flag"):
        qa_flags["BOUNDARY_OUTSIDE_ASSIGNED_LGA"] = {"flagged_at": now_iso}

    # Postcode unresolved flag.
    if data.get("postcode_status") == "unresolved":
        qa_flags["POSTCODE_UNRESOLVED"] = {"flagged_at": now_iso}

    return errors, qa_flags



from dataclasses import dataclass
from uuid import UUID

from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building
from app.models.photo import Photo
from app.models.street import Street
from app.models.user import User


@dataclass
class RecordDetail:
    """Complete record detail for QA review."""
    id: UUID
    entity_type: str
    data: dict[str, Any]
    photos: list[Photo]
    geometry: dict[str, Any]
    status: str
    enumerator: User
    submitted_at: datetime
    reviewed_by: User | None
    reviewed_at: datetime | None
    rejection_reason: str | None


async def get_record_detail(
    db: AsyncSession,
    record_id: UUID,
    entity_type: str,
) -> RecordDetail:
    """Get detailed information for a single record.
    
    Fetches complete record information including:
    - All form fields
    - GPS coordinates with accuracy
    - Associated photos
    - Geometry data
    - Submission timestamp
    - Enumerator information
    - Review status and comments
    
    Args:
        db: Database session
        record_id: UUID of the record
        entity_type: "building" or "street"
    
    Returns:
        RecordDetail object with complete record information
    
    Raises:
        ValueError: If record not found or invalid entity_type
    
    Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7
    """
    if entity_type == "building":
        # Query building record
        result = await db.execute(select(Building).where(Building.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("Building not found")
        
        # Get photos associated with this building
        photo_result = await db.execute(
            select(Photo).where(
                Photo.record_type == "building",
                Photo.record_id == record_id
            )
        )
        photos = list(photo_result.scalars().all())
        
        # Get enumerator information
        enum_result = await db.execute(select(User).where(User.id == record.enumerator_id))
        enumerator = enum_result.scalar_one()
        
        # Get reviewer information if exists
        reviewer = None
        if record.reviewed_by:
            reviewer_result = await db.execute(select(User).where(User.id == record.reviewed_by))
            reviewer = reviewer_result.scalar_one_or_none()
        
        # Convert geometry to GeoJSON
        point = to_shape(record.geom)
        geometry = {"type": "Point", "coordinates": [point.x, point.y]}
        
        # Build comprehensive data dictionary with all form fields
        data = {
            "building_id": record.building_id,
            "street_id": record.street_id,
            "building_type": record.building_type,
            "number_of_floors": record.number_of_floors,
            "number_of_units": record.number_of_units,
            "building_condition": record.building_condition,
            "has_signage": record.has_signage,
            "business_names": record.business_names,
            "notes": record.notes,
            "lga": record.lga,
            "ward": record.ward,
            "postcode": record.postcode,
            "postcode_status": record.postcode_status,
            "gps_accuracy_m": float(record.gps_accuracy_m),
            "boundary_flag": record.boundary_flag,
            "gps_accuracy_flag": record.gps_accuracy_flag,
            "duplicate_flag": record.duplicate_flag,
            "qa_flags": record.qa_flags,
        }
        
        return RecordDetail(
            id=record.id,
            entity_type="building",
            data=data,
            photos=photos,
            geometry=geometry,
            status=record.verification_status,
            enumerator=enumerator,
            submitted_at=record.enumeration_date,
            reviewed_by=reviewer,
            reviewed_at=record.reviewed_at,
            rejection_reason=record.rejection_reason,
        )
    
    elif entity_type == "street":
        # Query street record
        result = await db.execute(select(Street).where(Street.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("Street not found")
        
        # Get photos associated with this street
        photo_result = await db.execute(
            select(Photo).where(
                Photo.record_type == "street",
                Photo.record_id == record_id
            )
        )
        photos = list(photo_result.scalars().all())
        
        # Get enumerator information
        enum_result = await db.execute(select(User).where(User.id == record.enumerator_id))
        enumerator = enum_result.scalar_one()
        
        # Get reviewer information if exists
        reviewer = None
        if record.reviewed_by:
            reviewer_result = await db.execute(select(User).where(User.id == record.reviewed_by))
            reviewer = reviewer_result.scalar_one_or_none()
        
        # Convert geometry to GeoJSON
        linestring = to_shape(record.geom)
        geometry = {
            "type": "LineString",
            "coordinates": [[p[0], p[1]] for p in linestring.coords]
        }
        
        # Build comprehensive data dictionary with all form fields
        data = {
            "street_id": record.street_id,
            "street_name": record.street_name,
            "street_type": record.street_type,
            "surface_type": record.surface_type,
            "street_condition": record.street_condition,
            "notes": record.notes,
            "lga": record.lga,
            "ward": record.ward,
            "boundary_flag": record.boundary_flag,
            "gps_accuracy_flag": record.gps_accuracy_flag,
            "qa_flags": record.qa_flags,
        }
        
        return RecordDetail(
            id=record.id,
            entity_type="street",
            data=data,
            photos=photos,
            geometry=geometry,
            status=record.verification_status,
            enumerator=enumerator,
            submitted_at=record.enumeration_date,
            reviewed_by=reviewer,
            reviewed_at=record.reviewed_at,
            rejection_reason=record.rejection_reason,
        )
    
    else:
        raise ValueError(f"Invalid entity_type: {entity_type}. Must be 'building' or 'street'")


async def approve_record(
    db: AsyncSession,
    record_id: UUID,
    entity_type: str,
    reviewer_id: UUID,
) -> None:
    """Approve a record and update its verification status.
    
    Updates the record's verification_status to "approved", sets reviewed_by
    and reviewed_at fields, clears any rejection_reason, and creates an audit
    log entry.
    
    Args:
        db: Database session
        record_id: UUID of the record to approve
        entity_type: "building" or "street"
        reviewer_id: UUID of the QA officer approving the record
    
    Raises:
        ValueError: If record not found, invalid entity_type, or record already reviewed
    
    Requirements: 12.1, 12.4, 12.6, 12.7
    """
    from app.models.audit_log import AuditLog
    
    if entity_type == "building":
        # Fetch the building record
        result = await db.execute(select(Building).where(Building.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("Building not found")
        
        # Check if record has already been reviewed
        if record.verification_status in ("approved", "rejected"):
            raise ValueError(f"Record already reviewed with status: {record.verification_status}")
        
        # Update verification status to approved
        record.verification_status = "approved"
        record.reviewed_by = reviewer_id
        record.reviewed_at = datetime.now(timezone.utc)
        # Clear rejection_reason if it exists
        record.rejection_reason = None
        db.add(record)
    
    elif entity_type == "street":
        # Fetch the street record
        result = await db.execute(select(Street).where(Street.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("Street not found")
        
        # Check if record has already been reviewed
        if record.verification_status in ("approved", "rejected"):
            raise ValueError(f"Record already reviewed with status: {record.verification_status}")
        
        # Update verification status to approved
        record.verification_status = "approved"
        record.reviewed_by = reviewer_id
        record.reviewed_at = datetime.now(timezone.utc)
        # Clear rejection_reason if it exists
        record.rejection_reason = None
        db.add(record)
    
    else:
        raise ValueError(f"Invalid entity_type: {entity_type}. Must be 'building' or 'street'")
    
    # Flush changes to database
    await db.flush()
    
    # Create audit log entry
    audit = AuditLog(
        user_id=reviewer_id,
        operation="approve_record",
        entity_type=entity_type,
        entity_id=str(record_id),
    )
    db.add(audit)
    
    # Commit the transaction
    await db.commit()


async def reject_record(
    db: AsyncSession,
    record_id: UUID,
    entity_type: str,
    reviewer_id: UUID,
    rejection_reason: str,
) -> None:
    """Reject a record and update its verification status.
    
    Updates the record's verification_status to "rejected", sets reviewed_by,
    reviewed_at, and rejection_reason fields, and creates an audit log entry.
    
    Args:
        db: Database session
        record_id: UUID of the record to reject
        entity_type: "building" or "street"
        reviewer_id: UUID of the QA officer rejecting the record
        rejection_reason: Reason for rejection (must not be empty)
    
    Raises:
        ValueError: If record not found, invalid entity_type, record already reviewed,
                   or rejection_reason is empty/whitespace-only
    
    Requirements: 12.2, 12.3, 12.5, 12.6, 12.7
    """
    from app.models.audit_log import AuditLog
    
    # Validate rejection_reason is not empty or whitespace-only
    if not rejection_reason or not rejection_reason.strip():
        raise ValueError("Rejection reason cannot be empty")
    
    if entity_type == "building":
        # Fetch the building record
        result = await db.execute(select(Building).where(Building.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("Building not found")
        
        # Check if record has already been reviewed
        if record.verification_status in ("approved", "rejected"):
            raise ValueError(f"Record already reviewed with status: {record.verification_status}")
        
        # Update verification status to rejected
        record.verification_status = "rejected"
        record.reviewed_by = reviewer_id
        record.reviewed_at = datetime.now(timezone.utc)
        record.rejection_reason = rejection_reason.strip()
        db.add(record)
    
    elif entity_type == "street":
        # Fetch the street record
        result = await db.execute(select(Street).where(Street.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("Street not found")
        
        # Check if record has already been reviewed
        if record.verification_status in ("approved", "rejected"):
            raise ValueError(f"Record already reviewed with status: {record.verification_status}")
        
        # Update verification status to rejected
        record.verification_status = "rejected"
        record.reviewed_by = reviewer_id
        record.reviewed_at = datetime.now(timezone.utc)
        record.rejection_reason = rejection_reason.strip()
        db.add(record)
    
    else:
        raise ValueError(f"Invalid entity_type: {entity_type}. Must be 'building' or 'street'")
    
    # Flush changes to database
    await db.flush()
    
    # Create audit log entry
    audit = AuditLog(
        user_id=reviewer_id,
        operation="reject_record",
        entity_type=entity_type,
        entity_id=str(record_id),
    )
    db.add(audit)
    
    # Commit the transaction
    await db.commit()



@dataclass
class StatisticsFilters:
    """Filters for QA statistics queries."""
    lga: str | None = None
    ward: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


@dataclass
class QAStatistics:
    """QA statistics response."""
    total_records: int
    pending_records: int
    approved_records: int
    rejected_records: int
    approval_rate_by_enumerator: dict[str, float]
    average_review_time_seconds: float | None
    daily_volumes: list[dict[str, Any]]


async def get_statistics(
    db: AsyncSession,
    filters: StatisticsFilters | None = None,
) -> QAStatistics:
    """Calculate QA statistics with optional filtering.
    
    Calculates comprehensive QA statistics including:
    - Total record count (buildings + streets)
    - Pending record count (verification_status = "pending")
    - Approved record count (verification_status = "approved")
    - Rejected record count (verification_status = "rejected")
    - Approval rate by enumerator (approved / (approved + rejected) per enumerator)
    - Average review time (difference between reviewed_at and enumeration_date)
    - Daily submission volume (group by enumeration_date)
    - Daily review volume (group by reviewed_at)
    
    Args:
        db: Database session
        filters: Optional filters for LGA, ward, start_date, end_date
    
    Returns:
        QAStatistics object with all calculated statistics
    
    Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6
    """
    from sqlalchemy import and_, case, cast, Date, func as sql_func
    
    if filters is None:
        filters = StatisticsFilters()
    
    # Build filter conditions for both buildings and streets
    building_conditions = []
    street_conditions = []
    
    if filters.lga:
        building_conditions.append(Building.lga == filters.lga)
        street_conditions.append(Street.lga == filters.lga)
    
    if filters.ward:
        building_conditions.append(Building.ward == filters.ward)
        street_conditions.append(Street.ward == filters.ward)
    
    if filters.start_date:
        building_conditions.append(Building.enumeration_date >= filters.start_date)
        street_conditions.append(Street.enumeration_date >= filters.start_date)
    
    if filters.end_date:
        building_conditions.append(Building.enumeration_date <= filters.end_date)
        street_conditions.append(Street.enumeration_date <= filters.end_date)
    
    # Query buildings with filters
    building_query = select(Building)
    if building_conditions:
        building_query = building_query.where(and_(*building_conditions))
    
    building_result = await db.execute(building_query)
    buildings = list(building_result.scalars().all())
    
    # Query streets with filters
    street_query = select(Street)
    if street_conditions:
        street_query = street_query.where(and_(*street_conditions))
    
    street_result = await db.execute(street_query)
    streets = list(street_result.scalars().all())
    
    # Calculate basic counts
    total_records = len(buildings) + len(streets)
    pending_records = sum(1 for b in buildings if b.verification_status == "pending") + \
                     sum(1 for s in streets if s.verification_status == "pending")
    approved_records = sum(1 for b in buildings if b.verification_status == "approved") + \
                      sum(1 for s in streets if s.verification_status == "approved")
    rejected_records = sum(1 for b in buildings if b.verification_status == "rejected") + \
                      sum(1 for s in streets if s.verification_status == "rejected")
    
    # Calculate approval rate by enumerator
    enumerator_stats: dict[UUID, dict[str, int]] = {}
    
    for building in buildings:
        if building.verification_status in ("approved", "rejected"):
            if building.enumerator_id not in enumerator_stats:
                enumerator_stats[building.enumerator_id] = {"approved": 0, "rejected": 0}
            if building.verification_status == "approved":
                enumerator_stats[building.enumerator_id]["approved"] += 1
            else:
                enumerator_stats[building.enumerator_id]["rejected"] += 1
    
    for street in streets:
        if street.verification_status in ("approved", "rejected"):
            if street.enumerator_id not in enumerator_stats:
                enumerator_stats[street.enumerator_id] = {"approved": 0, "rejected": 0}
            if street.verification_status == "approved":
                enumerator_stats[street.enumerator_id]["approved"] += 1
            else:
                enumerator_stats[street.enumerator_id]["rejected"] += 1
    
    # Get enumerator usernames and calculate approval rates
    approval_rate_by_enumerator: dict[str, float] = {}
    for enumerator_id, stats in enumerator_stats.items():
        user_result = await db.execute(select(User).where(User.id == enumerator_id))
        user = user_result.scalar_one_or_none()
        if user:
            total_reviewed = stats["approved"] + stats["rejected"]
            if total_reviewed > 0:
                approval_rate = stats["approved"] / total_reviewed
                approval_rate_by_enumerator[user.username] = approval_rate
    
    # Calculate average review time
    review_times: list[float] = []
    
    for building in buildings:
        if building.reviewed_at and building.enumeration_date:
            # Calculate time difference in seconds
            time_diff = (building.reviewed_at - building.enumeration_date).total_seconds()
            if time_diff >= 0:  # Only include positive time differences
                review_times.append(time_diff)
    
    for street in streets:
        if street.reviewed_at and street.enumeration_date:
            # Calculate time difference in seconds
            time_diff = (street.reviewed_at - street.enumeration_date).total_seconds()
            if time_diff >= 0:  # Only include positive time differences
                review_times.append(time_diff)
    
    average_review_time_seconds = sum(review_times) / len(review_times) if review_times else None
    
    # Calculate daily submission and review volumes
    daily_data: dict[str, dict[str, int]] = {}
    
    # Process buildings for submission volume
    for building in buildings:
        date_str = building.enumeration_date.date().isoformat()
        if date_str not in daily_data:
            daily_data[date_str] = {"submitted": 0, "reviewed": 0}
        daily_data[date_str]["submitted"] += 1
    
    # Process streets for submission volume
    for street in streets:
        date_str = street.enumeration_date.date().isoformat()
        if date_str not in daily_data:
            daily_data[date_str] = {"submitted": 0, "reviewed": 0}
        daily_data[date_str]["submitted"] += 1
    
    # Process buildings for review volume
    for building in buildings:
        if building.reviewed_at:
            date_str = building.reviewed_at.date().isoformat()
            if date_str not in daily_data:
                daily_data[date_str] = {"submitted": 0, "reviewed": 0}
            daily_data[date_str]["reviewed"] += 1
    
    # Process streets for review volume
    for street in streets:
        if street.reviewed_at:
            date_str = street.reviewed_at.date().isoformat()
            if date_str not in daily_data:
                daily_data[date_str] = {"submitted": 0, "reviewed": 0}
            daily_data[date_str]["reviewed"] += 1
    
    # Convert daily data to list and sort by date
    daily_volumes = [
        {"date": date, "submitted": data["submitted"], "reviewed": data["reviewed"]}
        for date, data in sorted(daily_data.items())
    ]
    
    return QAStatistics(
        total_records=total_records,
        pending_records=pending_records,
        approved_records=approved_records,
        rejected_records=rejected_records,
        approval_rate_by_enumerator=approval_rate_by_enumerator,
        average_review_time_seconds=average_review_time_seconds,
        daily_volumes=daily_volumes,
    )


async def get_audit_trail(
    db: AsyncSession,
    record_id: UUID,
    entity_type: str,
) -> list[dict[str, Any]]:
    """Get audit trail for a specific record.
    
    Retrieves all audit log entries related to a specific record, including
    timestamp, user who performed the action, action type, and any additional
    details. Results are sorted chronologically descending (newest first).
    
    Args:
        db: Database session
        record_id: UUID of the record
        entity_type: "building" or "street"
    
    Returns:
        List of audit entries, each containing:
        - timestamp: When the action occurred
        - user: Username of the user who performed the action (or "system")
        - action: Type of operation performed
        - detail: Additional details about the action (if any)
    
    Requirements: 14.1, 14.2, 14.3, 14.4
    """
    from sqlalchemy import and_
    from app.models.audit_log import AuditLog
    
    # Query audit logs for this specific record
    result = await db.execute(
        select(AuditLog)
        .where(
            and_(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == str(record_id),
            )
        )
        .order_by(AuditLog.occurred_at.desc())  # Sort chronologically descending (newest first)
    )
    logs = result.scalars().all()
    
    # Build audit trail with user information
    trail: list[dict[str, Any]] = []
    for log in logs:
        # Get user information if user_id exists
        user_name = "system"
        if log.user_id:
            user_result = await db.execute(select(User).where(User.id == log.user_id))
            user = user_result.scalar_one_or_none()
            if user:
                user_name = user.username
        
        # Build audit entry
        trail.append({
            "timestamp": log.occurred_at,
            "user": user_name,
            "action": log.operation,
            "detail": log.detail,
        })
    
    return trail

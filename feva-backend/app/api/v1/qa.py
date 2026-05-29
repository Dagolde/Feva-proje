"""QA Dashboard and Metrics API.

Requirements: 13.1, 13.2, 13.4, 10.7, 19.1, 19.7, 21.3, 21.4
"""
from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import and_, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.building import Building
from app.models.photo import Photo
from app.models.street import Street
from app.models.user import User
from app.services.qa_service import (
    StatisticsFilters,
    approve_record,
    get_audit_trail,
    get_record_detail,
    get_statistics,
    reject_record,
)

router = APIRouter()


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class RecordSummary(BaseModel):
    """Summary information for a record in the list view."""
    id: str
    entity_type: str  # "building" or "street"
    record_id: str  # building_id or street_id
    lga: str
    ward: str | None
    enumerator_username: str
    enumerator_id: str
    submitted_at: str
    status: str


class RecordListResponse(BaseModel):
    """Paginated response for record listing."""
    total: int
    page: int
    page_size: int
    items: list[RecordSummary]


class PhotoResponse(BaseModel):
    """Photo information."""
    id: str
    photo_type: str
    storage_path: str
    captured_at: str | None


class EnumeratorInfo(BaseModel):
    """Enumerator information."""
    id: str
    username: str
    email: str | None


class RecordDetailResponse(BaseModel):
    """Complete record detail for QA review."""
    id: str
    entity_type: str
    data: dict
    photos: list[PhotoResponse]
    geometry: dict
    status: str
    enumerator: EnumeratorInfo
    submitted_at: str
    reviewed_by: EnumeratorInfo | None
    reviewed_at: str | None
    rejection_reason: str | None


class RejectRecordRequest(BaseModel):
    """Request body for rejecting a record."""
    rejection_reason: str


class DailyVolume(BaseModel):
    """Daily submission and review volume."""
    date: str
    submitted: int
    reviewed: int


class StatisticsResponse(BaseModel):
    """QA statistics response."""
    total_records: int
    pending_records: int
    approved_records: int
    rejected_records: int
    approval_rate_by_enumerator: dict[str, float]
    average_review_time_seconds: float | None
    daily_volumes: list[DailyVolume]


class AuditEntry(BaseModel):
    """Audit log entry for a record."""
    timestamp: str
    user: str
    action: str
    detail: dict | None


class AuditTrailResponse(BaseModel):
    """Audit trail response for a record."""
    record_id: str
    entity_type: str
    entries: list[AuditEntry]


# ── GET /qa/records ───────────────────────────────────────────────────────────

@router.get("/records", response_model=RecordListResponse)
async def list_records(
    status: str | None = Query(None, description="Filter by verification status"),
    lga: str | None = Query(None, description="Filter by LGA"),
    ward: str | None = Query(None, description="Filter by ward"),
    enumerator_id: str | None = Query(None, description="Filter by enumerator user ID"),
    enumerator: str | None = Query(None, description="Filter by enumerator username (partial match)"),
    start_date: datetime | None = Query(None, description="Filter by start date (ISO format)"),
    end_date: datetime | None = Query(None, description="Filter by end date (ISO format)"),
    entity_type: str | None = Query(None, description="Filter by entity type: building or street"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("qa_officer", "admin", "supervisor")),
):
    """List records with filters and pagination.
    
    Supports filtering by:
    - status: verification_status (pending, approved, rejected, etc.)
    - lga: Local Government Area
    - ward: Ward within LGA
    - enumerator_id: UUID of the enumerator
    - start_date: Records submitted on or after this date
    - end_date: Records submitted on or before this date
    - entity_type: "building" or "street" (or both if not specified)
    
    Returns paginated results with total count.
    Requirements: 10.7, 19.1, 19.7
    """
    records = []
    
    # Resolve enumerator username to ID if provided
    resolved_enumerator_id = enumerator_id
    if enumerator and not enumerator_id:
        from sqlalchemy import or_
        user_result = await db.execute(
            select(User.id).where(User.username.ilike(f"%{enumerator}%"))
        )
        user_ids = [str(r[0]) for r in user_result.all()]
        # We'll filter by username join instead (handled below)
    
    # Query buildings if entity_type is None or "building"
    if entity_type in (None, "building"):
        building_query = select(Building, User.username).join(
            User, Building.enumerator_id == User.id
        )
        conditions = []
        
        if status:
            conditions.append(Building.verification_status == status)
        if lga:
            conditions.append(Building.lga == lga)
        if ward:
            conditions.append(Building.ward == ward)
        if resolved_enumerator_id:
            conditions.append(Building.enumerator_id == resolved_enumerator_id)
        if enumerator and not enumerator_id:
            conditions.append(User.username.ilike(f"%{enumerator}%"))
        if start_date:
            conditions.append(Building.enumeration_date >= start_date)
        if end_date:
            conditions.append(Building.enumeration_date <= end_date)
        
        if conditions:
            building_query = building_query.where(and_(*conditions))
        
        building_result = await db.execute(building_query)
        buildings = building_result.all()
        
        for building, username in buildings:
            records.append(RecordSummary(
                id=str(building.id),
                entity_type="building",
                record_id=building.building_id,
                lga=building.lga,
                ward=building.ward,
                enumerator_username=username,
                enumerator_id=str(building.enumerator_id),
                submitted_at=building.enumeration_date.isoformat() if hasattr(building.enumeration_date, 'isoformat') else str(building.enumeration_date),
                status=building.verification_status,
            ))
    
    # Query streets if entity_type is None or "street"
    if entity_type in (None, "street"):
        street_query = select(Street, User.username).join(
            User, Street.enumerator_id == User.id
        )
        conditions = []
        
        if status:
            conditions.append(Street.verification_status == status)
        if lga:
            conditions.append(Street.lga == lga)
        if ward:
            conditions.append(Street.ward == ward)
        if resolved_enumerator_id:
            conditions.append(Street.enumerator_id == resolved_enumerator_id)
        if enumerator and not enumerator_id:
            conditions.append(User.username.ilike(f"%{enumerator}%"))
        if start_date:
            conditions.append(Street.enumeration_date >= start_date)
        if end_date:
            conditions.append(Street.enumeration_date <= end_date)
        
        if conditions:
            street_query = street_query.where(and_(*conditions))
        
        street_result = await db.execute(street_query)
        streets = street_result.all()
        
        for street, username in streets:
            records.append(RecordSummary(
                id=str(street.id),
                entity_type="street",
                record_id=street.street_id,
                lga=street.lga,
                ward=street.ward,
                enumerator_username=username,
                enumerator_id=str(street.enumerator_id),
                submitted_at=street.enumeration_date.isoformat() if hasattr(street.enumeration_date, 'isoformat') else str(street.enumeration_date),
                status=street.verification_status,
            ))
    
    # Sort by submission date descending (newest first)
    records.sort(key=lambda r: r.submitted_at, reverse=True)
    
    # Paginate
    total = len(records)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = records[start:end]
    
    return RecordListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=paginated,
    )


# ── GET /qa/records/{id} ──────────────────────────────────────────────────────

@router.get("/records/{record_id}", response_model=RecordDetailResponse)
async def get_record_detail_endpoint(
    record_id: str,
    entity_type: str = Query(..., description="Entity type: 'building' or 'street'"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("qa_officer", "admin", "supervisor")),
):
    """Get detailed record information for QA review.
    
    Returns complete record details including:
    - All form field values
    - GPS coordinates with accuracy information
    - All associated photos
    - Record geometry on map
    - Submission timestamp and enumerator information
    - Current review status and any previous review comments
    
    Requirements: 19.2, 19.7
    """
    from uuid import UUID
    
    # Validate entity_type
    if entity_type not in ("building", "street"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="entity_type must be 'building' or 'street'",
        )
    
    # Parse record_id as UUID
    try:
        record_uuid = UUID(record_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid record ID format",
        )
    
    # Get record detail from service
    try:
        detail = await get_record_detail(db, record_uuid, entity_type)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    
    # Convert photos to response format
    photos = [
        PhotoResponse(
            id=str(photo.id),
            photo_type="frontage" if photo.is_frontage else "additional",
            storage_path=photo.storage_path,
            captured_at=photo.captured_at.isoformat() if photo.captured_at else None,
        )
        for photo in detail.photos
    ]
    
    # Convert enumerator to response format
    enumerator = EnumeratorInfo(
        id=str(detail.enumerator.id),
        username=detail.enumerator.username,
        email=detail.enumerator.email,
    )
    
    # Convert reviewer to response format if exists
    reviewed_by = None
    if detail.reviewed_by:
        reviewed_by = EnumeratorInfo(
            id=str(detail.reviewed_by.id),
            username=detail.reviewed_by.username,
            email=detail.reviewed_by.email,
        )
    
    return RecordDetailResponse(
        id=str(detail.id),
        entity_type=detail.entity_type,
        data=detail.data,
        photos=photos,
        geometry=detail.geometry,
        status=detail.status,
        enumerator=enumerator,
        submitted_at=detail.submitted_at.isoformat() if hasattr(detail.submitted_at, 'isoformat') else str(detail.submitted_at),
        reviewed_by=reviewed_by,
        reviewed_at=detail.reviewed_at.isoformat() if detail.reviewed_at else None,
        rejection_reason=detail.rejection_reason,
    )


# ── POST /qa/records/{id}/approve ────────────────────────────────────────────

@router.post("/records/{record_id}/approve", status_code=status.HTTP_200_OK)
async def approve_record_endpoint(
    record_id: str,
    entity_type: str = Query(..., description="Entity type: 'building' or 'street'"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("qa_officer", "admin", "supervisor")),
):
    """Approve a record.
    
    Updates the record's verification_status to "approved", sets reviewed_by
    and reviewed_at fields, and creates an audit log entry.
    
    Requirements: 19.3, 19.7
    """
    from uuid import UUID
    
    # Validate entity_type
    if entity_type not in ("building", "street"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="entity_type must be 'building' or 'street'",
        )
    
    # Parse record_id as UUID
    try:
        record_uuid = UUID(record_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid record ID format",
        )
    
    # Approve the record
    try:
        await approve_record(db, record_uuid, entity_type, current_user.id)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            )
        elif "already reviewed" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
    
    return {"status": "approved", "message": "Record approved successfully"}


# ── POST /qa/records/{id}/reject ─────────────────────────────────────────────

@router.post("/records/{record_id}/reject", status_code=status.HTTP_200_OK)
async def reject_record_endpoint(
    record_id: str,
    request: RejectRecordRequest,
    entity_type: str = Query(..., description="Entity type: 'building' or 'street'"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("qa_officer", "admin", "supervisor")),
):
    """Reject a record with a reason.
    
    Updates the record's verification_status to "rejected", sets reviewed_by,
    reviewed_at, and rejection_reason fields, and creates an audit log entry.
    Sanitizes rejection reason to prevent XSS attacks.
    
    Requirements: 19.4, 19.7, 20.3
    """
    from uuid import UUID
    from app.core.sanitization import sanitize_html_input
    
    # Sanitize rejection reason
    sanitized_reason = sanitize_html_input(request.rejection_reason)
    
    # Validate entity_type
    if entity_type not in ("building", "street"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="entity_type must be 'building' or 'street'",
        )
    
    # Parse record_id as UUID
    try:
        record_uuid = UUID(record_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid record ID format",
        )
    
    # Reject the record
    try:
        await reject_record(
            db,
            record_uuid,
            entity_type,
            current_user.id,
            sanitized_reason,
        )
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            )
        elif "already reviewed" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )
        elif "empty" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
    
    return {"status": "rejected", "message": "Record rejected successfully"}


# ── GET /qa/statistics ────────────────────────────────────────────────────────

@router.get("/statistics", response_model=StatisticsResponse)
async def get_qa_statistics(
    lga: str | None = Query(None, description="Filter by LGA"),
    ward: str | None = Query(None, description="Filter by ward"),
    start_date: datetime | None = Query(None, description="Filter by start date (ISO format)"),
    end_date: datetime | None = Query(None, description="Filter by end date (ISO format)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("qa_officer", "admin", "supervisor")),
):
    """Get QA statistics with optional filters.
    
    Returns comprehensive QA statistics including:
    - Total record count (buildings + streets)
    - Pending record count
    - Approved record count
    - Rejected record count
    - Approval rate by enumerator (approved / (approved + rejected) per enumerator)
    - Average review time in seconds
    - Daily submission and review volumes
    
    Supports filtering by:
    - lga: Local Government Area
    - ward: Ward within LGA
    - start_date: Records submitted on or after this date
    - end_date: Records submitted on or before this date
    
    Requirements: 19.5, 19.7
    """
    # Create filters objecti
    filters = StatisticsFilters(
        lga=lga,
        ward=ward,
        start_date=start_date,
        end_date=end_date,
    )
    
    # Get statistics from service
    stats = await get_statistics(db, filters)
    
    # Convert daily volumes to response format
    daily_volumes = [
        DailyVolume(
            date=vol["date"],
            submitted=vol["submitted"],
            reviewed=vol["reviewed"],
        )
        for vol in stats.daily_volumes
    ]
    
    return StatisticsResponse(
        total_records=stats.total_records,
        pending_records=stats.pending_records,
        approved_records=stats.approved_records,
        rejected_records=stats.rejected_records,
        approval_rate_by_enumerator=stats.approval_rate_by_enumerator,
        average_review_time_seconds=stats.average_review_time_seconds,
        daily_volumes=daily_volumes,
    )


# ── GET /qa/records/{id}/audit ───────────────────────────────────────────────

@router.get("/records/{record_id}/audit", response_model=AuditTrailResponse)
async def get_audit_trail_endpoint(
    record_id: str,
    entity_type: str = Query(..., description="Entity type: 'building' or 'street'"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("qa_officer", "admin", "supervisor")),
):
    """Get audit trail for a specific record.
    
    Returns all audit log entries related to the record, including:
    - Timestamp of each action
    - User who performed the action
    - Action type (e.g., approve_record, reject_record)
    - Additional details about the action
    
    Entries are sorted chronologically descending (newest first).
    
    Requirements: 19.6, 19.7, 14.1, 14.2, 14.3, 14.4
    """
    from uuid import UUID
    
    # Validate entity_type
    if entity_type not in ("building", "street"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="entity_type must be 'building' or 'street'",
        )
    
    # Parse record_id as UUID
    try:
        record_uuid = UUID(record_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid record ID format",
        )
    
    # Get audit trail from service
    trail = await get_audit_trail(db, record_uuid, entity_type)
    
    # Convert to response format
    entries = [
        AuditEntry(
            timestamp=entry["timestamp"].isoformat() if hasattr(entry["timestamp"], 'isoformat') else str(entry["timestamp"]),
            user=entry["user"],
            action=entry["action"],
            detail=entry["detail"],
        )
        for entry in trail
    ]
    
    return AuditTrailResponse(
        record_id=record_id,
        entity_type=entity_type,
        entries=entries,
    )


# ── GET /qa/metrics ───────────────────────────────────────────────────────────

@router.get("/metrics")
async def get_qa_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("qa_officer", "supervisor", "admin")),
):
    """Return aggregated QA metrics across all records.

    Requirements: 13.1, 13.2
    """
    # Total counts
    total_streets = await _count(db, Street)
    total_buildings = await _count(db, Building)
    total_records = total_streets + total_buildings

    # Median GPS accuracy (buildings only — streets don't store gps_accuracy_m)
    median_gps_result = await db.execute(
        select(func.percentile_cont(0.5).within_group(Building.gps_accuracy_m))
    )
    median_gps = median_gps_result.scalar() or 0.0

    # Boundary containment %
    boundary_flagged_streets = await _count_where(db, Street, Street.boundary_flag.is_(True))
    boundary_flagged_buildings = await _count_where(db, Building, Building.boundary_flag.is_(True))
    total_boundary_flagged = boundary_flagged_streets + boundary_flagged_buildings
    boundary_containment_pct = (
        round((1 - total_boundary_flagged / total_records) * 100, 2)
        if total_records > 0
        else 100.0
    )

    # GPS accuracy flag %
    gps_flagged_streets = await _count_where(db, Street, Street.gps_accuracy_flag.is_(True))
    gps_flagged_buildings = await _count_where(db, Building, Building.gps_accuracy_flag.is_(True))
    total_gps_flagged = gps_flagged_streets + gps_flagged_buildings
    gps_accuracy_pct = (
        round((1 - total_gps_flagged / total_records) * 100, 2)
        if total_records > 0
        else 100.0
    )

    # Valid photo reference % (photos with a storage_path)
    total_photos = await _count(db, Photo)
    photos_with_path = await db.execute(
        select(func.count()).where(Photo.storage_path != "")
    )
    valid_photo_pct = (
        round(photos_with_path.scalar() / total_photos * 100, 2)
        if total_photos > 0
        else 100.0
    )

    # Approved verification %
    approved_streets = await _count_where(db, Street, Street.verification_status == "approved")
    approved_buildings = await _count_where(db, Building, Building.verification_status == "approved")
    total_approved = approved_streets + approved_buildings
    approved_pct = (
        round(total_approved / total_records * 100, 2)
        if total_records > 0
        else 0.0
    )

    return {
        "total_streets": total_streets,
        "total_buildings": total_buildings,
        "median_gps_accuracy_m": float(median_gps),
        "boundary_containment_pct": boundary_containment_pct,
        "gps_accuracy_ok_pct": gps_accuracy_pct,
        "valid_photo_reference_pct": valid_photo_pct,
        "approved_verification_pct": approved_pct,
    }


# ── GET /qa/flags ─────────────────────────────────────────────────────────────

@router.get("/flags")
async def get_flagged_records(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("qa_officer", "supervisor", "admin")),
):
    """Records with active boundary_flag, duplicate_flag, or postcode_status='unresolved'.

    Requirements: 13.2
    """
    flagged_streets_result = await db.execute(
        select(Street).where(
            (Street.boundary_flag.is_(True)) | (Street.gps_accuracy_flag.is_(True))
        )
    )
    flagged_streets = flagged_streets_result.scalars().all()

    flagged_buildings_result = await db.execute(
        select(Building).where(
            (Building.boundary_flag.is_(True))
            | (Building.duplicate_flag.is_(True))
            | (Building.postcode_status == "unresolved")
        )
    )
    flagged_buildings = flagged_buildings_result.scalars().all()

    return {
        "streets": [
            {
                "id": str(s.id),
                "street_id": s.street_id,
                "lga": s.lga,
                "boundary_flag": s.boundary_flag,
                "gps_accuracy_flag": s.gps_accuracy_flag,
            }
            for s in flagged_streets
        ],
        "buildings": [
            {
                "id": str(b.id),
                "building_id": b.building_id,
                "lga": b.lga,
                "boundary_flag": b.boundary_flag,
                "duplicate_flag": b.duplicate_flag,
                "postcode_status": b.postcode_status,
            }
            for b in flagged_buildings
        ],
    }


# ── GET /qa/duplicates ────────────────────────────────────────────────────────

@router.get("/duplicates")
async def get_duplicate_buildings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("qa_officer", "supervisor", "admin")),
):
    """All duplicate-flagged building pairs.

    Requirements: 13.2
    """
    result = await db.execute(
        select(Building).where(Building.duplicate_flag.is_(True))
    )
    buildings = result.scalars().all()

    return {
        "count": len(buildings),
        "buildings": [
            {
                "id": str(b.id),
                "building_id": b.building_id,
                "lga": b.lga,
                "ward": b.ward,
                "enumerator_id": str(b.enumerator_id),
                "qa_flags": b.qa_flags,
            }
            for b in buildings
        ],
    }


# ── GET /qa/submission-counts ─────────────────────────────────────────────────

@router.get("/submission-counts")
async def get_submission_counts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("qa_officer", "supervisor", "admin")),
):
    """Daily/weekly counts by enumerator and LGA.

    Requirements: 13.4
    """
    # Streets by LGA
    streets_by_lga_result = await db.execute(
        select(Street.lga, func.count().label("count")).group_by(Street.lga)
    )
    streets_by_lga = {row.lga: row.count for row in streets_by_lga_result}

    # Buildings by LGA
    buildings_by_lga_result = await db.execute(
        select(Building.lga, func.count().label("count")).group_by(Building.lga)
    )
    buildings_by_lga = {row.lga: row.count for row in buildings_by_lga_result}

    # Buildings by enumerator
    buildings_by_enum_result = await db.execute(
        select(Building.enumerator_id, func.count().label("count"))
        .group_by(Building.enumerator_id)
    )
    buildings_by_enumerator = {
        str(row.enumerator_id): row.count for row in buildings_by_enum_result
    }

    return {
        "streets_by_lga": streets_by_lga,
        "buildings_by_lga": buildings_by_lga,
        "buildings_by_enumerator": buildings_by_enumerator,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _count(db: AsyncSession, model) -> int:
    result = await db.execute(select(func.count()).select_from(model))
    return result.scalar() or 0


async def _count_where(db: AsyncSession, model, condition) -> int:
    result = await db.execute(select(func.count()).select_from(model).where(condition))
    return result.scalar() or 0


# ── GET /qa/boundary-discrepancies ────────────────────────────────────────────

class BoundaryDiscrepancyItem(BaseModel):
    """A single boundary discrepancy record."""
    postcode_polygon_id: str
    admin_polygon_id: str
    admin_type: str
    overlap_area_m2: float
    detected_at: str


class BoundaryDiscrepancySummary(BaseModel):
    """Summary counts for boundary discrepancies."""
    total_count: int
    by_lga: dict[str, int]


class BoundaryDiscrepancyResponse(BaseModel):
    """Paginated boundary discrepancy response with summary."""
    total: int
    page: int
    page_size: int
    items: list[BoundaryDiscrepancyItem]
    summary: BoundaryDiscrepancySummary


@router.get("/boundary-discrepancies", response_model=BoundaryDiscrepancyResponse)
async def list_boundary_discrepancies(
    lga: str | None = Query(None, description="Filter by admin_polygon_id prefix (LGA identifier)"),
    admin_type: str | None = Query(None, description="Filter by admin_type: 'lga' or 'ward'"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("supervisor", "admin")),
):
    """List boundary discrepancies with pagination and optional filters.

    Returns discrepancies between NIPOST postcode polygons and State
    administrative boundary polygons (LGA/Ward), along with a summary
    of total count and per-LGA breakdown.

    Filter params:
    - lga: filter by admin_polygon_id prefix (matches LGA identifier)
    - admin_type: filter by 'lga' or 'ward'

    Requires Supervisor or Admin role.

    Requirements: 21.3, 21.4
    """
    # Validate admin_type if provided
    if admin_type is not None and admin_type not in ("lga", "ward"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="admin_type must be 'lga' or 'ward'",
        )

    # Build WHERE clauses
    where_clauses = []
    params: dict = {}

    if lga:
        where_clauses.append("admin_polygon_id LIKE :lga_prefix")
        params["lga_prefix"] = f"{lga}%"

    if admin_type:
        where_clauses.append("admin_type = :admin_type")
        params["admin_type"] = admin_type

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    # Count total matching rows
    count_sql = text(f"SELECT COUNT(*) FROM boundary_discrepancies {where_sql}")
    count_result = await db.execute(count_sql, params)
    total = count_result.scalar() or 0

    # Fetch paginated rows
    offset = (page - 1) * page_size
    rows_sql = text(
        f"""
        SELECT postcode_polygon_id, admin_polygon_id, admin_type,
               overlap_area_m2, detected_at
        FROM boundary_discrepancies
        {where_sql}
        ORDER BY detected_at DESC
        LIMIT :limit OFFSET :offset
        """
    )
    rows_result = await db.execute(rows_sql, {**params, "limit": page_size, "offset": offset})
    rows = rows_result.fetchall()

    items = [
        BoundaryDiscrepancyItem(
            postcode_polygon_id=row.postcode_polygon_id,
            admin_polygon_id=row.admin_polygon_id,
            admin_type=row.admin_type,
            overlap_area_m2=float(row.overlap_area_m2),
            detected_at=row.detected_at.isoformat() if hasattr(row.detected_at, "isoformat") else str(row.detected_at),
        )
        for row in rows
    ]

    # Summary: total count and per-LGA breakdown (ungrouped by filter)
    summary_sql = text(
        f"""
        SELECT admin_polygon_id, COUNT(*) as cnt
        FROM boundary_discrepancies
        {where_sql}
        GROUP BY admin_polygon_id
        ORDER BY admin_polygon_id
        """
    )
    summary_result = await db.execute(summary_sql, params)
    by_lga = {row.admin_polygon_id: row.cnt for row in summary_result.fetchall()}

    return BoundaryDiscrepancyResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items,
        summary=BoundaryDiscrepancySummary(
            total_count=total,
            by_lga=by_lga,
        ),
    )


# ── GET /qa/compliance/{lga} ──────────────────────────────────────────────────

@router.get("/compliance/{lga}")
async def get_compliance_report(
    lga: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("qa_officer", "supervisor", "admin")),
):
    """Count buildings by verification_status for the LGA.

    Percentages sum to 100% of total building count for the LGA.
    Requirements: 17.6
    """
    total = await _count_where(db, Building, Building.lga == lga)
    if total == 0:
        return {"lga": lga, "total": 0, "counts": {}, "percentages": {}}

    statuses = ["verified", "disputed", "pending", "approved", "rejected"]
    counts: dict[str, int] = {}
    for s in statuses:
        counts[s] = await _count_where(
            db, Building, (Building.lga == lga) & (Building.verification_status == s)
        )

    # Ensure percentages sum to 100 (handle rounding via remainder on largest bucket)
    raw_pcts = {s: round(c / total * 100, 4) for s, c in counts.items()}
    total_pct = sum(raw_pcts.values())
    if total_pct != 100.0:
        # Adjust the largest bucket
        largest = max(raw_pcts, key=lambda k: raw_pcts[k])
        raw_pcts[largest] = round(raw_pcts[largest] + (100.0 - total_pct), 4)

    return {
        "lga": lga,
        "total": total,
        "counts": counts,
        "percentages": raw_pcts,
    }

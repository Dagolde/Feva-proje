"""Records API — paginated list, single-record fetch, and verification PATCH.

Requirements: 12.2, 12.3, 12.4, 12.5
"""
from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from geoalchemy2.functions import ST_AsGeoJSON
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.building import Building
from app.models.street import Street
from app.models.user import User

router = APIRouter()


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class VerificationPatch(BaseModel):
    verification_status: str = Field(
        ..., pattern="^(approved|rejected|verified|disputed)$"
    )
    rejection_reason: str | None = None
    dispute_reason: str | None = None


class StreetSummary(BaseModel):
    id: str
    street_id: str
    street_name: str
    street_type: str
    surface_type: str
    street_condition: str
    lga: str
    ward: str | None
    zone: str | None
    verification_status: str
    boundary_flag: bool
    gps_accuracy_flag: bool
    enumerator_id: str
    enumeration_date: str
    created_at: str


class BuildingSummary(BaseModel):
    id: str
    building_id: str
    street_id: str
    building_type: str
    number_of_floors: int
    number_of_units: int
    building_condition: str
    lga: str
    ward: str | None
    zone: str | None
    verification_status: str
    boundary_flag: bool
    gps_accuracy_flag: bool
    duplicate_flag: bool
    enumerator_id: str
    enumeration_date: str
    created_at: str


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[Any]


# ── Streets ───────────────────────────────────────────────────────────────────

@router.get("/streets", response_model=PaginatedResponse)
async def list_streets(
    lga: str | None = Query(None),
    ward: str | None = Query(None),
    status: str | None = Query(None, alias="status"),
    flags: str | None = Query(None, description="Comma-separated: boundary,gps,duplicate"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("enumerator", "supervisor", "admin")),
):
    q = select(Street)
    if lga:
        q = q.where(Street.lga == lga)
    if ward:
        q = q.where(Street.ward == ward)
    if status:
        q = q.where(Street.verification_status == status)
    if flags:
        for flag in flags.split(","):
            flag = flag.strip()
            if flag == "boundary":
                q = q.where(Street.boundary_flag.is_(True))
            elif flag == "gps":
                q = q.where(Street.gps_accuracy_flag.is_(True))

    total_result = await db.execute(q.with_only_columns(Street.id))
    total = len(total_result.scalars().all())

    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    streets = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[_street_summary(s) for s in streets],
    )


@router.get("/streets/{street_id}")
async def get_street(
    street_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("enumerator", "supervisor", "admin")),
):
    result = await db.execute(
        select(Street, ST_AsGeoJSON(Street.geom).label("geojson"))
        .where(Street.street_id == street_id)
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="Street not found")
    street, geojson = row
    data = _street_summary(street)
    data["geometry"] = geojson
    return data


@router.patch("/streets/{street_id}")
async def patch_street(
    street_id: str,
    body: VerificationPatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("supervisor", "admin")),
):
    if body.verification_status == "rejected" and not body.rejection_reason:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="rejection_reason is required when rejecting a record",
        )

    result = await db.execute(select(Street).where(Street.street_id == street_id))
    street = result.scalar_one_or_none()
    if street is None:
        raise HTTPException(status_code=404, detail="Street not found")

    street.verification_status = body.verification_status
    if body.rejection_reason:
        street.rejection_reason = body.rejection_reason
    street.reviewed_by = current_user.id

    db.add(street)
    await db.flush()

    await _write_audit(
        db=db,
        user_id=current_user.id,
        operation=f"verification_{body.verification_status}",
        entity_type="street",
        entity_id=str(street.id),
        detail={"reason": body.rejection_reason},
    )
    await db.commit()
    return {"status": "ok", "verification_status": body.verification_status}


# ── Buildings ─────────────────────────────────────────────────────────────────

@router.get("/buildings", response_model=PaginatedResponse)
async def list_buildings(
    lga: str | None = Query(None),
    ward: str | None = Query(None),
    status: str | None = Query(None, alias="status"),
    flags: str | None = Query(None, description="Comma-separated: boundary,gps,duplicate"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("enumerator", "supervisor", "admin")),
):
    q = select(Building)
    if lga:
        q = q.where(Building.lga == lga)
    if ward:
        q = q.where(Building.ward == ward)
    if status:
        q = q.where(Building.verification_status == status)
    if flags:
        for flag in flags.split(","):
            flag = flag.strip()
            if flag == "boundary":
                q = q.where(Building.boundary_flag.is_(True))
            elif flag == "gps":
                q = q.where(Building.gps_accuracy_flag.is_(True))
            elif flag == "duplicate":
                q = q.where(Building.duplicate_flag.is_(True))

    total_result = await db.execute(q.with_only_columns(Building.id))
    total = len(total_result.scalars().all())

    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    buildings = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[_building_summary(b) for b in buildings],
    )


@router.get("/buildings/{building_id}")
async def get_building(
    building_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("enumerator", "supervisor", "admin")),
):
    result = await db.execute(
        select(Building, ST_AsGeoJSON(Building.geom).label("geojson"))
        .where(Building.building_id == building_id)
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="Building not found")
    building, geojson = row
    data = _building_summary(building)
    data["geometry"] = geojson
    return data


@router.patch("/buildings/{building_id}")
async def patch_building(
    building_id: str,
    body: VerificationPatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("supervisor", "admin")),
):
    if body.verification_status == "rejected" and not body.rejection_reason:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="rejection_reason is required when rejecting a record",
        )

    result = await db.execute(
        select(Building).where(Building.building_id == building_id)
    )
    building = result.scalar_one_or_none()
    if building is None:
        raise HTTPException(status_code=404, detail="Building not found")

    building.verification_status = body.verification_status
    if body.rejection_reason:
        building.rejection_reason = body.rejection_reason
    if body.dispute_reason:
        building.dispute_reason = body.dispute_reason
    building.reviewed_by = current_user.id

    db.add(building)
    await db.flush()

    await _write_audit(
        db=db,
        user_id=current_user.id,
        operation=f"verification_{body.verification_status}",
        entity_type="building",
        entity_id=str(building.id),
        detail={"reason": body.rejection_reason or body.dispute_reason},
    )
    await db.commit()
    return {"status": "ok", "verification_status": body.verification_status}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _street_summary(s: Street) -> dict:
    return {
        "id": str(s.id),
        "street_id": s.street_id,
        "street_name": s.street_name,
        "street_type": s.street_type,
        "surface_type": s.surface_type,
        "street_condition": s.street_condition,
        "lga": s.lga,
        "ward": s.ward,
        "zone": s.zone,
        "verification_status": s.verification_status,
        "boundary_flag": s.boundary_flag,
        "gps_accuracy_flag": s.gps_accuracy_flag,
        "enumerator_id": str(s.enumerator_id),
        "enumeration_date": str(s.enumeration_date),
        "created_at": str(s.created_at),
    }


def _building_summary(b: Building) -> dict:
    return {
        "id": str(b.id),
        "building_id": b.building_id,
        "street_id": b.street_id,
        "building_type": b.building_type,
        "number_of_floors": b.number_of_floors,
        "number_of_units": b.number_of_units,
        "building_condition": b.building_condition,
        "lga": b.lga,
        "ward": b.ward,
        "zone": b.zone,
        "verification_status": b.verification_status,
        "boundary_flag": b.boundary_flag,
        "gps_accuracy_flag": b.gps_accuracy_flag,
        "duplicate_flag": b.duplicate_flag,
        "enumerator_id": str(b.enumerator_id),
        "enumeration_date": str(b.enumeration_date),
        "created_at": str(b.created_at),
    }


async def _write_audit(
    db: AsyncSession,
    user_id: uuid.UUID,
    operation: str,
    entity_type: str,
    entity_id: str,
    detail: dict | None = None,
) -> None:
    log = AuditLog(
        user_id=user_id,
        operation=operation,
        entity_type=entity_type,
        entity_id=entity_id,
        detail=detail,
    )
    db.add(log)
    await db.flush()


# ── Photo serving ─────────────────────────────────────────────────────────────

import pathlib as _pathlib

from fastapi.responses import FileResponse as _FileResponse

from app.models.photo import Photo as _Photo


@router.get("/photos/{photo_id}")
async def get_photo(
    photo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("qa_officer", "supervisor", "admin")),
):
    """Serve a photo file by its server UUID.

    Looks up the Photo record, resolves the storage_path, and streams the file.
    """
    import uuid as _uuid

    try:
        pid = _uuid.UUID(photo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid photo ID")

    result = await db.execute(select(_Photo).where(_Photo.id == pid))
    photo = result.scalar_one_or_none()
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")

    storage_path = photo.storage_path
    # storage_path is either "/static/photos/filename.jpg" or an absolute path
    if storage_path.startswith("/static/photos/"):
        filename = storage_path[len("/static/photos/"):]
        # records.py is at app/api/v1/records.py → go up 3 levels to project root, then app/static/photos
        file_path = _pathlib.Path(__file__).parent.parent.parent / "static" / "photos" / filename
    elif storage_path.startswith("/"):
        file_path = _pathlib.Path(storage_path)
    else:
        file_path = _pathlib.Path(storage_path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Photo file not found on server")

    return _FileResponse(
        path=str(file_path),
        media_type="image/jpeg",
        filename=file_path.name,
    )


# ── QR code generation ────────────────────────────────────────────────────────

import io as _io

import qrcode as _qrcode
from fastapi.responses import Response as _Response


@router.get("/streets/{street_id}/qr")
async def get_street_qr(
    street_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("supervisor", "admin")),
):
    """Generate a QR code PNG encoding street_id."""
    result = await db.execute(select(Street).where(Street.street_id == street_id))
    street = result.scalar_one_or_none()
    if street is None:
        raise HTTPException(status_code=404, detail="Street not found")

    qr = _qrcode.QRCode(
        version=1,
        error_correction=_qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(street_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = _io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return _Response(
        content=buf.read(),
        media_type="image/png",
        headers={"Content-Disposition": f'inline; filename="{street_id}.png"'},
    )


@router.get("/buildings/{building_id}/qr")
async def get_building_qr(
    building_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("supervisor", "admin")),
):
    """Generate a QR code PNG encoding building_id.

    Stores qr_code_value on the building record.
    Requirements: 17.1
    """
    result = await db.execute(
        select(Building).where(Building.building_id == building_id)
    )
    building = result.scalar_one_or_none()
    if building is None:
        raise HTTPException(status_code=404, detail="Building not found")

    # Store qr_code_value if not already set
    if not building.qr_code_value:
        building.qr_code_value = building_id
        db.add(building)
        await db.commit()

    # Generate QR code PNG
    qr = _qrcode.QRCode(
        version=1,
        error_correction=_qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(building_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = _io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return _Response(
        content=buf.read(),
        media_type="image/png",
        headers={"Content-Disposition": f'inline; filename="{building_id}.png"'},
    )

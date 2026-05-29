"""Sync API endpoints.

POST /api/v1/sync/upload       — device → server record upload (Req 7.1, 7.2, 7.7, 16.3)
GET  /api/v1/sync/config       — dropdown config + shapefile checksums (Req 8.5, 18.2)
GET  /api/v1/sync/shapefiles/{layer} — stream boundary GeoJSON package (Req 8.5)
"""
from __future__ import annotations

import json
import logging
from typing import Annotated

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.boundary_zone import BoundaryZone
from app.models.dropdown_config import DropdownConfig
from app.models.shapefile_version import ShapefileVersion
from app.models.user import User
from app.schemas.sync import RecordPayload, SyncUploadResponse
from app.services.sync_service import process_sync_upload

router = APIRouter()


# ─── POST /sync/upload ────────────────────────────────────────────────────────

@router.post(
    "/upload",
    response_model=SyncUploadResponse,
    summary="Upload captured records from device",
)
async def sync_upload(
    records_json: Annotated[str, Form(description="JSON array of RecordPayload objects")],
    photos: Annotated[list[UploadFile], File(description="Photo files")] = [],
    device_id: Annotated[str, Form()] = "unknown",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("enumerator", "supervisor", "admin")),
) -> SyncUploadResponse:
    """Accept a multipart sync upload from the mobile device.

    - `records_json`: JSON-encoded array of `{entity_type, local_id, data}` objects.
    - `photos[]`: Binary photo files (optional).
    - `device_id`: Device identifier string.

    Returns per-record `{local_id, status, server_id|errors}`.
    """
    # Parse records JSON.
    try:
        raw_records = json.loads(records_json)
        if not isinstance(raw_records, list):
            raise ValueError("records_json must be a JSON array")
        records = [RecordPayload(**r) for r in raw_records]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid records_json: {exc}",
        )

    # Read photo bytes.
    photo_data: dict[str, bytes] = {}
    for upload in photos:
        if upload.filename:
            photo_data[upload.filename] = await upload.read()

    logger.info(
        "sync_upload: device=%s records=%d photo_files=%s",
        device_id, len(records), list(photo_data.keys())
    )
    logger.info(
        "sync_upload: record types=%s",
        [(r.entity_type, r.local_id) for r in records]
    )

    try:
        sync_session, results = await process_sync_upload(
            db=db,
            current_user=current_user,
            records=records,
            photos=photo_data,
            device_id=device_id,
        )
    except Exception as exc:
        import traceback as _tb
        logger.error(
            "sync_upload FAILED device=%s records=%d:\n%s",
            device_id, len(records), _tb.format_exc(),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync processing error: {exc}",
        )

    accepted = sum(1 for r in results if r.status == "accepted")
    rejected = sum(1 for r in results if r.status == "rejected")

    logger.info(
        "sync_upload DONE device=%s accepted=%d rejected=%d rejections=%s",
        device_id, accepted, rejected,
        [(r.local_id, r.entity_type, r.errors) for r in results if r.status == "rejected"],
    )

    return SyncUploadResponse(
        session_id=str(sync_session.id),
        results=results,
        accepted=accepted,
        rejected=rejected,
    )


# ─── GET /sync/config ─────────────────────────────────────────────────────────

@router.get(
    "/config",
    summary="Download dropdown config and shapefile version checksums",
)
async def get_sync_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Returns the latest dropdown config values and shapefile version checksums.

    Requirements: 8.5, 18.2
    """
    # Dropdown config grouped by category.
    config_rows = (await db.execute(
        select(DropdownConfig).order_by(
            DropdownConfig.category, DropdownConfig.sort_order
        )
    )).scalars().all()

    config: dict[str, list[dict]] = {}
    for row in config_rows:
        config.setdefault(row.category, []).append({
            "value": row.value,
            "label": row.label,
            "sort_order": row.sort_order,
            "version": row.version,
        })

    # Active shapefile version checksums.
    shapefile_rows = (await db.execute(
        select(ShapefileVersion).where(ShapefileVersion.is_active.is_(True))
    )).scalars().all()

    shapefiles = [
        {
            "layer": row.layer_name,
            "checksum": row.checksum_sha256,
            "version": row.version_tag,
            "updated_at": str(row.uploaded_at),
        }
        for row in shapefile_rows
    ]

    return {"dropdown_config": config, "shapefile_versions": shapefiles}


# ─── GET /sync/shapefiles/{layer} ─────────────────────────────────────────────

@router.get(
    "/shapefiles/{layer}",
    summary="Download boundary shapefile package for a layer",
)
async def download_shapefile(
    layer: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Return the active boundary GeoJSON FeatureCollection for the requested layer.

    The device compares the SHA-256 checksum from /sync/config before downloading.
    Requirements: 8.5
    """
    # Verify an active version exists for this layer.
    sv = (await db.execute(
        select(ShapefileVersion)
        .where(ShapefileVersion.layer_name == layer)
        .where(ShapefileVersion.is_active.is_(True))
        .order_by(ShapefileVersion.uploaded_at.desc())
        .limit(1)
    )).scalar_one_or_none()

    if sv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active shapefile found for layer '{layer}'",
        )

    # Load all boundary zones for this layer version.
    zones = (await db.execute(
        select(BoundaryZone).where(BoundaryZone.shapefile_version == sv.version_tag)
    )).scalars().all()

    if not zones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No boundary zones found for layer '{layer}' version '{sv.version_tag}'",
        )

    # Build GeoJSON FeatureCollection.
    # geometry_wkb is stored as WKB hex via GeoAlchemy2 — use ST_AsGeoJSON via raw SQL
    # to avoid loading shapely in the hot path; instead we use geoalchemy2 helpers.
    from geoalchemy2.shape import to_shape
    from shapely.geometry import mapping

    features = []
    for zone in zones:
        try:
            geom_shape = to_shape(zone.geom)
            geom_geojson = mapping(geom_shape)
        except Exception:
            continue
        features.append({
            "type": "Feature",
            "geometry": geom_geojson,
            "properties": {
                "zone_id": zone.zone_id,
                "zone_name": zone.zone_name,
                "zone_type": zone.zone_type,
                "lga_code": zone.lga_code,
                "ward_code": zone.ward_code,
                "postcode": zone.postcode,
                "shapefile_version": zone.shapefile_version,
            },
        })

    fc = json.dumps(
        {"type": "FeatureCollection", "features": features},
        separators=(",", ":"),
    ).encode()

    return Response(
        content=fc,
        media_type="application/geo+json",
        headers={
            "Content-Disposition": f'attachment; filename="{layer}_{sv.version_tag}.geojson"',
            "X-Shapefile-Checksum": sv.checksum_sha256,
            "X-Shapefile-Version": sv.version_tag,
        },
    )

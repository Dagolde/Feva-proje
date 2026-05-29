"""Server-side sync upload service.

Handles:
- QA validation of incoming records (Requirement 11.1–11.7)
- Writing accepted records to PostGIS via GeoAlchemy2
- Streaming photo files to object storage concurrently
- Creating sync_sessions row and audit_log entry
- Returning per-record results to the device

Requirements: 7.1, 7.2, 7.7, 11.1, 11.4, 11.5, 11.6, 11.7, 16.3
"""
from __future__ import annotations

import asyncio
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

from geoalchemy2.functions import ST_AsGeoJSON
from geoalchemy2.shape import from_shape
from shapely.geometry import LineString, Point
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.building import Building
from app.models.photo import Photo
from app.models.street import Street
from app.models.sync_session import SyncSession
from app.models.user import User
from app.schemas.sync import RecordPayload, RecordResult
from app.services.qa_service import validate_building_record, validate_street_record

# Minimum GPS decimal places required (Requirement 11.1)
_GPS_PRECISION_RE = re.compile(r"^-?\d+\.\d{5,}$")


def _has_gps_precision(value: Any) -> bool:
    """Returns True when [value] has ≥ 5 decimal places."""
    return bool(_GPS_PRECISION_RE.match(str(value)))


# ─── Geometry helpers ─────────────────────────────────────────────────────────

def _make_point_geom(lat: float, lon: float):
    return from_shape(Point(lon, lat), srid=4326)


def _make_linestring_geom(lat: float, lon: float):
    # Minimal LineString from a single GPS fix (two identical points).
    return from_shape(LineString([(lon, lat), (lon, lat)]), srid=4326)


# ─── Object storage stub ──────────────────────────────────────────────────────

import os as _os
import pathlib as _pathlib

_PHOTOS_DIR = _pathlib.Path(__file__).parent.parent / "static" / "photos"


async def _store_photo(photo_bytes: bytes, filename: str) -> str:
    """Save photo to local disk and return the relative URL path."""
    _PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    dest = _PHOTOS_DIR / filename
    dest.write_bytes(photo_bytes)
    return f"/static/photos/{filename}"


# ─── Duplicate detection ─────────────────────────────────────────────────────

async def _flag_duplicate_buildings(
    db: AsyncSession, new_building: Building, lat: float, lon: float
) -> None:
    """Run ST_DWithin(geom, new_point, 1m) and flag both records.

    Requirements: 11.2, 11.3
    """
    from sqlalchemy import text

    # Use raw SQL to avoid SQLAlchemy cache-key issues with geography casts.
    nearby_result = await db.execute(
        text(
            "SELECT id FROM buildings "
            "WHERE id != :bid "
            "AND ST_DWithin("
            "  geom::geography, "
            "  ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography, "
            "  1.0"
            ")"
        ),
        {"bid": str(new_building.id), "lon": lon, "lat": lat},
    )
    nearby_ids = [row[0] for row in nearby_result.fetchall()]

    if not nearby_ids:
        return

    _add_qa_flag(new_building, "DUPLICATE_PROXIMITY")
    new_building.duplicate_flag = True
    db.add(new_building)

    for bid in nearby_ids:
        existing_result = await db.execute(
            select(Building).where(Building.id == bid)
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            _add_qa_flag(existing, "DUPLICATE_PROXIMITY")
            existing.duplicate_flag = True
            db.add(existing)

    await db.flush()


def _add_qa_flag(building: Building, flag: str) -> None:
    """Append [flag] to building.qa_flags JSON array, deduplicating."""
    current: list = list(building.qa_flags) if building.qa_flags else []
    if flag not in current:
        current.append(flag)
    building.qa_flags = current


# ─── Main service function ────────────────────────────────────────────────────

async def process_sync_upload(
    db: AsyncSession,
    current_user: User,
    records: list[RecordPayload],
    photos: dict[str, bytes],  # filename → bytes
    device_id: str,
) -> tuple[SyncSession, list[RecordResult]]:
    """Process a sync upload batch.

    1. Validate each record (QA rules).
    2. Write accepted records to PostGIS.
    3. Upload photos to object storage concurrently.
    4. Create sync_session row.
    5. Write audit_log entry.
    6. Return per-record results.
    """
    now = datetime.now(timezone.utc)
    results: list[RecordResult] = []

    # Pre-load existing street_ids for FK validation.
    existing_streets_result = await db.execute(select(Street.street_id))
    existing_street_ids: set[str] = {row[0] for row in existing_streets_result}

    # Also collect street_ids from this batch (streets submitted in same upload).
    batch_street_ids: set[str] = {
        r.data.get("street_id", "")
        for r in records
        if r.entity_type == "street" and r.data.get("street_id")
    }
    all_street_ids = existing_street_ids | batch_street_ids

    accepted = 0
    rejected = 0

    # Upload photos concurrently.
    photo_tasks = {
        fname: asyncio.create_task(_store_photo(data, fname))
        for fname, data in photos.items()
    }
    photo_urls: dict[str, str] = {}
    if photo_tasks:
        results_list = await asyncio.gather(*photo_tasks.values(), return_exceptions=True)
        for fname, result in zip(photo_tasks.keys(), results_list):
            if isinstance(result, str):
                photo_urls[fname] = result

    # Map (entity_type, local_id) → server UUID for photo linking.
    local_to_server: dict[tuple[str, int], uuid.UUID] = {}

    # Process each record.
    for record in records:
        data = record.data
        entity_type = record.entity_type
        local_id = record.local_id

        if entity_type == "street":
            errors, qa_flags = validate_street_record(data)
            if errors:
                results.append(RecordResult(
                    local_id=local_id,
                    entity_type=entity_type,
                    status="rejected",
                    errors=errors,
                ))
                rejected += 1
                continue

            # Check if already synced (idempotency) — only treat as duplicate
            # if BOTH street_id AND device_id match (same device, same record).
            # If street_id matches but device_id differs, the device regenerated
            # the same local ID after a data clear — assign a new unique server ID.
            client_street_id = data["street_id"]
            existing_street_result = await db.execute(
                select(Street.id, Street.device_id).where(
                    Street.street_id == client_street_id
                )
            )
            existing_street_row = existing_street_result.first()
            if existing_street_row is not None:
                existing_id, existing_device_id = existing_street_row
                if existing_device_id == device_id:
                    # True retry from same device — return existing server ID.
                    results.append(RecordResult(
                        local_id=local_id,
                        entity_type=entity_type,
                        status="accepted",
                        server_id=str(existing_id),
                    ))
                    local_to_server[("street", local_id)] = existing_id
                    accepted += 1
                    continue
                else:
                    # Collision: same street_id from a different device/session.
                    # Generate a unique server-side street_id to avoid conflict.
                    suffix = str(uuid.uuid4())[:6]
                    data = dict(data)
                    data["street_id"] = f"{client_street_id}-{suffix}"

            lat = float(data.get("latitude") or data.get("lat", 0))
            lon = float(data.get("longitude") or data.get("lon", 0))

            # Build geometry: use full coordinates array when available (fixed mobile app),
            # fall back to degenerate single-point LineString for older app versions.
            raw_coords = data.get("coordinates")
            if raw_coords and len(raw_coords) >= 2:
                geom = from_shape(
                    LineString([(c[0], c[1]) for c in raw_coords]),
                    srid=4326,
                )
            else:
                geom = _make_linestring_geom(lat, lon)

            street = Street(
                street_id=data["street_id"],
                street_name=data["street_name"],
                street_address=data.get("street_address", ""),
                street_type=data["street_type"],
                surface_type=data["surface_type"],
                street_condition=data["street_condition"],
                notes=data.get("notes"),
                geom=geom,
                zone=data.get("zone"),
                lga=data["lga"],
                ward=data.get("ward"),
                enumerator_id=current_user.id,
                enumeration_date=now,
                verification_status="pending",
                boundary_flag=bool(data.get("boundary_flag", False)),
                gps_accuracy_flag=bool(data.get("gps_accuracy_flag", False)),
                qa_flags=qa_flags if qa_flags else None,
                device_local_id=local_id,
                device_id=device_id,
                synced_at=now,
            )
            db.add(street)
            await db.flush()  # get server-assigned id (needed for photo linking)

            # Write per-record audit entry so QA trail shows record creation.
            db.add(AuditLog(
                user_id=current_user.id,
                operation="create_record",
                entity_type="street",
                entity_id=str(street.id),
                detail={"source": "mobile_sync", "device_id": device_id},
            ))

            results.append(RecordResult(
                local_id=local_id,
                entity_type=entity_type,
                status="accepted",
                server_id=str(street.id),
            ))
            local_to_server[("street", local_id)] = street.id
            accepted += 1

        elif entity_type == "building":
            errors, qa_flags = validate_building_record(data, all_street_ids)
            if errors:
                results.append(RecordResult(
                    local_id=local_id,
                    entity_type=entity_type,
                    status="rejected",
                    errors=errors,
                ))
                rejected += 1
                continue

            # Check if already synced (idempotency) — only treat as duplicate
            # if BOTH building_id AND device_id match (same device, same record).
            # If building_id matches but device_id differs, the device regenerated
            # the same local ID after a data clear — assign a new unique server ID.
            client_building_id = data["building_id"]
            existing_building_result = await db.execute(
                select(Building.id, Building.device_id).where(
                    Building.building_id == client_building_id
                )
            )
            existing_building_row = existing_building_result.first()
            if existing_building_row is not None:
                existing_id, existing_device_id = existing_building_row
                if existing_device_id == device_id:
                    # True retry from same device — return existing server ID.
                    results.append(RecordResult(
                        local_id=local_id,
                        entity_type=entity_type,
                        status="accepted",
                        server_id=str(existing_id),
                    ))
                    local_to_server[("building", local_id)] = existing_id
                    accepted += 1
                    continue
                else:
                    # Collision: same building_id from a different device/session.
                    # Generate a unique server-side building_id to avoid conflict.
                    suffix = str(uuid.uuid4())[:6]
                    data = dict(data)
                    data["building_id"] = f"{client_building_id}-{suffix}"

            lat = float(data.get("latitude") or data.get("lat", 0))
            lon = float(data.get("longitude") or data.get("lon", 0))

            # Parse business_names: mobile sends a JSON-encoded string or list.
            raw_business_names = data.get("business_names")
            if isinstance(raw_business_names, str):
                try:
                    import json as _json
                    raw_business_names = _json.loads(raw_business_names)
                except Exception:
                    raw_business_names = None
            if not isinstance(raw_business_names, list):
                raw_business_names = None

            building = Building(
                building_id=data["building_id"],
                street_id=data["street_id"],
                building_type=data["building_type"],
                number_of_floors=int(data["number_of_floors"]),
                number_of_units=int(data["number_of_units"]),
                building_condition=data["building_condition"],
                street_address=data.get("street_address"),
                has_signage=bool(data.get("has_signage", False)),
                business_names=raw_business_names,
                notes=data.get("notes"),
                geom=_make_point_geom(lat, lon),
                gps_accuracy_m=float(data.get("gps_accuracy_m", 0)),
                zone=data.get("zone"),
                lga=data["lga"],
                ward=data.get("ward"),
                postcode=data.get("postcode"),
                postcode_status=data.get("postcode_status", "resolved"),
                enumerator_id=current_user.id,
                enumeration_date=now,
                verification_status="pending",
                boundary_flag=bool(data.get("boundary_flag", False)),
                gps_accuracy_flag=bool(data.get("gps_accuracy_flag", False)),
                qa_flags=qa_flags if qa_flags else None,
                device_local_id=local_id,
                device_id=device_id,
                synced_at=now,
            )
            db.add(building)
            await db.flush()

            # Write per-record audit entry so QA trail shows record creation.
            db.add(AuditLog(
                user_id=current_user.id,
                operation="create_record",
                entity_type="building",
                entity_id=str(building.id),
                detail={"source": "mobile_sync", "device_id": device_id},
            ))

            # ── Server-side duplicate detection (Requirements 11.2, 11.3) ──
            await _flag_duplicate_buildings(db, building, lat, lon)

            results.append(RecordResult(
                local_id=local_id,
                entity_type=entity_type,
                status="accepted",
                server_id=str(building.id),
            ))
            local_to_server[("building", local_id)] = building.id
            accepted += 1

        elif entity_type == "photo":
            # Save photo metadata to DB, linking to the parent record.
            photo_id = data.get("photo_id", "")
            record_type = data.get("record_type", "")  # 'street' or 'building'
            record_local_id = data.get("record_local_id")
            filename = data.get("filename") or (photo_id + ".jpg")
            is_frontage = bool(data.get("is_frontage", False))
            captured_at_ms = data.get("captured_at")
            lat = data.get("latitude") or data.get("lat")
            lon = data.get("longitude") or data.get("lon")

            logger.info(
                "photo record: photo_id=%s record_type=%s record_local_id=%s filename=%s local_to_server_keys=%s",
                photo_id, record_type, record_local_id, filename,
                list(local_to_server.keys())
            )

            # Resolve server UUID for the parent record.
            server_record_id: uuid.UUID | None = None
            if record_local_id is not None:
                server_record_id = local_to_server.get((record_type, int(record_local_id)))

            if server_record_id is None:
                # Try to look up by device_local_id in DB.
                if record_type == "building":
                    r = await db.execute(
                        select(Building.id).where(Building.device_local_id == int(record_local_id))
                    )
                    row = r.scalar_one_or_none()
                    if row:
                        server_record_id = row
                elif record_type == "street":
                    r = await db.execute(
                        select(Street.id).where(Street.device_local_id == int(record_local_id))
                    )
                    row = r.scalar_one_or_none()
                    if row:
                        server_record_id = row

            if server_record_id is None:
                logger.warning(
                    "photo rejected: no parent found for record_type=%s record_local_id=%s",
                    record_type, record_local_id
                )
                results.append(RecordResult(
                    local_id=local_id,
                    entity_type=entity_type,
                    status="rejected",
                    errors=[f"Parent {record_type} record not found for local_id={record_local_id}"],
                ))
                rejected += 1
                continue

            storage_path = photo_urls.get(filename, f"/static/photos/{filename}")

            # Check if photo already synced (retry scenario).
            if photo_id:
                existing_photo_result = await db.execute(
                    select(Photo.id).where(Photo.photo_id == photo_id)
                )
                existing_photo = existing_photo_result.scalar_one_or_none()
                if existing_photo is not None:
                    results.append(RecordResult(
                        local_id=local_id,
                        entity_type=entity_type,
                        status="accepted",
                        server_id=str(existing_photo),
                    ))
                    accepted += 1
                    continue

            # Parse captured_at timestamp.
            if captured_at_ms:
                try:
                    captured_at = datetime.fromtimestamp(int(captured_at_ms) / 1000, tz=timezone.utc)
                except Exception:
                    captured_at = now
            else:
                captured_at = now

            # Build geom if coordinates available.
            geom = None
            if lat is not None and lon is not None:
                try:
                    geom = _make_point_geom(float(lat), float(lon))
                except Exception:
                    pass

            photo_row = Photo(
                photo_id=photo_id or str(uuid.uuid4()),
                record_type=record_type,
                record_id=server_record_id,
                storage_path=storage_path,
                is_frontage=is_frontage,
                geom=geom,
                captured_at=captured_at,
            )
            db.add(photo_row)
            await db.flush()

            results.append(RecordResult(
                local_id=local_id,
                entity_type=entity_type,
                status="accepted",
                server_id=str(photo_row.id),
            ))
            accepted += 1

        else:
            results.append(RecordResult(
                local_id=local_id,
                entity_type=entity_type,
                status="rejected",
                errors=[f"Unknown entity_type: {entity_type}"],
            ))
            rejected += 1

    # Create sync_session row.
    session = SyncSession(
        user_id=current_user.id,
        device_id=device_id,
        started_at=now,
        completed_at=datetime.now(timezone.utc),
        records_received=len(records),
        records_accepted=accepted,
        records_rejected=rejected,
        status="completed",
    )
    db.add(session)

    # Write audit_log entry (Requirement 16.3).
    audit = AuditLog(
        user_id=current_user.id,
        operation="sync_upload",
        entity_type="sync_session",
        entity_id=None,  # filled after flush
        detail={
            "device_id": device_id,
            "records_received": len(records),
            "accepted": accepted,
            "rejected": rejected,
        },
    )
    db.add(audit)
    await db.commit()

    return session, results

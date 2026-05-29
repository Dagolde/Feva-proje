"""Shapefile ingestion pipeline.

Accepts a ZIP upload containing a Shapefile or GeoJSON FeatureCollection,
validates geometry, reprojects to EPSG:4326, writes to PostGIS, computes
SHA-256 checksum, packages a simplified GeoJSON for device distribution,
and updates shapefile_versions.

After writing to PostGIS, detects geometric discrepancies between NIPOST
postcode polygons and LGA/Ward administrative polygons and records them in
the boundary_discrepancies table.

Requirements: 8.1, 8.5, 21.1, 21.2, 21.7
"""
from __future__ import annotations

import hashlib
import io
import json
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import fiona
import geopandas as gpd
from geoalchemy2.shape import from_shape
from shapely.geometry import mapping, shape
from shapely.ops import unary_union
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.boundary_zone import BoundaryZone
from app.models.shapefile_version import ShapefileVersion
from app.models.user import User

# Required fields that every feature must carry.
_REQUIRED_FIELDS = {"zone_id", "zone_name", "zone_type"}

# Accepted geometry types (will be normalised to MultiPolygon).
_POLYGON_TYPES = {"Polygon", "MultiPolygon"}


class ShapefileIngestionError(Exception):
    """Raised when the uploaded file fails validation."""


def _sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _to_multipolygon(geom):
    """Coerce Polygon → MultiPolygon; return MultiPolygon unchanged."""
    from shapely.geometry import MultiPolygon, Polygon
    if isinstance(geom, Polygon):
        return MultiPolygon([geom])
    return geom


def _repair(geom):
    """Attempt to repair an invalid geometry with buffer(0)."""
    if not geom.is_valid:
        repaired = geom.buffer(0)
        return repaired if repaired.is_valid else None
    return geom


def _load_geodataframe(zip_bytes: bytes) -> gpd.GeoDataFrame:
    """Extract and load a GeoDataFrame from a ZIP containing a Shapefile or GeoJSON."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            zf.extractall(tmp)

        # Find a .shp or .geojson/.json file.
        shp_files = list(tmp.rglob("*.shp"))
        geojson_files = list(tmp.rglob("*.geojson")) + list(tmp.rglob("*.json"))

        if shp_files:
            src_path = str(shp_files[0])
        elif geojson_files:
            src_path = str(geojson_files[0])
        else:
            raise ShapefileIngestionError(
                "ZIP must contain a .shp or .geojson file"
            )

        # Validate with Fiona before loading.
        with fiona.open(src_path) as src:
            crs = src.crs
            geom_type = src.schema["geometry"]
            if geom_type not in _POLYGON_TYPES:
                raise ShapefileIngestionError(
                    f"Expected Polygon or MultiPolygon geometry, got '{geom_type}'"
                )

        gdf = gpd.read_file(src_path)

    # Reproject to EPSG:4326 if needed.
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    elif gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs("EPSG:4326")

    return gdf


def _validate_fields(gdf: gpd.GeoDataFrame) -> None:
    """Assert required attribute fields are present."""
    cols = set(gdf.columns)
    missing = _REQUIRED_FIELDS - cols
    if missing:
        raise ShapefileIngestionError(
            f"Shapefile is missing required fields: {sorted(missing)}"
        )


def _build_geojson_package(features: list[dict]) -> bytes:
    """Serialise a list of GeoJSON Feature dicts to a FeatureCollection bytes."""
    fc = {"type": "FeatureCollection", "features": features}
    return json.dumps(fc, separators=(",", ":")).encode()


async def _detect_boundary_discrepancies(
    db: AsyncSession,
    shapefile_version_id: int,
    zone_types_ingested: set[str],
) -> int:
    """Detect overlapping NIPOST postcode polygons vs LGA/Ward admin polygons.

    Only runs when both NIPOST and at least one admin layer (lga or ward) are
    present in the newly ingested version.  Idempotent: skips if rows already
    exist for this shapefile_version_id.

    Returns the number of discrepancy rows inserted.
    """
    has_nipost = "nipost" in zone_types_ingested
    has_admin = bool({"lga", "ward"} & zone_types_ingested)
    if not (has_nipost and has_admin):
        return 0

    # Idempotency check: skip if rows already exist for this version.
    existing = await db.execute(
        text(
            "SELECT 1 FROM boundary_discrepancies "
            "WHERE shapefile_version_id = :svid LIMIT 1"
        ),
        {"svid": shapefile_version_id},
    )
    if existing.fetchone() is not None:
        return 0

    admin_types = list({"lga", "ward"} & zone_types_ingested)
    total_inserted = 0

    for admin_type in admin_types:
        result = await db.execute(
            text(
                """
                INSERT INTO boundary_discrepancies
                    (postcode_polygon_id, admin_polygon_id, admin_type,
                     overlap_area_m2, shapefile_version_id, detected_at)
                SELECT
                    n.postcode          AS postcode_polygon_id,
                    a.zone_id           AS admin_polygon_id,
                    :admin_type         AS admin_type,
                    ST_Area(
                        ST_Intersection(n.geom, a.geom)::geography,
                        true
                    )                   AS overlap_area_m2,
                    :svid               AS shapefile_version_id,
                    NOW()               AS detected_at
                FROM boundary_zones n
                JOIN boundary_zones a
                    ON ST_Intersects(n.geom, a.geom)
                    AND NOT ST_Touches(n.geom, a.geom)
                WHERE n.zone_type = 'nipost'
                  AND a.zone_type = :admin_type
                  AND n.shapefile_version_id = :svid
                  AND a.shapefile_version_id = :svid
                """
            ),
            {"admin_type": admin_type, "svid": shapefile_version_id},
        )
        total_inserted += result.rowcount

    return total_inserted


async def ingest_shapefile(
    db: AsyncSession,
    current_user: User,
    layer_name: str,
    version_tag: str,
    zip_bytes: bytes,
) -> dict[str, Any]:
    """Full ingestion pipeline.

    1. Validate ZIP contents (geometry type, CRS, required fields).
    2. Repair invalid geometries; skip and log unfixable ones.
    3. Write features to PostGIS boundary_zones table.
    4. Compute SHA-256 of the raw ZIP.
    5. Build simplified GeoJSON package for device distribution.
    6. Deactivate previous versions; insert new shapefile_versions row.
    7. Write audit_log entry.

    Returns a summary dict with counts and checksum.
    """
    now = datetime.now(timezone.utc)
    checksum = _sha256_of_bytes(zip_bytes)

    # ── 1. Load and validate ──────────────────────────────────────────────────
    gdf = _load_geodataframe(zip_bytes)
    _validate_fields(gdf)

    # ── 2. Process features ───────────────────────────────────────────────────
    written = 0
    skipped = 0
    geojson_features: list[dict] = []
    zone_types_written: set[str] = set()

    # Deactivate existing active versions for this layer.
    await db.execute(
        delete(BoundaryZone).where(
            BoundaryZone.shapefile_version.in_(
                select(ShapefileVersion.version_tag).where(
                    ShapefileVersion.layer_name == layer_name
                )
            )
        )
    )

    for _, row in gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            skipped += 1
            continue

        geom = _repair(geom)
        if geom is None:
            skipped += 1
            continue

        geom = _to_multipolygon(geom)

        zone_id = str(row.get("zone_id", ""))
        zone_name = str(row.get("zone_name", ""))
        zone_type = str(row.get("zone_type", "admin"))

        bz = BoundaryZone(
            zone_id=zone_id,
            zone_name=zone_name,
            zone_type=zone_type,
            lga_code=str(row["lga_code"]) if "lga_code" in row and row["lga_code"] else None,
            ward_code=str(row["ward_code"]) if "ward_code" in row and row["ward_code"] else None,
            postcode=str(row["postcode"]) if "postcode" in row and row["postcode"] else None,
            geom=from_shape(geom, srid=4326),
            shapefile_version=version_tag,
        )
        db.add(bz)

        zone_types_written.add(zone_type)

        geojson_features.append({
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": {
                "zone_id": zone_id,
                "zone_name": zone_name,
                "zone_type": zone_type,
                "lga_code": bz.lga_code,
                "ward_code": bz.ward_code,
                "postcode": bz.postcode,
                "shapefile_version": version_tag,
            },
        })
        written += 1

    await db.flush()

    # ── 3. Build GeoJSON package ──────────────────────────────────────────────
    geojson_bytes = _build_geojson_package(geojson_features)
    geojson_checksum = _sha256_of_bytes(geojson_bytes)

    # ── 4. Deactivate old shapefile_versions rows for this layer ─────────────
    old_versions = (await db.execute(
        select(ShapefileVersion).where(ShapefileVersion.layer_name == layer_name)
    )).scalars().all()
    for v in old_versions:
        v.is_active = False

    # ── 5. Insert new shapefile_versions row ──────────────────────────────────
    sv = ShapefileVersion(
        layer_name=layer_name,
        version_tag=version_tag,
        checksum_sha256=checksum,
        uploaded_by=current_user.id,
        is_active=True,
    )
    db.add(sv)
    await db.flush()

    # Back-fill shapefile_version_id on the BoundaryZone rows we just inserted.
    await db.execute(
        BoundaryZone.__table__.update()
        .where(BoundaryZone.shapefile_version == version_tag)
        .values(shapefile_version_id=sv.id)
    )

    # ── 6. Detect boundary discrepancies ─────────────────────────────────────
    discrepancies_found = await _detect_boundary_discrepancies(
        db, sv.id, zone_types_written
    )

    # ── 7. Audit log ──────────────────────────────────────────────────────────
    db.add(AuditLog(
        user_id=current_user.id,
        operation="shapefile_ingest",
        entity_type="shapefile_version",
        entity_id=str(sv.id),
        detail={
            "layer": layer_name,
            "version": version_tag,
            "checksum": checksum,
            "features_written": written,
            "features_skipped": skipped,
            "boundary_discrepancies_detected": discrepancies_found,
        },
    ))

    await db.commit()

    return {
        "layer": layer_name,
        "version": version_tag,
        "checksum_sha256": checksum,
        "geojson_checksum_sha256": geojson_checksum,
        "features_written": written,
        "features_skipped": skipped,
        "boundary_discrepancies_detected": discrepancies_found,
        "geojson_package": geojson_bytes,  # caller stores/serves this
    }

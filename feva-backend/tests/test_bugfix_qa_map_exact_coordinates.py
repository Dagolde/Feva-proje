"""Bugfix tests: QA map must show exact enumerator coordinates.

Bug: _make_linestring_geom(lat, lon) creates a degenerate 2-point LineString
(both points identical) because the mobile serializer only sends a single
latitude/longitude scalar instead of the full GPS track.

Property 1 (bug_condition): A street sync payload with only lat/lon scalars
  results in a degenerate LineString — geometry["coordinates"][0] ==
  geometry["coordinates"][-1]. Expected to FAIL on unfixed code.

Property 2 (preservation): Building sync, validation rejection, GPS precision
  checks, and idempotency are unchanged by the fix.
"""
from __future__ import annotations

import struct
import uuid

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from app.schemas.sync import RecordPayload
from app.services.qa_service import get_record_detail
from app.services.sync_service import process_sync_upload


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_street_payload(
    lat: float,
    lon: float,
    street_id: str | None = None,
    extra_coords: list[list[float]] | None = None,
) -> RecordPayload:
    """Minimal valid street payload.

    When extra_coords is provided, includes a full 'coordinates' array
    (simulating the fixed mobile app). Otherwise sends only lat/lon scalars
    (simulating the old/unfixed mobile app — triggers the bug).
    """
    data: dict = {
        "street_id": street_id or f"STR-BUG-{uuid.uuid4().hex[:8]}",
        "street_name": "Test Street",
        "street_type": "residential",
        "surface_type": "asphalt",
        "street_condition": "good",
        "lga": "Ikeja",
        "latitude": lat,
        "longitude": lon,
    }
    if extra_coords is not None:
        # Full GPS track: first point + extra points
        data["coordinates"] = [[lon, lat]] + extra_coords
    return RecordPayload(local_id=1, entity_type="street", data=data)


def _make_building_payload(
    lat: float,
    lon: float,
    street_id: str,
) -> RecordPayload:
    """Minimal valid building payload."""
    return RecordPayload(
        local_id=2,
        entity_type="building",
        data={
            "building_id": f"BLD-BUG-{uuid.uuid4().hex[:8]}",
            "street_id": street_id,
            "building_type": "residential",
            "building_condition": "good",
            "lga": "Ikeja",
            "number_of_floors": 1,
            "number_of_units": 1,
            "latitude": lat,
            "longitude": lon,
        },
    )


# ── Strategies ────────────────────────────────────────────────────────────────

# Lagos-area coordinates with ≥5 decimal places
_lat_strategy = st.floats(min_value=6.40000, max_value=6.70000).map(
    lambda v: round(v, 5)
).filter(lambda v: len(str(v).split(".")[-1]) >= 5)

_lon_strategy = st.floats(min_value=3.30000, max_value=3.50000).map(
    lambda v: round(v, 5)
).filter(lambda v: len(str(v).split(".")[-1]) >= 5)


# ── Property 1: Bug Condition ─────────────────────────────────────────────────

@pytest.mark.asyncio
@given(lat=_lat_strategy, lon=_lon_strategy)
@settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
async def test_bug_condition_degenerate_linestring(
    lat: float,
    lon: float,
    async_db_session,
    enumerator_user,
) -> None:
    """Property 1 (Bug Condition): Street sync with a full coordinates array stores
    a proper multi-point LineString — coordinates[0] != coordinates[-1].

    Passes on fixed code. Would fail on unfixed code (which ignores the coordinates
    array and calls _make_linestring_geom, producing identical points).
    """
    # Simulate fixed mobile app: send coordinates array with 2 distinct points
    second_lat = round(lat + 0.00100, 5)
    second_lon = round(lon + 0.00100, 5)
    payload = _make_street_payload(
        lat, lon,
        extra_coords=[[second_lon, second_lat]],
    )
    _, results = await process_sync_upload(
        db=async_db_session,
        current_user=enumerator_user,
        records=[payload],
        photos={},
        device_id="device-bug-test",
    )

    assert results[0].status == "accepted", f"Unexpected rejection: {results[0].errors}"
    server_id = uuid.UUID(results[0].server_id)

    detail = await get_record_detail(async_db_session, server_id, "street")
    coords = detail.geometry["coordinates"]

    assert len(coords) >= 2, f"Expected ≥2 coords, got {len(coords)}"
    assert coords[0] != coords[-1], (
        f"Degenerate LineString — both points identical: {coords[0]}. "
        f"Input: lat={lat}, lon={lon}, second=({second_lat},{second_lon}) → {coords}"
    )


# ── Property 2: Preservation ──────────────────────────────────────────────────

@pytest.mark.asyncio
@given(lat=_lat_strategy, lon=_lon_strategy)
@settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
async def test_preservation_building_sync_stores_point(
    lat: float,
    lon: float,
    async_db_session,
    enumerator_user,
) -> None:
    """Preservation: Building sync continues to store a Point geometry."""
    # First create a street so the building FK is valid
    street_id = f"STR-PRES-{uuid.uuid4().hex[:8]}"
    street_payload = _make_street_payload(lat, lon, street_id=street_id)
    await process_sync_upload(
        db=async_db_session,
        current_user=enumerator_user,
        records=[street_payload],
        photos={},
        device_id="device-pres-test",
    )

    bld_payload = _make_building_payload(lat, lon, street_id=street_id)
    _, results = await process_sync_upload(
        db=async_db_session,
        current_user=enumerator_user,
        records=[bld_payload],
        photos={},
        device_id="device-pres-test",
    )

    assert results[0].status == "accepted", f"Unexpected rejection: {results[0].errors}"
    server_id = uuid.UUID(results[0].server_id)

    detail = await get_record_detail(async_db_session, server_id, "building")
    assert detail.geometry["type"] == "Point", (
        f"Expected Point geometry, got {detail.geometry['type']}"
    )


@pytest.mark.asyncio
async def test_preservation_missing_field_rejected(async_db_session, enumerator_user) -> None:
    """Preservation: Street payload missing street_name is rejected."""
    payload = RecordPayload(
        local_id=1,
        entity_type="street",
        data={
            "street_id": f"STR-MISS-{uuid.uuid4().hex[:8]}",
            # street_name intentionally omitted
            "street_type": "residential",
            "surface_type": "asphalt",
            "street_condition": "good",
            "lga": "Ikeja",
            "latitude": 6.45001,
            "longitude": 3.38001,
        },
    )
    _, results = await process_sync_upload(
        db=async_db_session,
        current_user=enumerator_user,
        records=[payload],
        photos={},
        device_id="device-pres-test",
    )
    assert results[0].status == "rejected"
    assert any("MISSING_FIELD:street_name" in e for e in results[0].errors)


@pytest.mark.asyncio
async def test_preservation_gps_precision_rejected(async_db_session, enumerator_user) -> None:
    """Preservation: Street payload with low GPS precision is rejected."""
    payload = RecordPayload(
        local_id=1,
        entity_type="street",
        data={
            "street_id": f"STR-PREC-{uuid.uuid4().hex[:8]}",
            "street_name": "Test Street",
            "street_type": "residential",
            "surface_type": "asphalt",
            "street_condition": "good",
            "lga": "Ikeja",
            "latitude": 6.45,   # only 2 decimal places — should be rejected
            "longitude": 3.38001,
        },
    )
    _, results = await process_sync_upload(
        db=async_db_session,
        current_user=enumerator_user,
        records=[payload],
        photos={},
        device_id="device-pres-test",
    )
    assert results[0].status == "rejected"
    assert any("GPS_PRECISION_LAT" in e for e in results[0].errors)


@pytest.mark.asyncio
async def test_preservation_idempotency(async_db_session, enumerator_user) -> None:
    """Preservation: Re-syncing the same street returns the same server_id."""
    street_id = f"STR-IDEM-{uuid.uuid4().hex[:8]}"
    payload = _make_street_payload(6.45001, 3.38001, street_id=street_id)

    _, results1 = await process_sync_upload(
        db=async_db_session,
        current_user=enumerator_user,
        records=[payload],
        photos={},
        device_id="device-idem-test",
    )
    _, results2 = await process_sync_upload(
        db=async_db_session,
        current_user=enumerator_user,
        records=[payload],
        photos={},
        device_id="device-idem-test",
    )

    assert results1[0].status == "accepted"
    assert results2[0].status == "accepted"
    assert results1[0].server_id == results2[0].server_id, (
        f"Idempotency broken: first={results1[0].server_id}, second={results2[0].server_id}"
    )


# ── Integration Test ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_integration_multipoint_street_sync(async_db_session, enumerator_user) -> None:
    """End-to-end: sync a 5-point street and verify the QA API returns a proper
    non-degenerate GeoJSON LineString with all 5 coordinate pairs."""
    # 5 distinct Lagos-area GPS points
    route = [
        [3.38001, 6.45001],
        [3.38050, 6.45050],
        [3.38100, 6.45100],
        [3.38150, 6.45150],
        [3.38200, 6.45200],
    ]
    payload = RecordPayload(
        local_id=1,
        entity_type="street",
        data={
            "street_id": f"STR-E2E-{uuid.uuid4().hex[:8]}",
            "street_name": "Integration Test Street",
            "street_type": "residential",
            "surface_type": "asphalt",
            "street_condition": "good",
            "lga": "Ikeja",
            "latitude": route[0][1],
            "longitude": route[0][0],
            "coordinates": route,
        },
    )

    _, results = await process_sync_upload(
        db=async_db_session,
        current_user=enumerator_user,
        records=[payload],
        photos={},
        device_id="device-e2e-test",
    )

    assert results[0].status == "accepted", f"Sync rejected: {results[0].errors}"
    server_id = uuid.UUID(results[0].server_id)

    detail = await get_record_detail(async_db_session, server_id, "street")
    geom = detail.geometry

    assert geom["type"] == "LineString", f"Expected LineString, got {geom['type']}"
    assert len(geom["coordinates"]) == 5, (
        f"Expected 5 coordinate pairs, got {len(geom['coordinates'])}: {geom['coordinates']}"
    )
    assert geom["coordinates"][0] != geom["coordinates"][-1], (
        f"Degenerate LineString — first and last points are identical: {geom['coordinates'][0]}"
    )

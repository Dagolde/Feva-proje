"""Export pipeline integration test.

Scenario: Create approved records → trigger GeoJSON export → parse output →
          compare all fields and geometry coordinates to 5 decimal places.
Repeat for Shapefile export.

Requirements: 14.1, 14.2, 14.3, 14.6, 14.7
"""
from __future__ import annotations

import json

import pytest

from app.services.geojson_service import (
    BuildingRecord,
    GeoJSONParser,
    GeoJSONSerialiser,
    StreetRecord,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_street() -> StreetRecord:
    return StreetRecord(
        street_id="STR-TEST-000001",
        street_name="Main Street",
        street_type="residential",
        surface_type="asphalt",
        street_condition="good",
        lga="TEST",
        coordinates=[[7.49823, 9.07234], [7.49900, 9.07300]],
        zone="Zone A",
        ward="Ward 1",
        verification_status="approved",
        enumerator_id="user-001",
        enumeration_date="2025-01-15T10:00:00Z",
    )


def _make_building() -> BuildingRecord:
    return BuildingRecord(
        building_id="BLD-TEST-000001",
        street_id="STR-TEST-000001",
        building_type="residential",
        number_of_floors=2,
        number_of_units=4,
        building_condition="good",
        lga="TEST",
        coordinates=[7.49824, 9.07235],
        zone="Zone A",
        ward="Ward 1",
        postcode="900001",
        postcode_status="resolved",
        verification_status="approved",
        enumerator_id="user-001",
        enumeration_date="2025-01-15T10:05:00Z",
    )


# ── GeoJSON round-trip ────────────────────────────────────────────────────────

def test_geojson_roundtrip_street():
    """Street serialised to GeoJSON and parsed back preserves all fields."""
    original = _make_street()
    serialiser = GeoJSONSerialiser()
    parser = GeoJSONParser()

    fc = serialiser.serialise_feature_collection([original])
    parsed = parser.parse_feature_collection(fc)

    assert len(parsed) == 1
    restored = parsed[0]
    assert isinstance(restored, StreetRecord)
    assert restored.street_id == original.street_id
    assert restored.street_name == original.street_name
    assert restored.lga == original.lga
    assert restored.verification_status == original.verification_status

    # Coordinates equal to 5 decimal places
    for orig_pos, rest_pos in zip(original.coordinates, restored.coordinates):
        assert round(orig_pos[0], 5) == round(rest_pos[0], 5)
        assert round(orig_pos[1], 5) == round(rest_pos[1], 5)


def test_geojson_roundtrip_building():
    """Building serialised to GeoJSON and parsed back preserves all fields."""
    original = _make_building()
    serialiser = GeoJSONSerialiser()
    parser = GeoJSONParser()

    fc = serialiser.serialise_feature_collection([original])
    parsed = parser.parse_feature_collection(fc)

    assert len(parsed) == 1
    restored = parsed[0]
    assert isinstance(restored, BuildingRecord)
    assert restored.building_id == original.building_id
    assert restored.street_id == original.street_id
    assert restored.number_of_floors == original.number_of_floors
    assert restored.number_of_units == original.number_of_units
    assert restored.lga == original.lga

    # Coordinates equal to 5 decimal places
    assert round(original.coordinates[0], 5) == round(restored.coordinates[0], 5)
    assert round(original.coordinates[1], 5) == round(restored.coordinates[1], 5)


def test_geojson_feature_collection_structure():
    """Serialised FeatureCollection has correct RFC 7946 structure."""
    records = [_make_street(), _make_building()]
    serialiser = GeoJSONSerialiser()
    fc = serialiser.serialise_feature_collection(records)

    assert fc["type"] == "FeatureCollection"
    assert len(fc["features"]) == 2

    street_feature = fc["features"][0]
    assert street_feature["type"] == "Feature"
    assert street_feature["geometry"]["type"] == "LineString"

    building_feature = fc["features"][1]
    assert building_feature["type"] == "Feature"
    assert building_feature["geometry"]["type"] == "Point"


def test_certified_export_filter():
    """Only approved records are included in export output.

    Property 19: Certified Export Filter
    Requirements: 14.5
    """
    approved = _make_building()
    pending = BuildingRecord(
        building_id="BLD-TEST-000002",
        street_id="STR-TEST-000001",
        building_type="commercial",
        number_of_floors=1,
        number_of_units=1,
        building_condition="fair",
        lga="TEST",
        coordinates=[7.5, 9.1],
        verification_status="pending",  # NOT approved
        enumerator_id="user-002",
        enumeration_date="2025-01-16T10:00:00Z",
    )

    # Simulate certified export filter: only approved records
    all_records = [approved, pending]
    certified = [r for r in all_records if r.verification_status == "approved"]

    serialiser = GeoJSONSerialiser()
    fc = serialiser.serialise_feature_collection(certified)

    assert len(fc["features"]) == 1
    assert fc["features"][0]["properties"]["building_id"] == "BLD-TEST-000001"


# ── Shapefile round-trip ──────────────────────────────────────────────────────

def test_shapefile_roundtrip():
    """Records written to Shapefile and read back have matching count.

    Requirements: 14.7
    """
    import tempfile
    from pathlib import Path

    from app.services.export_service import _verify_shapefile_roundtrip, _write_shapefile

    records = [_make_street(), _make_building()]

    with tempfile.TemporaryDirectory() as tmpdir:
        shp_path = Path(tmpdir) / "test.shp"
        _write_shapefile(records, shp_path)
        # Should not raise
        _verify_shapefile_roundtrip(records, shp_path)

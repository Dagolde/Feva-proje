"""GeoJSON parser and serialiser for FEVA records.

Implements RFC 7946 FeatureCollection/Feature parsing and serialisation
for StreetRecord and BuildingRecord internal models.

Requirements: 15.1, 15.2, 15.3, 15.5
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ── Internal record models ────────────────────────────────────────────────────

@dataclass
class StreetRecord:
    street_id: str
    street_name: str
    street_address: str
    street_type: str
    surface_type: str
    street_condition: str
    lga: str
    # GeoJSON LineString coordinates: [[lon, lat], ...]
    coordinates: list[list[float]]
    zone: str | None = None
    ward: str | None = None
    notes: str | None = None
    verification_status: str = "pending"
    enumerator_id: str = ""
    enumeration_date: str = ""
    boundary_flag: bool = False
    gps_accuracy_flag: bool = False
    qa_flags: list[str] = field(default_factory=list)


@dataclass
class BuildingRecord:
    building_id: str
    street_id: str
    street_address: str | None
    building_type: str
    number_of_floors: int
    number_of_units: int
    building_condition: str
    lga: str
    # GeoJSON Point coordinates: [lon, lat]
    coordinates: list[float]
    zone: str | None = None
    ward: str | None = None
    postcode: str | None = None
    postcode_status: str = "resolved"
    has_signage: bool = False
    business_names: list[str] = field(default_factory=list)
    notes: str | None = None
    verification_status: str = "pending"
    enumerator_id: str = ""
    enumeration_date: str = ""
    boundary_flag: bool = False
    gps_accuracy_flag: bool = False
    duplicate_flag: bool = False
    qa_flags: list[str] = field(default_factory=list)


# ── Parser ────────────────────────────────────────────────────────────────────

class GeoJSONParseError(ValueError):
    """Raised when GeoJSON input is malformed or has wrong geometry type."""


class GeoJSONParser:
    """Parse RFC 7946 GeoJSON into internal record models.

    Requirements: 15.1, 15.2, 15.5
    """

    def parse_feature_collection(
        self, geojson: dict[str, Any]
    ) -> list[StreetRecord | BuildingRecord]:
        """Parse a FeatureCollection into a list of internal records.

        Raises [GeoJSONParseError] on malformed input or geometry type mismatch.
        """
        if not isinstance(geojson, dict):
            raise GeoJSONParseError("Input must be a JSON object")

        if geojson.get("type") != "FeatureCollection":
            raise GeoJSONParseError(
                f"Expected type='FeatureCollection', got '{geojson.get('type')}'"
            )

        features = geojson.get("features")
        if not isinstance(features, list):
            raise GeoJSONParseError("'features' must be an array")

        records: list[StreetRecord | BuildingRecord] = []
        for i, feature in enumerate(features):
            try:
                records.append(self._parse_feature(feature))
            except GeoJSONParseError as exc:
                raise GeoJSONParseError(f"Feature[{i}]: {exc}") from exc

        return records

    def _parse_feature(self, feature: Any) -> StreetRecord | BuildingRecord:
        if not isinstance(feature, dict):
            raise GeoJSONParseError("Feature must be a JSON object")

        if feature.get("type") != "Feature":
            raise GeoJSONParseError(
                f"Expected type='Feature', got '{feature.get('type')}'"
            )

        geometry = feature.get("geometry")
        if not isinstance(geometry, dict):
            raise GeoJSONParseError("'geometry' must be a JSON object")

        props = feature.get("properties") or {}
        geom_type = geometry.get("type")
        coords = geometry.get("coordinates")

        if geom_type == "LineString":
            return self._parse_street(props, coords)
        elif geom_type == "Point":
            return self._parse_building(props, coords)
        else:
            raise GeoJSONParseError(
                f"Unsupported geometry type '{geom_type}'. "
                "Expected 'LineString' (street) or 'Point' (building)."
            )

    def _parse_street(self, props: dict, coords: Any) -> StreetRecord:
        if not isinstance(coords, list) or len(coords) < 2:
            raise GeoJSONParseError(
                "LineString coordinates must be an array of at least 2 positions"
            )
        for pos in coords:
            _validate_position(pos)

        return StreetRecord(
            street_id=_require_str(props, "street_id"),
            street_name=_require_str(props, "street_name"),
            street_address=props.get("street_address", ""),
            street_type=_require_str(props, "street_type"),
            surface_type=_require_str(props, "surface_type"),
            street_condition=_require_str(props, "street_condition"),
            lga=_require_str(props, "lga"),
            coordinates=coords,
            zone=props.get("zone"),
            ward=props.get("ward"),
            notes=props.get("notes"),
            verification_status=props.get("verification_status", "pending"),
            enumerator_id=props.get("enumerator_id", ""),
            enumeration_date=props.get("enumeration_date", ""),
            boundary_flag=bool(props.get("boundary_flag", False)),
            gps_accuracy_flag=bool(props.get("gps_accuracy_flag", False)),
            qa_flags=list(props.get("qa_flags") or []),
        )

    def _parse_building(self, props: dict, coords: Any) -> BuildingRecord:
        _validate_position(coords)

        return BuildingRecord(
            building_id=_require_str(props, "building_id"),
            street_id=_require_str(props, "street_id"),
            street_address=props.get("street_address"),
            building_type=_require_str(props, "building_type"),
            number_of_floors=_require_int(props, "number_of_floors"),
            number_of_units=_require_int(props, "number_of_units"),
            building_condition=_require_str(props, "building_condition"),
            lga=_require_str(props, "lga"),
            coordinates=coords,
            zone=props.get("zone"),
            ward=props.get("ward"),
            postcode=props.get("postcode"),
            postcode_status=props.get("postcode_status", "resolved"),
            has_signage=bool(props.get("has_signage", False)),
            business_names=list(props.get("business_names") or []),
            notes=props.get("notes"),
            verification_status=props.get("verification_status", "pending"),
            enumerator_id=props.get("enumerator_id", ""),
            enumeration_date=props.get("enumeration_date", ""),
            boundary_flag=bool(props.get("boundary_flag", False)),
            gps_accuracy_flag=bool(props.get("gps_accuracy_flag", False)),
            duplicate_flag=bool(props.get("duplicate_flag", False)),
            qa_flags=list(props.get("qa_flags") or []),
        )


# ── Serialiser ────────────────────────────────────────────────────────────────

class GeoJSONSerialiser:
    """Serialise internal records to RFC 7946 GeoJSON.

    Coordinates are always in [lon, lat] order per RFC 7946 §3.1.1.

    Requirements: 15.3
    """

    def serialise_feature_collection(
        self, records: list[StreetRecord | BuildingRecord]
    ) -> dict[str, Any]:
        return {
            "type": "FeatureCollection",
            "features": [self._serialise_record(r) for r in records],
        }

    def _serialise_record(
        self, record: StreetRecord | BuildingRecord
    ) -> dict[str, Any]:
        if isinstance(record, StreetRecord):
            return self._serialise_street(record)
        return self._serialise_building(record)

    def _serialise_street(self, s: StreetRecord) -> dict[str, Any]:
        return {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": s.coordinates,  # already [lon, lat] pairs
            },
            "properties": {
                "street_id": s.street_id,
                "street_name": s.street_name,
                "street_address": s.street_address,
                "street_type": s.street_type,
                "surface_type": s.surface_type,
                "street_condition": s.street_condition,
                "lga": s.lga,
                "zone": s.zone,
                "ward": s.ward,
                "notes": s.notes,
                "verification_status": s.verification_status,
                "enumerator_id": s.enumerator_id,
                "enumeration_date": s.enumeration_date,
                "boundary_flag": s.boundary_flag,
                "gps_accuracy_flag": s.gps_accuracy_flag,
                "qa_flags": s.qa_flags,
            },
        }

    def _serialise_building(self, b: BuildingRecord) -> dict[str, Any]:
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": b.coordinates,  # [lon, lat]
            },
            "properties": {
                "building_id": b.building_id,
                "street_id": b.street_id,
                "street_address": b.street_address,
                "building_type": b.building_type,
                "number_of_floors": b.number_of_floors,
                "number_of_units": b.number_of_units,
                "building_condition": b.building_condition,
                "lga": b.lga,
                "zone": b.zone,
                "ward": b.ward,
                "postcode": b.postcode,
                "postcode_status": b.postcode_status,
                "has_signage": b.has_signage,
                "business_names": b.business_names,
                "notes": b.notes,
                "verification_status": b.verification_status,
                "enumerator_id": b.enumerator_id,
                "enumeration_date": b.enumeration_date,
                "boundary_flag": b.boundary_flag,
                "gps_accuracy_flag": b.gps_accuracy_flag,
                "duplicate_flag": b.duplicate_flag,
                "qa_flags": b.qa_flags,
            },
        }


# ── Validation helpers ────────────────────────────────────────────────────────

def _validate_position(pos: Any) -> None:
    """Assert [pos] is a valid [lon, lat] position array."""
    if not isinstance(pos, list) or len(pos) < 2:
        raise GeoJSONParseError(
            f"Position must be [lon, lat] array, got: {pos!r}"
        )
    if not all(isinstance(v, (int, float)) for v in pos[:2]):
        raise GeoJSONParseError(
            f"Position coordinates must be numbers, got: {pos!r}"
        )


def _require_str(props: dict, key: str) -> str:
    val = props.get(key)
    if not isinstance(val, str) or not val.strip():
        raise GeoJSONParseError(f"Missing or empty required property '{key}'")
    return val


def _require_int(props: dict, key: str) -> int:
    val = props.get(key)
    if not isinstance(val, (int, float)):
        raise GeoJSONParseError(f"Property '{key}' must be a number, got: {val!r}")
    return int(val)

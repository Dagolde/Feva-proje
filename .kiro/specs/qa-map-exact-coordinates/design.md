# QA Map Exact Coordinates Bugfix Design

## Overview

Street records captured on the mobile app store a full WKB-encoded LineString (the complete GPS track walked by the enumerator), but the sync serializer `_streetToJson` in `street_bloc.dart` extracts only the first coordinate pair and sends a single `latitude`/`longitude` scalar. The backend `sync_service.py` then calls `_make_linestring_geom(lat, lon)` which constructs a degenerate two-point LineString with both points identical. The QA map therefore renders a dot or zero-length line instead of the actual route.

The fix has two parts:
1. **Mobile (Dart)**: Extend `_streetToJson` to decode all points from the WKB LineString and include them as a `coordinates` array in the sync payload.
2. **Backend (Python)**: Update `sync_service.py` to detect the `coordinates` array in the street payload and build a proper multi-point LineString geometry instead of calling `_make_linestring_geom`.

Buildings are unaffected by the geometry change (they correctly use a single Point), but the schema change must not break building sync.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug — a street sync payload that contains only a single `latitude`/`longitude` scalar instead of a full `coordinates` array, causing the backend to store a degenerate LineString.
- **Property (P)**: The desired behavior when the bug condition holds — the backend SHALL store a PostGIS LineString with all N coordinate pairs from the enumerator's GPS track, and the QA map SHALL render a polyline.
- **Preservation**: Existing sync acceptance/rejection logic, building geometry handling, idempotency, QA flag checks, and GPS Information panel display that must remain unchanged by the fix.
- **`_streetToJson`**: The method in `feva-mobile/lib/streets/bloc/street_bloc.dart` that serializes a `Street` row into the sync payload JSON. Currently extracts only the first WKB point.
- **`_make_linestring_geom`**: The helper in `feva-backend/app/services/sync_service.py` that constructs a degenerate two-point LineString from a single lat/lon pair. Will be bypassed when a full `coordinates` array is present.
- **WKB LineString**: Well-Known Binary encoding of a LineString geometry. Layout: `byteOrder(1) + wkbType(4) + numPoints(4) + [X(8) + Y(8)] * numPoints`.
- **Degenerate LineString**: A LineString where all points are identical, rendering as a dot on a map.
- **`geometryWkb`**: The `Uint8List` column in the mobile SQLite `streets` table storing the full GPS track as WKB.

## Bug Details

### Bug Condition

The bug manifests when a street record is serialized for sync. `_streetToJson` reads only the first `(lon, lat)` pair from the WKB blob and emits a flat `latitude`/`longitude` scalar. The backend receives no multi-point geometry and reconstructs a degenerate LineString.

**Formal Specification:**
```
FUNCTION isBugCondition(payload)
  INPUT: payload of type Map<String, dynamic>  (street sync payload)
  OUTPUT: boolean

  RETURN payload["entity_type"] == "street"
         AND payload["data"] does NOT contain key "coordinates"
         AND payload["data"] contains keys "latitude" AND "longitude"
         AND the WKB stored in the streets table for this record
             has numPoints >= 2
END FUNCTION
```

### Examples

- **2-point street**: Enumerator walks a short block, WKB has 2 points `[(3.38001, 6.45001), (3.38050, 6.45050)]`. `_streetToJson` emits `latitude: 6.45001, longitude: 3.38001`. Backend stores `LineString((3.38001 6.45001, 3.38001 6.45001))`. QA map shows a dot at the start point.
- **10-point street**: Enumerator walks a curved road, WKB has 10 points. `_streetToJson` emits only the first point. Backend stores a degenerate 2-point LineString. QA map shows a dot; the 9 subsequent GPS fixes are lost.
- **1-point street (edge case)**: WKB has exactly 1 point (GPS captured at a single location). `isBugCondition` returns false because there is no additional geometry to lose. Backend behavior is unchanged.
- **Building record**: `isBugCondition` returns false (entity_type != "street"). Building sync is unaffected.

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Street and building records with valid mandatory fields SHALL continue to be accepted and assigned a server UUID.
- Building records SHALL continue to store a PostGIS Point geometry from the `latitude`/`longitude` scalars in the payload.
- Records missing mandatory fields or failing GPS precision checks SHALL continue to be rejected with the appropriate error codes.
- The GPS Information panel on the QA record detail page SHALL continue to display latitude, longitude, and GPS accuracy values (derived from the first coordinate of the route).
- Boundary flag and GPS accuracy flag checks SHALL continue to use the first coordinate of the street route (already extracted in `_onSaveStreet` before calling `_streetToJson`).
- Sync idempotency (same `device_id` + `street_id` retry) SHALL continue to work correctly for both streets and buildings.
- Building records viewed on the QA map SHALL continue to display a single pin marker.

**Scope:**
All inputs that do NOT involve a multi-point street WKB geometry should be completely unaffected by this fix. This includes:
- Building sync payloads (use `latitude`/`longitude` scalars, unchanged)
- Photo sync payloads (no geometry change)
- Street payloads that already have only 1 GPS point (degenerate case, no regression)
- All QA approval/rejection/audit-trail flows

## Hypothesized Root Cause

Based on code inspection, the root causes are confirmed (not merely hypothesized):

1. **`_streetToJson` only reads the first WKB point**: The method at the bottom of `street_bloc.dart` decodes `lon` and `lat` from byte offsets 9 and 17 of the WKB blob (the first point) and places them as flat scalars in the payload. There is no loop over `numPoints`.

2. **`_make_linestring_geom` creates a degenerate geometry**: In `sync_service.py`, the street branch calls `_make_linestring_geom(lat, lon)` which does `LineString([(lon, lat), (lon, lat)])` — two identical points — regardless of the original track.

3. **No `coordinates` field in the sync schema**: `RecordPayload.data` is a free-form `dict[str, Any]`, so adding a `coordinates` key requires no schema migration, only a convention change in the serializer and the service handler.

4. **`WkbPolygon` parser exists but only handles Polygon (type 3)**: The existing `wkb_polygon.dart` utility cannot be reused for LineString (type 2). A new inline decoder or a shared `WkbLineString` utility is needed in `street_bloc.dart`.

## Correctness Properties

Property 1: Bug Condition - Full GPS Track Preserved in Street Sync

_For any_ street record where the WKB LineString contains N ≥ 2 distinct coordinate pairs (isBugCondition returns true), the fixed `_streetToJson` function SHALL include a `coordinates` field containing all N `[lon, lat]` pairs, and the fixed `sync_service.py` SHALL store a PostGIS LineString with exactly those N coordinate pairs, such that `get_record_detail` returns a GeoJSON LineString with N coordinates and the QA map renders a polyline.

**Validates: Requirements 2.1, 2.2, 2.3**

Property 2: Preservation - Non-Street and Single-Point Street Behavior Unchanged

_For any_ sync payload where the bug condition does NOT hold (building records, photo records, or street records with a single GPS point), the fixed sync pipeline SHALL produce exactly the same stored geometry, acceptance/rejection status, QA flags, and API responses as the original pipeline, preserving all existing functionality for non-buggy inputs.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File 1**: `feva-mobile/lib/streets/bloc/street_bloc.dart`

**Function**: `_streetToJson`

**Specific Changes**:
1. **Decode all WKB points**: After reading `numPoints` from bytes 5–8 of the LineString WKB, loop over all N points (each 16 bytes: 8 lon + 8 lat) starting at offset 9.
2. **Emit `coordinates` array**: Add a `'coordinates': [[lon0, lat0], [lon1, lat1], ...]` field to the returned map.
3. **Keep `latitude`/`longitude` scalars**: Retain the existing first-point scalars for backward compatibility with GPS precision validation on the backend (which checks `data.get("latitude")`).

```dart
// Pseudocode for the fixed _streetToJson
Map<String, dynamic> _streetToJson(Street s) {
  final bytes = s.geometryWkb;
  double lat = 0, lon = 0;
  final coordinates = <List<double>>[];

  if (bytes.length >= 25) {
    final bd = ByteData.sublistView(Uint8List.fromList(bytes));
    final isLe = bytes[0] == 1;
    final numPoints = isLe
        ? bd.getUint32(5, Endian.little)
        : bd.getUint32(5, Endian.big);
    int offset = 9;
    for (int i = 0; i < numPoints && offset + 16 <= bytes.length; i++) {
      final x = isLe ? bd.getFloat64(offset, Endian.little) : bd.getFloat64(offset, Endian.big);
      final y = isLe ? bd.getFloat64(offset + 8, Endian.little) : bd.getFloat64(offset + 8, Endian.big);
      coordinates.add([x, y]);  // [lon, lat]
      offset += 16;
    }
    if (coordinates.isNotEmpty) {
      lon = coordinates[0][0];
      lat = coordinates[0][1];
    }
  }

  return {
    ...existingFields,
    'latitude': lat,
    'longitude': lon,
    'coordinates': coordinates,  // NEW: full GPS track
  };
}
```

**File 2**: `feva-backend/app/services/sync_service.py`

**Function**: `process_sync_upload` (street branch)

**Specific Changes**:
1. **Detect `coordinates` field**: After extracting `lat`/`lon` for the first-point checks, check if `data.get("coordinates")` is a non-empty list.
2. **Build multi-point geometry**: If `coordinates` is present and has ≥ 2 points, call `from_shape(LineString([(c[0], c[1]) for c in coordinates]), srid=4326)` instead of `_make_linestring_geom(lat, lon)`.
3. **Fall back gracefully**: If `coordinates` is absent or has < 2 points, continue using `_make_linestring_geom(lat, lon)` for backward compatibility with older app versions.

```python
# Pseudocode for the fixed geometry construction in the street branch
raw_coords = data.get("coordinates")
if raw_coords and len(raw_coords) >= 2:
    geom = from_shape(
        LineString([(c[0], c[1]) for c in raw_coords]),
        srid=4326
    )
else:
    geom = _make_linestring_geom(lat, lon)  # backward-compat fallback
```

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write unit tests that call `_streetToJson` with a known multi-point WKB blob and assert the output. Also write backend tests that call `process_sync_upload` with a street payload containing only `latitude`/`longitude` scalars and assert the stored geometry is degenerate. Run these tests on the UNFIXED code to observe failures.

**Test Cases**:
1. **Dart serializer multi-point test**: Construct a 3-point WKB LineString, call `_streetToJson`, assert `result['coordinates']` is absent or has length 1 (will fail on unfixed code — confirms bug).
2. **Backend degenerate geometry test**: POST a street sync payload with `latitude: 6.45001, longitude: 3.38001` (no `coordinates`), fetch the stored record via `get_record_detail`, assert `geometry.coordinates` has 2 identical points (confirms degenerate storage).
3. **QA map data contract test**: Assert that `geometry.coordinates[0] == geometry.coordinates[1]` for a synced street (confirms the dot-rendering root cause).
4. **Edge case — 1-point WKB**: Construct a 1-point WKB, call `_streetToJson`, assert behavior is unchanged (should pass on both unfixed and fixed code).

**Expected Counterexamples**:
- `_streetToJson` output does not contain a `coordinates` key with multiple entries.
- Stored PostGIS geometry for a multi-point street has `ST_NumPoints = 2` with identical coordinates.

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL street_wkb WHERE numPoints(street_wkb) >= 2 DO
  payload := _streetToJson_fixed(street_with_wkb)
  ASSERT "coordinates" IN payload
  ASSERT len(payload["coordinates"]) == numPoints(street_wkb)
  ASSERT payload["coordinates"][0] == [first_lon, first_lat]

  stored_geom := process_sync_upload_fixed(payload).geom
  ASSERT ST_NumPoints(stored_geom) == numPoints(street_wkb)
  ASSERT ST_GeometryType(stored_geom) == "ST_LineString"
  ASSERT NOT (stored_geom.coords[0] == stored_geom.coords[1])  // not degenerate
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL payload WHERE NOT isBugCondition(payload) DO
  result_original := process_sync_upload_original(payload)
  result_fixed    := process_sync_upload_fixed(payload)
  ASSERT result_original.status      == result_fixed.status
  ASSERT result_original.server_id   == result_fixed.server_id  // same idempotency
  ASSERT result_original.geom_type   == result_fixed.geom_type
  ASSERT result_original.errors      == result_fixed.errors
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain (building payloads, photo payloads, 1-point street payloads, invalid payloads)
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for building sync, photo sync, and validation rejection, then write property-based tests capturing that behavior.

**Test Cases**:
1. **Building sync preservation**: Verify building payloads with `latitude`/`longitude` scalars continue to produce a Point geometry and accepted status after the fix.
2. **Validation rejection preservation**: Verify that street payloads missing mandatory fields are still rejected with the same error codes after the fix.
3. **Idempotency preservation**: Verify that re-syncing the same street (same `device_id` + `street_id`) still returns the existing server UUID after the fix.
4. **GPS precision check preservation**: Verify that a street payload with `latitude: 6.45` (only 2 decimal places) is still rejected with `GPS_PRECISION_LAT` after the fix.
5. **Building map pin preservation**: Verify that `get_record_detail` for a building still returns `geometry.type == "Point"` after the fix.

### Unit Tests

- Test `_streetToJson` with a 1-point WKB: `coordinates` array has 1 entry, `latitude`/`longitude` scalars are correct.
- Test `_streetToJson` with a 5-point WKB: `coordinates` array has 5 entries, all coordinate pairs match the WKB data.
- Test `_streetToJson` with an empty WKB: returns `latitude: 0, longitude: 0, coordinates: []` without crashing.
- Test backend `_make_linestring_geom` fallback: when `coordinates` is absent, geometry is still created from scalars.
- Test backend multi-point path: when `coordinates` has 4 entries, stored geometry has `ST_NumPoints == 4`.

### Property-Based Tests

- **Property 1 (Fix)**: For any WKB LineString with N ≥ 2 randomly generated points, `_streetToJson` emits a `coordinates` array of length N, and the backend stores a LineString with exactly N points.
- **Property 2 (Preservation)**: For any randomly generated building payload with valid fields, the sync result (status, geometry type, server_id) is identical before and after the fix.
- **Property 2b (Preservation)**: For any randomly generated street payload that omits the `coordinates` field (simulating an old app version), the sync result is identical to the original behavior (degenerate LineString stored, accepted status returned).

### Integration Tests

- Sync a full street record end-to-end (mobile serializer → HTTP upload → backend → PostGIS → QA API): assert `GET /api/v1/qa/records/{id}?entity_type=street` returns a GeoJSON LineString with the correct number of points and non-identical coordinates.
- Sync a building record end-to-end after the fix: assert geometry type is still `Point` and coordinates match the submitted `latitude`/`longitude`.
- Verify the QA record detail page map renders a polyline (not a dot) for a synced multi-point street by asserting `geometry.coordinates.length > 1` and `geometry.coordinates[0] != geometry.coordinates[-1]`.

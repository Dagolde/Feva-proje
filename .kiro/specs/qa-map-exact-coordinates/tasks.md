# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Degenerate LineString Stored for Multi-Point Street
  - **CRITICAL**: This test MUST FAIL on unfixed code — failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior — it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: Scope the property to concrete failing cases — street sync payloads that contain only `latitude`/`longitude` scalars (no `coordinates` array) when the original WKB has N ≥ 2 distinct points
  - Create `feva-backend/tests/test_bugfix_qa_map_exact_coordinates.py`
  - Write a property-based test using `hypothesis` that generates street sync payloads with only `latitude`/`longitude` scalars (no `coordinates` key) and calls `process_sync_upload` directly
  - After the upload, fetch the stored street via `get_record_detail` and assert `geometry["coordinates"]` has at least 2 entries AND `geometry["coordinates"][0] != geometry["coordinates"][-1]` (non-degenerate)
  - Run test on UNFIXED code — the assertion will FAIL because the stored geometry has 2 identical points (degenerate LineString from `_make_linestring_geom`)
  - Document the counterexample: e.g. `process_sync_upload` with `latitude: 6.45001, longitude: 3.38001` stores `LineString((3.38001 6.45001, 3.38001 6.45001))` — both points identical
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Building Sync, Validation Rejection, Idempotency, and GPS Precision Unchanged
  - **IMPORTANT**: Follow observation-first methodology — run UNFIXED code with non-buggy inputs first, observe outputs, then encode as property tests
  - Add preservation tests to `feva-backend/tests/test_bugfix_qa_map_exact_coordinates.py`
  - **Observe on UNFIXED code**:
    - Building payload with valid `latitude`/`longitude` → accepted, geometry type is `Point`
    - Street payload missing `street_name` → rejected with `MISSING_FIELD:street_name`
    - Street payload with `latitude: 6.45` (2 decimal places) → rejected with `GPS_PRECISION_LAT:6.45`
    - Re-syncing same `street_id` + `device_id` → returns existing `server_id` (idempotency)
  - Write property-based tests using `hypothesis` that generate:
    - Random valid building payloads (varying lat/lon, lga, building_type, etc.) — assert status is `accepted` and geometry type is `Point`
    - Random street payloads with a missing mandatory field — assert status is `rejected` and errors contain `MISSING_FIELD:*`
    - Random street payloads with GPS coordinates having < 5 decimal places — assert status is `rejected` and errors contain `GPS_PRECISION_*`
  - Write a deterministic idempotency test: sync a street twice with the same `device_id` + `street_id`, assert both calls return the same `server_id`
  - Verify ALL preservation tests PASS on UNFIXED code before proceeding
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.5, 3.6_

- [x] 3. Fix: multi-point LineString stored for street sync

  - [x] 3.1 Update `_streetToJson` in `feva-mobile/lib/streets/bloc/street_bloc.dart`
    - Read `numPoints` from WKB bytes 5–8 (little-endian or big-endian per byte-order flag)
    - Loop over all N points starting at offset 9, each point is 16 bytes (8 lon + 8 lat)
    - Build a `coordinates` list: `[[lon0, lat0], [lon1, lat1], ...]`
    - Add `'coordinates': coordinates` to the returned map alongside the existing `latitude`/`longitude` scalars (keep scalars for backward-compat GPS precision validation on the backend)
    - Handle edge cases: empty WKB returns `coordinates: []`; 1-point WKB returns a single-entry list
    - _Bug_Condition: isBugCondition(payload) — street payload with only latitude/longitude scalars and WKB numPoints ≥ 2_
    - _Expected_Behavior: payload["coordinates"] contains all N [lon, lat] pairs from the WKB_
    - _Preservation: latitude/longitude scalars retained; 1-point and empty WKB behavior unchanged_
    - _Requirements: 2.1, 2.3_

  - [x] 3.2 Update `process_sync_upload` street branch in `feva-backend/app/services/sync_service.py`
    - After extracting `lat`/`lon` scalars, read `raw_coords = data.get("coordinates")`
    - If `raw_coords` is a non-empty list with ≥ 2 entries, build geometry with `from_shape(LineString([(c[0], c[1]) for c in raw_coords]), srid=4326)`
    - Otherwise fall back to `_make_linestring_geom(lat, lon)` for backward compatibility with older app versions that do not send a `coordinates` array
    - _Bug_Condition: isBugCondition(payload) — coordinates array absent, backend falls back to degenerate LineString_
    - _Expected_Behavior: stored PostGIS geometry has ST_NumPoints == len(coordinates) and is non-degenerate_
    - _Preservation: _make_linestring_geom fallback path unchanged; building branch untouched_
    - _Requirements: 2.1, 2.3, 3.1, 3.5, 3.6_

  - [x] 3.3 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Full GPS Track Preserved in Street Sync
    - **IMPORTANT**: Re-run the SAME test from task 1 — do NOT write a new test
    - The test from task 1 asserts `geometry["coordinates"]` has ≥ 2 non-identical entries
    - When this test passes, it confirms the backend now stores a proper multi-point LineString
    - Run `pytest feva-backend/tests/test_bugfix_qa_map_exact_coordinates.py -k "bug_condition"` (or equivalent)
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 3.4 Verify preservation tests still pass
    - **Property 2: Preservation** - Building Sync, Validation Rejection, Idempotency, GPS Precision Unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 — do NOT write new tests
    - Run `pytest feva-backend/tests/test_bugfix_qa_map_exact_coordinates.py -k "preservation"` (or equivalent)
    - **EXPECTED OUTCOME**: All preservation tests PASS (confirms no regressions)
    - Confirm building geometry is still `Point`, rejection errors are unchanged, idempotency still works

- [x] 4. Write end-to-end integration test for multi-point street sync
  - Add an integration test to `feva-backend/tests/test_bugfix_qa_map_exact_coordinates.py`
  - Construct a street sync payload with a `coordinates` array of 5 distinct `[lon, lat]` pairs (e.g. a short route across Lagos)
  - POST to `/api/v1/sync/upload` with a valid enumerator token
  - Resolve the `server_id` from the sync response
  - GET `/api/v1/qa/records/{server_id}?entity_type=street`
  - Assert `response.json()["geometry"]["type"] == "LineString"`
  - Assert `len(response.json()["geometry"]["coordinates"]) == 5`
  - Assert `response.json()["geometry"]["coordinates"][0] != response.json()["geometry"]["coordinates"][-1]` (non-degenerate)
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 5. Checkpoint — Ensure all tests pass
  - Run the full test file: `pytest feva-backend/tests/test_bugfix_qa_map_exact_coordinates.py -v`
  - Confirm Property 1 (bug condition) passes — bug is fixed
  - Confirm Property 2 (preservation) passes — no regressions
  - Confirm integration test passes — end-to-end route is correct
  - Ask the user if any questions arise before closing the spec

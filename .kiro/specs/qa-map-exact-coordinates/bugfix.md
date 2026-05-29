# Bugfix Requirements Document

## Introduction

The QA dashboard map does not display the exact GPS coordinates captured by the enumerator on the mobile app. Instead of showing the precise location (or full GPS track for streets), the map shows an incorrect or approximate position.

Root cause analysis reveals two related issues:

1. **Streets**: The mobile app stores a full WKB-encoded LineString (the complete GPS track walked by the enumerator) in the local database, but the sync payload serializer (`_streetToJson`) only extracts the first point from the WKB and sends a single `latitude`/`longitude` pair. The backend sync service then reconstructs a degenerate two-point LineString from that single coordinate (both points identical), discarding the full route. The QA map therefore shows a dot or a zero-length line instead of the actual street path.

2. **Buildings**: The mobile app correctly extracts the single GPS point from the WKB and sends `latitude`/`longitude`. The backend stores it correctly as a PostGIS Point. However, the `qa_service.py` geometry conversion uses `to_shape(record.geom)` which is correct, so buildings are less affected — but the same serialization pattern means any precision loss in the float extraction from WKB could cause minor coordinate drift.

The QA reviewer needs to see the exact pin (for buildings) or the exact route polyline (for streets) on the map, matching what the enumerator captured on the device.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN a street record is synced from the mobile app THEN the system stores only the first GPS coordinate of the enumerator's route as a degenerate two-point LineString (both points identical), discarding all other GPS track points

1.2 WHEN a QA reviewer opens the record detail page for a street THEN the system displays a zero-length line or a single dot on the map instead of the full GPS route walked by the enumerator

1.3 WHEN a street record is synced THEN the system receives only a single `latitude`/`longitude` scalar in the payload because `_streetToJson` extracts only the first point from the WKB LineString, ignoring all subsequent points

1.4 WHEN a building record is synced from the mobile app THEN the system stores the GPS point correctly, but the coordinate precision may be reduced because the WKB float extraction in `_buildingToJson` uses standard double precision without verifying the ≥5 decimal place requirement is preserved end-to-end

### Expected Behavior (Correct)

2.1 WHEN a street record is synced from the mobile app THEN the system SHALL store the complete GPS track as a multi-point LineString in PostGIS, preserving all coordinate pairs captured by the enumerator

2.2 WHEN a QA reviewer opens the record detail page for a street THEN the system SHALL display the full GPS route polyline on the map, with start and end markers, matching the path walked by the enumerator

2.3 WHEN a street record is synced THEN the system SHALL receive the full geometry as either a WKB hex string or a GeoJSON coordinates array in the payload so the backend can reconstruct the complete LineString

2.4 WHEN a building record is synced from the mobile app THEN the system SHALL store the GPS point with full precision (≥5 decimal places) matching the coordinate captured on the device

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a street record payload contains valid mandatory fields THEN the system SHALL CONTINUE TO accept the record and assign a server UUID

3.2 WHEN a building record payload contains valid mandatory fields and GPS coordinates THEN the system SHALL CONTINUE TO store the building with the correct Point geometry and all existing QA flags

3.3 WHEN a street or building record fails QA validation (missing fields, GPS precision errors) THEN the system SHALL CONTINUE TO reject the record and return the appropriate error codes

3.4 WHEN a QA reviewer views the GPS Information panel on the record detail page THEN the system SHALL CONTINUE TO display latitude, longitude, and GPS accuracy values

3.5 WHEN a street record is synced THEN the system SHALL CONTINUE TO perform boundary flag checks and GPS accuracy flag checks using the first coordinate of the route

3.6 WHEN the sync engine processes a batch upload THEN the system SHALL CONTINUE TO handle idempotency (same device_id + record_id retries) correctly for both streets and buildings

3.7 WHEN a building record is viewed on the QA map THEN the system SHALL CONTINUE TO display a single pin marker at the building's GPS location

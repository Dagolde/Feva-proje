# Implementation Plan: FEVA — Field Enumeration and Verification App

## Overview

Phased implementation across three delivery milestones. Phase 1 targets a working MVP by Week 4 covering offline capture, auth, GPS, photos, and basic sync. Phase 2 adds supervisory workflows, QA rules, and certified export. Phase 3 delivers physical verification via QR scanning. Backend, DevOps, and testing tasks run in parallel with mobile phases.

---

## Phase 1 — MVP (Target: Week 4)

### 1. DevOps: Repository and CI/CD Setup

- [x] 1.1 Initialise IGSL GitHub organisation repositories
  - Create `feva-mobile` (Flutter) and `feva-backend` (Python) repos under IGSL GitHub org
  - Add `.gitignore`, `LICENSE`, `CODEOWNERS`, branch protection rules (`main`, `develop`)
  - _Requirements: 20.1_

- [ ]* 1.2 Configure GitHub Actions CI pipeline for Flutter
  - Run `flutter analyze`, `flutter test --coverage` on every PR to `develop`
  - Upload coverage report as PR artifact
  - _Requirements: 20.1_

- [ ]* 1.3 Configure GitHub Actions CI pipeline for Python backend
  - Run `ruff`, `mypy`, `pytest --cov` on every PR to `develop`
  - Upload coverage report as PR artifact
  - _Requirements: 20.1_

- [x] 1.4 Configure deployment pipeline to IGSL infrastructure
  - Dockerfile for FastAPI service (multi-stage, non-root user)
  - `docker-compose.yml` for local dev (FastAPI + PostgreSQL/PostGIS + Redis)
  - GitHub Actions CD: build image, push to IGSL container registry, deploy on merge to `main`
  - _Requirements: 20.1, 20.2_

### 2. Backend: Project Scaffold and PostgreSQL/PostGIS Schema

- [x] 2.1 Scaffold FastAPI project structure
  - Create `feva-backend/` with `app/`, `tests/`, `alembic/`, `pyproject.toml`
  - Install dependencies: `fastapi`, `uvicorn[standard]`, `gunicorn`, `sqlalchemy[asyncio]`, `asyncpg`, `geoalchemy2`, `alembic`, `python-jose[cryptography]`, `pyotp`, `passlib[bcrypt]`, `hypothesis`, `pytest-asyncio`, `ruff`, `mypy`
  - Configure `app/core/config.py` with Pydantic `Settings` (env-based)
  - _Requirements: 20.1, 20.2_

- [x] 2.2 Implement PostgreSQL/PostGIS schema via Alembic migrations
  - Create initial migration: `roles`, `users`, `dropdown_config`, `shapefile_versions`, `streets`, `buildings`, `photos`, `audit_log`, `sync_sessions` tables as per design DDL
  - Add immutability triggers `trg_audit_log_no_update` / `trg_audit_log_no_delete` on `audit_log`
  - Add GIST spatial indexes on `streets.geom`, `buildings.geom`
  - _Requirements: 6.2, 16.3, 16.4, 16.5_

- [ ]* 2.3 Write unit test for audit log immutability trigger
  - Attempt UPDATE and DELETE on `audit_log` rows; assert `ProgrammingError` is raised
  - **Property 8: Audit Log Immutability**
  - **Validates: Requirements 16.4**
  - _Requirements: 16.4_

### 3. Backend: Authentication Service

- [x] 3.1 Implement JWT RS256 auth service
  - `POST /api/v1/auth/login` — validate credentials with `passlib`, issue RS256 access + refresh tokens via `python-jose`
  - `POST /api/v1/auth/refresh` — rotate access token
  - `POST /api/v1/auth/logout` — delete refresh token hash
  - Account lockout after 3 failed attempts (`users.locked_at`); write every attempt to `audit_log`
  - _Requirements: 1.2, 1.3, 1.4, 1.9, 16.1_

- [x] 3.2 Implement TOTP 2FA endpoints
  - `POST /api/v1/auth/totp/setup` — generate secret with `pyotp`, return QR code URI + 8 backup codes (bcrypt-hashed)
  - `POST /api/v1/auth/totp/verify` — validate TOTP code at login when `totp_enabled=TRUE`
  - _Requirements: 1.5_

- [x] 3.3 Implement FastAPI RBAC middleware
  - Dependency `require_role(*roles)` that decodes JWT, checks `role` claim, returns 403 if not permitted
  - Apply to all protected endpoints per RBAC permission matrix in design
  - _Requirements: 1.6, 1.7, 1.8_

- [ ]* 3.4 Write property test for RBAC enforcement
  - **Property 5: RBAC Enforcement**
  - Generate arbitrary (role, endpoint) pairs; assert 403 for unpermitted combinations, 2xx for permitted
  - **Validates: Requirements 1.6, 1.7, 1.8**

- [ ]* 3.5 Write property test for token issuance
  - **Property 6: Token Issuance on Valid Login**
  - Use Hypothesis `st.builds` to generate valid and invalid credential pairs; assert token returned iff credentials valid
  - **Validates: Requirements 1.3, 1.5**

- [ ]* 3.6 Write property test for expired token rejection
  - **Property 23: Expired Token Rejection**
  - Generate tokens with past `exp`; assert all protected endpoints return 401
  - **Validates: Requirements 16.6**

### 4. Mobile: Flutter Project Scaffold

- [x] 4.1 Scaffold Flutter project with Drift ORM and SQLCipher
  - `flutter create feva_mobile --org com.igsl.feva`
  - Add dependencies: `drift`, `drift_flutter`, `sqlcipher_flutter_libs`, `flutter_secure_storage`, `geolocator`, `camera`, `native_exif`, `maplibre_gl`, `workmanager`, `mobile_scanner`, `http`, `flutter_bloc`, `equatable`
  - Configure `pubspec.yaml`; set `minSdkVersion 26` in `android/app/build.gradle`
  - _Requirements: 19.1, 20.1_

- [x] 4.2 Implement SQLite/SQLCipher schema with Drift ORM
  - Define Drift table classes for: `Sessions`, `DropdownConfig`, `BoundaryZones`, `Streets`, `Buildings`, `Photos`, `SyncQueue`, `AuditLog` matching design DDL
  - Configure `AppDatabase` with SQLCipher; derive encryption key via PBKDF2 from user password + device salt; store key in `flutter_secure_storage`
  - Write Drift migration for schema version 1
  - _Requirements: 6.2, 16.2_

### 5. Mobile: Authentication Module

- [x] 5.1 Implement AuthBloc and LoginScreen
  - `AuthBloc` with states: `AuthInitial`, `AuthLoading`, `AuthAuthenticated`, `AuthError`, `AuthLocked`
  - `LoginScreen` with username/password fields; calls `POST /api/v1/auth/login` over TLS
  - On success: store `access_token` + `refresh_token` in `flutter_secure_storage`; write session row to `Sessions` table
  - On 3 failures: display lockout message; write to device `audit_log`
  - `TwoFactorScreen` shown when server returns 422 (TOTP required)
  - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.9_

- [x] 5.2 Implement session expiry and re-auth guard
  - `AuthGuard` widget checks `token_expires_at` before each navigation; redirects to `LoginScreen` if expired
  - Preserve unsaved form state across re-auth using `flutter_secure_storage` draft persistence
  - _Requirements: 16.6_

- [x] 5.3 Implement role-based navigation routing
  - `AppRouter` reads `role` from session; restricts routes per RBAC matrix
  - Enumerator: street capture, building capture, personal history only
  - Supervisor: adds spot-check, QA dashboard routes
  - Admin: all routes
  - _Requirements: 1.6, 1.7, 1.8_

### 6. Mobile: GPS Service

- [x] 6.1 Implement GPS service with accuracy monitoring
  - `GpsService` wrapping `geolocator`; exposes `Stream<Position>` with accuracy and satellite count
  - Enforce 5 decimal place precision on stored coordinates
  - Raise `LowAccuracyWarning` event when accuracy > 10 m; set `gps_accuracy_flag=1` on record
  - 30-second timeout: show retry dialog + manual coordinate entry with accuracy disclaimer flag
  - Display real-time accuracy estimate and satellite count in capture UI
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [ ]* 6.2 Write property test for GPS precision invariant
  - **Property 3: GPS Precision Invariant**
  - Use `dart:math` `Random` with the standard `test` package to generate arbitrary lat/lon values; assert stored values have ≥ 5 decimal places
  - **Validates: Requirements 2.3, 3.3, 4.3, 11.1**

### 7. Mobile: Photo Service

- [x] 7.1 Implement photo capture with EXIF injection
  - `PhotoService` wrapping `camera` package; after capture, inject GPS lat/lon + UTC timestamp into EXIF via `native_exif`
  - Store file in app-private directory; record relative path + coordinates in `photos` table
  - Support multiple photos per street and building record
  - _Requirements: 5.1, 5.2, 5.5_

- [x] 7.2 Implement broken photo reference detection
  - Before any sync attempt, scan all `photos` rows with `sync_status='queued'`; check file existence via `dart:io`
  - Set `broken_ref_flag=1` and write to `audit_log` for any missing file
  - Display warning in submission list for records with broken references
  - _Requirements: 5.3_

- [ ]* 7.3 Write unit test for EXIF metadata injection
  - **Property 11: Photo EXIF Metadata Injection**
  - Capture a test photo; read back EXIF; assert GPS lat/lon and timestamp match the GPS_Fix used
  - **Validates: Requirements 5.1**

- [ ]* 7.4 Write unit test for broken photo reference detection
  - **Property 12: Broken Photo Reference Detection**
  - Insert a `photos` row with a non-existent file path; run detection; assert `broken_ref_flag=1`
  - **Validates: Requirements 5.3**

### 8. Mobile: Boundary Service and Shapefile Offline Layers

- [x] 8.1 Implement boundary service with offline point-in-polygon
  - `BoundaryService` loading WKB polygons from `boundary_zones` SQLite table
  - `containmentCheck(Point, zone_id) → bool` using `dart_jts`
  - `reverseGeocode(Point) → {zone, lga, ward, postcode}` querying all zone types
  - Set `boundary_flag=1` and display warning when point falls outside assigned zone
  - Set `postcode_status='unresolved'` when no NIPOST polygon matches
  - _Requirements: 2.4, 3.4, 8.2, 8.3, 10.1, 10.2, 10.3_

- [x] 8.2 Implement Shapefile boundary layer ingestion on device
  - During device provisioning / sync, download `.feva_boundaries` ZIP from `GET /api/v1/sync/shapefiles/{layer}`
  - Parse GeoJSON FeatureCollection; convert polygons to WKB; upsert into `boundary_zones` table
  - Compare SHA-256 checksum against stored `shapefile_version`; skip download if unchanged
  - _Requirements: 8.1, 8.5_

- [x] 8.3 Implement MapLibre map component with offline tiles
  - `MapLibreMapWidget` loading offline MBTiles from device storage
  - Overlay GeoJSON boundary layers from `boundary_zones` SQLite table
  - Display captured street/building points on map
  - _Requirements: 8.4, 8.6_

- [ ]* 8.4 Write property test for reverse geocode completeness
  - **Property 4: Reverse Geocode Completeness**
  - Use `Glados` to generate points known to be inside test boundary polygons; assert non-null zone/lga/ward returned
  - **Validates: Requirements 2.4, 3.4, 10.1, 10.2**

- [ ]* 8.5 Write property test for boundary containment and postcode resolution
  - **Property 9: Boundary Containment and Postcode Resolution**
  - Generate points outside assigned zone; assert `boundary_flag=1`; generate points outside NIPOST polygons; assert `postcode_status='unresolved'`
  - **Validates: Requirements 8.2, 8.3, 10.3**

### 9. Mobile: Street Capture Module

- [x] 9.1 Implement street ID generation and street form
  - `StreetBloc` with `StreetListScreen`, `StreetFormScreen`, `StreetMapScreen`
  - Auto-generate `STR-[LGA]-[SEQ]` using last known sequence from SQLite (`MAX(street_id)` per LGA)
  - Capture mandatory fields: `street_name`, `street_type`, `surface_type`, `street_condition`, at least one geotagged photo
  - Populate `zone`, `lga`, `ward` via `BoundaryService.reverseGeocode` on save
  - Set `enumerator_id`, `enumeration_date`, `verification_status='pending'` automatically
  - Block save if any mandatory field is empty; display names of missing fields
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

- [ ]* 9.2 Write property test for record ID format invariant (streets)
  - **Property 1: Record ID Format Invariant**
  - Use `dart:math` `Random` with the standard `test` package to generate arbitrary LGA codes and sequence numbers; assert generated `STR-[LGA]-[SEQ]` matches regex `^STR-[A-Z0-9]+-\d{6}$`
  - **Validates: Requirements 2.1**

- [ ]* 9.3 Write property test for mandatory field validation (streets)
  - **Property 2: Mandatory Field Validation**
  - Generate street records with arbitrary missing mandatory fields; assert save is rejected and record not persisted
  - **Validates: Requirements 2.2, 2.5, 11.4**

### 10. Mobile: Building Capture Module

- [x] 10.1 Implement building ID generation and building form
  - `BuildingBloc` with `BuildingListScreen`, `BuildingFormScreen`, `BuildingMapScreen`
  - Auto-generate `BLD-[LGA]-[SEQ]` using last known sequence from SQLite
  - Capture mandatory fields: `building_type`, `number_of_floors`, `number_of_units`, `building_condition`, `frontage_photo`, valid `street_id`
  - Populate `zone`, `lga`, `ward`, `postcode` via `BoundaryService.reverseGeocode` on save
  - Capture `has_signage` boolean; show `business_names` multi-entry field when `has_signage=true`
  - Block save if mandatory field missing or `street_id` invalid; display specific error messages
  - Set `enumerator_id`, `enumeration_date`, `verification_status='pending'` automatically
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

- [ ]* 10.2 Write property test for record ID format invariant (buildings)
  - **Property 1: Record ID Format Invariant**
  - Generate arbitrary LGA codes and sequences; assert `BLD-[LGA]-[SEQ]` matches regex `^BLD-[A-Z0-9]+-\d{6}$`
  - **Validates: Requirements 3.1**

- [ ]* 10.3 Write property test for mandatory field validation (buildings)
  - **Property 2: Mandatory Field Validation**
  - Generate building records with arbitrary missing mandatory fields (including absent frontage photo and missing street_id); assert save rejected and record not persisted
  - **Validates: Requirements 3.2, 3.5, 3.6, 5.4, 11.4**

### 11. Mobile: Offline Store and Sync Engine

- [x] 11.1 Implement offline queuing and unsynced record counter
  - On every street/building save, insert a row into `sync_queue` with `status='pending'`
  - `OfflineStatusWidget` subscribes to `SELECT COUNT(*) FROM sync_queue WHERE status='pending'`; displays count in real time
  - _Requirements: 6.4, 6.6_

- [x] 11.2 Implement Sync Engine in background isolate
  - `SyncEngine` running in Dart isolate via `flutter_workmanager`
  - On connectivity detected (or manual trigger): read `sync_queue WHERE status='pending' LIMIT 50`; mark `in_flight`
  - Build multipart payload (records JSON + photo files); `POST /api/v1/sync/upload` with JWT, TLS 1.2+
  - Per-result handling: accepted → `sync_status='synced'`, `server_id` stored; rejected → `sync_status='failed'`, error logged
  - Write sync operation to device `audit_log`; emit `SyncStatusEvent` to UI stream
  - Retry failed records on next cycle; expose manual sync trigger
  - _Requirements: 7.1, 7.3, 7.4, 7.5, 7.6_

- [ ]* 11.3 Write property test for offline queuing invariant
  - **Property 13: Offline Queuing Invariant**
  - Save records while simulating no connectivity; assert `sync_status='queued'` and `sync_queue` entry with `status='pending'` exists for each
  - **Validates: Requirements 6.4, 7.1**

- [ ]* 11.4 Write property test for incremental sync payload
  - **Property 14: Incremental Sync Payload**
  - Create records at known timestamps; run sync; assert payload contains exactly records with `last_modified_at > last_sync_at`
  - **Validates: Requirements 7.5**

- [ ]* 11.5 Write property test for sync state transitions
  - **Property 15: Sync State Transitions**
  - Simulate server accepting and rejecting records; assert accepted records have `sync_status='synced'` + non-null `server_id`; rejected have `sync_status='failed'`
  - **Validates: Requirements 7.3, 7.4**

- [x] 11.6 Checkpoint — Phase 1 core mobile complete
  - Ensure all Phase 1 mobile tests pass; verify end-to-end: capture street → capture building → GPS fix → photo → offline store → manual sync trigger → records appear in backend DB
  - Ask the user if questions arise.

### 12. Backend: Sync Upload Endpoint and Server-Side Validation

- [x] 12.1 Implement `POST /api/v1/sync/upload` endpoint
  - Accept `multipart/form-data`: `records_json` array + `photos[]` binary files
  - Stream photo files to IGSL object storage concurrently via `asyncio.gather`
  - Write accepted records to PostGIS via GeoAlchemy2; return per-record `{local_id, status, server_id|errors}`
  - Create `sync_sessions` row; write to `audit_log`
  - _Requirements: 7.1, 7.2, 7.7, 16.3_

- [x] 12.2 Implement server-side QA validation service
  - Validate: mandatory fields present, GPS precision ≥ 5 decimal places, geometry type matches (LineString/Point), `street_id` reference exists
  - Return structured per-record error responses for violations; do not persist invalid records
  - Write QA flag name + timestamp to `qa_flags` JSONB on accepted records
  - _Requirements: 11.1, 11.4, 11.5, 11.6, 11.7_

- [ ]* 12.3 Write property test for server-side validation rejection
  - **Property 17: Server-Side Validation Rejection**
  - Use Hypothesis to generate records violating each QA rule; assert server returns structured error and record not in DB
  - **Validates: Requirements 11.7**

- [x] 12.4 Implement `GET /api/v1/sync/config` and Shapefile download endpoints
  - Return latest `dropdown_config` rows + `shapefile_versions` checksums
  - `GET /api/v1/sync/shapefiles/{layer}` — stream `.feva_boundaries` ZIP package
  - _Requirements: 8.5, 18.2_

### 13. Backend: Shapefile Ingestion Pipeline

- [x] 13.1 Implement Shapefile ingestion pipeline
  - `POST /api/v1/admin/shapefiles` — accept ZIP upload; validate with GDAL/OGR (geometry type, CRS, required fields)
  - Read features into GeoDataFrame via Fiona/GeoPandas; reproject to EPSG:4326
  - Validate geometries with Shapely `is_valid`; repair with `buffer(0)` where possible; skip and log invalid features
  - Write to PostGIS via GeoAlchemy2; create GIST index; compute SHA-256 checksum
  - Package simplified GeoJSON + MBTiles for device distribution; store in IGSL object storage
  - Update `shapefile_versions.is_active`
  - _Requirements: 8.1, 8.5_

- [x] 13.2 Checkpoint — Phase 1 backend and sync complete
  - Ensure all Phase 1 backend tests pass; verify: login → JWT → sync upload → PostGIS write → Shapefile ingestion → device download
  - Properties 1–3, 13, 15 must be passing (Phase 1 exit criteria)
  - Ask the user if questions arise.

---

## Phase 2 — Enhanced

### 14. Mobile: Dropdown Configuration

- [x] 14.1 Implement configurable dropdown service
  - `DropdownService` reads `dropdown_config` table; provides values for `street_type`, `surface_type`, `street_condition`, `building_type`, `building_condition`
  - On sync, download updated config from `GET /api/v1/sync/config`; upsert into `dropdown_config` table
  - Fall back to last downloaded config when offline; log download failures with timestamp
  - _Requirements: 18.1, 18.2, 18.3, 18.4_

### 15. Mobile: Duplicate Detection

- [x] 15.1 Implement client-side duplicate detection
  - On building save, query `buildings` table: `SELECT * FROM buildings WHERE distance(geometry_wkb, new_point) < 1m` using haversine in Dart
  - If duplicate found: set `duplicate_flag=1`, add `'DUPLICATE_PROXIMITY'` to `qa_flags`, display non-blocking warning
  - _Requirements: 11.2, 11.3_

- [ ]* 15.2 Write property test for duplicate building detection
  - **Property 16: Duplicate Building Detection**
  - Use `Glados` to generate pairs of GPS points within and beyond 1 m; assert `duplicate_flag=1` iff distance < 1 m and `qa_flags` contains `'DUPLICATE_PROXIMITY'`
  - **Validates: Requirements 11.2, 11.3**

### 16. Mobile: Supervisor Spot-Check Module

- [x] 16.1 Implement supervisor spot-check screens
  - `SpotCheckListScreen`: list of Building/Street records in Supervisor's assigned LGA, sorted by submission date descending
  - `SpotCheckDetailScreen`: display full record; approve or reject with mandatory rejection reason
  - On approve: `PATCH /api/v1/records/{type}/{id}` with `verification_status='approved'`; update local record
  - On reject: require non-empty `rejection_reason`; `PATCH` with `verification_status='rejected'`; notify originating Enumerator
  - Write every approval/rejection to device `audit_log`
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ]* 16.2 Write property test for verification status transitions
  - **Property 18: Verification Status Transitions**
  - Use Hypothesis to generate approval/rejection/verification/dispute actions; assert correct `verification_status` set; assert rejection without reason returns 422
  - **Validates: Requirements 12.2, 12.3, 12.4, 17.4, 17.5**

### 17. Backend: Records API and Supervisor Endpoints

- [x] 17.1 Implement Records API endpoints
  - `GET /api/v1/records/streets` and `/buildings` — paginated, filterable by `lga`, `ward`, `status`, `flags`
  - `GET /api/v1/records/streets/{id}` and `/buildings/{id}` — single record with full geometry as GeoJSON
  - `PATCH /api/v1/records/streets/{id}` and `/buildings/{id}` — update `verification_status`, `rejection_reason`; write to `audit_log`
  - _Requirements: 12.2, 12.3, 12.4, 12.5_

- [x] 17.2 Implement server-side duplicate detection
  - On sync upload, run `ST_DWithin(geom, new_point, 1m)` PostGIS query for each incoming building
  - Set `duplicate_flag=TRUE` and add `'DUPLICATE_PROXIMITY'` to `qa_flags` on both records
  - _Requirements: 11.2, 11.3_

### 18. Backend: QA Dashboard and Metrics API

- [x] 18.1 Implement QA metrics API endpoints
  - `GET /api/v1/qa/metrics` — return: median GPS accuracy, boundary containment %, mandatory field completion %, valid photo reference %, approved verification %
  - `GET /api/v1/qa/flags` — records with active `boundary_flag`, `duplicate_flag`, or `postcode_status='unresolved'`
  - `GET /api/v1/qa/duplicates` — all duplicate-flagged building pairs
  - `GET /api/v1/qa/submission-counts` — daily/weekly counts by enumerator/LGA/ward
  - _Requirements: 13.1, 13.2, 13.4_

- [x] 18.2 Implement QA Dashboard web UI
  - FastAPI + Jinja2 server-rendered dashboard at `/dashboard/`
  - Display all metrics from 13.1–13.4; highlight median GPS accuracy > 5 m in red
  - Auto-refresh every 5 minutes via JavaScript `setInterval` polling `/api/v1/qa/metrics`
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

### 19. Mobile: Live GIS Connectivity

- [x] 19.1 Implement live WMS/WFS fallback in map component
  - `ConnectivityService` monitors network state; switches `MapLibreMapWidget` tile source between offline MBTiles and WMS/WFS URL
  - WFS `GetFeature` requests for live boundary overlay when online; attach JWT in `Authorization` header
  - On WMS/WFS error: silently fall back to offline tiles; no capture interruption
  - _Requirements: 9.1, 9.2, 9.3_

### 20. Backend: GeoJSON Parser/Serialiser and Export Pipeline

- [x] 20.1 Implement GeoJSON parser and serialiser
  - `GeoJSONParser`: parse RFC 7946 FeatureCollection/Feature into internal `StreetRecord`/`BuildingRecord` models
  - Validate geometry type (LineString for streets, Point for buildings); return descriptive error on type mismatch or malformed JSON
  - `GeoJSONSerialiser`: serialise internal records to RFC 7946 GeoJSON with coordinates in [lon, lat] order
  - _Requirements: 15.1, 15.2, 15.3, 15.5_

- [ ]* 20.2 Write property test for GeoJSON export validity
  - **Property 20: GeoJSON Export Validity**
  - Use Hypothesis to generate approved street and building records; assert exported GeoJSON has correct geometry type and valid RFC 7946 structure
  - **Validates: Requirements 14.1, 14.2, 15.3**

- [ ]* 20.3 Write property test for export round-trip fidelity
  - **Property 21: Export Round-Trip Fidelity**
  - Generate arbitrary valid records; serialise to GeoJSON; parse back; assert all fields equal and coordinates equal to 5 decimal places
  - Same test for Shapefile: export → re-import → compare
  - **Validates: Requirements 14.6, 14.7, 15.1, 15.4**

- [ ]* 20.4 Write property test for GeoJSON parser error handling
  - **Property 22: GeoJSON Parser Error Handling**
  - Use Hypothesis to generate malformed GeoJSON and geometry type mismatches; assert descriptive error returned and no partial record produced
  - **Validates: Requirements 15.2, 15.5**

- [x] 20.5 Implement async export service
  - `POST /api/v1/export/geojson` and `/shapefile` — create async export job; return `job_id`
  - Background task: query approved records from PostGIS via GeoPandas; write via Fiona; verify round-trip; store in IGSL object storage
  - `GET /api/v1/export/jobs/{job_id}` — poll status; return download URL when complete
  - `GET /api/v1/export/monthly/{year}/{month}` — serve pre-generated monthly package
  - Certified export filter: only `verification_status='approved'` records included
  - Write export job to `audit_log`
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7_

- [ ]* 20.6 Write property test for certified export filter
  - **Property 19: Certified Export Filter**
  - Generate records with mixed `verification_status`; run export; assert every record in output has `verification_status='approved'`
  - **Validates: Requirements 14.5**

- [x] 20.7 Implement Celery beat monthly automated export
  - Configure Celery + Redis; schedule task on 1st of each month at 02:00 UTC
  - Generate GeoJSON + Shapefile for all approved records in previous month; store in IGSL object storage
  - _Requirements: 14.4_

### 21. Backend: Admin API and Audit Log

- [x] 21.1 Implement Admin API endpoints
  - `GET/POST/PATCH/DELETE /api/v1/admin/users` — user management (create, update role/assignment/lock, deactivate)
  - `GET/POST /api/v1/admin/dropdown-config` — manage dropdown values; increment `version` on update
  - `GET /api/v1/admin/audit-log` — paginated read-only audit log (Admin only)
  - All mutations write to `audit_log`
  - _Requirements: 1.4, 1.8, 18.1, 18.2, 16.3, 16.5_

- [ ]* 21.2 Write property test for audit log completeness
  - **Property 7: Audit Log Completeness**
  - Use Hypothesis to generate sequences of system operations; assert each produces a corresponding `audit_log` entry with correct `operation`, `user_id`, `entity_id`, and UTC timestamp
  - **Validates: Requirements 1.9, 12.5, 16.3**

- [x] 21.3 Checkpoint — Phase 2 complete
  - Ensure all 25 correctness properties are passing
  - Verify: export round-trip green; QA dashboard metrics correct; supervisor spot-check flow end-to-end
  - Ask the user if questions arise.

### 26. Backend: NIPOST Boundary Discrepancy Reporting

- [x] 26.1 Add Alembic migration for `boundary_discrepancies` table and extend Shapefile ingestion pipeline
  - Create Alembic migration adding `boundary_discrepancies` table as per design DDL (columns: `id`, `postcode_polygon_id`, `admin_polygon_id`, `admin_type`, `overlap_area_m2`, `shapefile_version_id`, `detected_at`); add GIST indexes
  - After PostGIS write in `shapefile_service.py`, run ST_Intersection / ST_Area detection between NIPOST postcode polygons and LGA/Ward polygons for the newly ingested version
  - Insert discrepancy rows for all overlapping polygon pairs; record zero-discrepancy result (no row inserted) for postcodes with no overlap, ensuring no false positives
  - _Requirements: 21.1, 21.2, 21.7_

- [x] 26.2 Implement `GET /api/v1/qa/boundary-discrepancies` endpoint and update QA Dashboard
  - Implement paginated endpoint in `qa.py`; support filter params `?lga=` and `?admin_type=lga|ward`; return `postcode_polygon_id`, `admin_polygon_id`, `admin_type`, `overlap_area_m2`, `detected_at`
  - Update QA Dashboard (`qa/index.html` + `qa_dashboard.py`) to display total discrepancy count and per-LGA breakdown; highlight LGAs with count > 0 in a visually distinct manner alongside the GPS accuracy alert
  - _Requirements: 21.3, 21.4_

- [x] 26.3 Implement `GET /api/v1/export/boundary-discrepancies` on-demand endpoint and include in certified export
  - Add endpoint in `export.py` returning all current discrepancy records; support `?format=csv|json`
  - Extend certified export job (async export service) to bundle `boundary_discrepancies.csv` alongside GeoJSON/Shapefile files
  - _Requirements: 21.5, 21.6_

- [ ]* 26.4 Write property test for boundary discrepancy detection completeness
  - **Property 26: Boundary Discrepancy Detection Completeness**
  - Use Hypothesis to generate pairs of overlapping NIPOST/admin polygons (guaranteed non-zero intersection) and non-overlapping pairs; assert overlapping pairs produce exactly one discrepancy row with correct `overlap_area_m2 > 0`; assert non-overlapping pairs produce no discrepancy row
  - **Validates: Requirements 21.1, 21.2, 21.7**

### 27. Backend: Monthly Export Package Format

- [x] 27.1 Extend Celery beat monthly export task to generate coverage report and DQ metrics snapshot
  - In `worker.py` monthly export task (task 20.7), after generating GeoJSON/Shapefile, query street/building counts grouped by LGA and enumerator for the calendar month; include zero-count rows for all known LGAs and enumerators with no records in that month
  - Compute the 5 QA metrics (median GPS accuracy, boundary containment %, mandatory field completion %, duplicate flag %, verification approval %) for the same month; write as `dq_metrics_snapshot.csv`
  - Bundle both files into the monthly ZIP alongside existing exports
  - _Requirements: 22.1, 22.2, 22.3, 22.6_

- [x] 27.2 Implement on-demand coverage report and DQ metrics endpoints
  - Add `GET /api/v1/export/monthly/{year}/{month}/coverage-report` and `GET /api/v1/export/monthly/{year}/{month}/dq-metrics` in `export.py`; support `?format=csv|json`
  - Apply the same LGA / date-range / `verification_status` filters used by the certified export when called from a certified export context (Requirement 22.5)
  - _Requirements: 22.4, 22.5_

- [ ]* 27.3 Write property test for coverage report zero-count completeness
  - **Property 27: Coverage Report Zero-Count Completeness**
  - Use Hypothesis to generate months with sparse data (some LGAs and enumerators have zero records); assert every known LGA and every known enumerator appears in the coverage report with a zero-count row rather than being omitted
  - **Validates: Requirements 22.6**

- [ ]* 27.4 Write property test for DQ metrics snapshot consistency
  - **Property 28: DQ Metrics Snapshot Consistency**
  - Use Hypothesis to generate a set of records for a given date range; assert the values returned by `GET /api/v1/export/monthly/{year}/{month}/dq-metrics` match the values returned by `GET /api/v1/qa/metrics` when called with the same date range parameters
  - **Validates: Requirements 22.2**

---

## Phase 3 — Verification

### 22. Mobile: QR Code Scanning and Verification Mode

- [x] 22.1 Implement QR scanner and verification mode
  - `QRScannerScreen` using `mobile_scanner`; decode QR → `building_id`
  - Fetch `Building_Record` from local SQLite first; fall back to `GET /api/v1/records/buildings/{id}` if not found locally
  - Display captured attributes for Supervisor confirmation or dispute
  - On confirm: `PATCH /api/v1/records/buildings/{id}` with `verification_status='verified'`, `verified_by`, `verified_at`
  - On dispute: require non-empty `dispute_reason`; `PATCH` with `verification_status='disputed'`; queue for Admin review
  - If QR code has no matching record: display "record not found" error; write scan attempt to `audit_log`
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.7_

- [ ]* 22.2 Write property test for QR code lookup
  - **Property 24: QR Code Lookup**
  - Generate valid and invalid QR code values; assert valid codes retrieve correct `Building_Record`; invalid codes return "record not found" and log scan attempt
  - **Validates: Requirements 17.2, 17.7**

### 23. Backend: QR Code Generation and Compliance Report

- [x] 23.1 Implement QR code generation endpoint
  - `GET /api/v1/records/buildings/{id}/qr` — generate QR code PNG encoding `building_id`; store `qr_code_value` on building record
  - Use `qrcode` Python library; return PNG as response
  - _Requirements: 17.1_

- [x] 23.2 Implement compliance report endpoint
  - `GET /api/v1/qa/compliance/{lga}` — count buildings by `verification_status` ('verified', 'disputed', 'pending') for the LGA; return counts and percentages
  - Percentages must sum to 100% of total building count for the LGA
  - _Requirements: 17.6_

- [ ]* 23.3 Write property test for compliance report calculation
  - **Property 25: Compliance Report Calculation**
  - Use Hypothesis to generate arbitrary sets of buildings with mixed statuses per LGA; assert counts correct and percentages sum to 100%
  - **Validates: Requirements 17.6**

- [x] 23.4 Checkpoint — Phase 3 complete
  - Properties 18, 24, 25 passing; QR scan integration test green; compliance report generated per LGA
  - Ask the user if questions arise.

---

## Integration Tests

### 24. End-to-End Integration Tests

- [x] 24.1 Write end-to-end sync integration test
  - Flutter app in test mode → FastAPI test server → PostgreSQL test DB
  - Scenario: login → capture street → capture building with photo → trigger sync → assert records in PostGIS with correct geometry and fields
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 24.2 Write Shapefile ingestion integration test
  - Upload test Shapefile ZIP → PostGIS write → device package generation → device download → point-in-polygon query
  - Assert boundary containment and reverse geocode return correct values for known test points
  - _Requirements: 8.1, 8.2, 8.5_

- [x] 24.3 Write export pipeline integration test
  - Create approved records in PostGIS → trigger GeoJSON export → parse output → compare all fields and geometry coordinates to 5 decimal places
  - Repeat for Shapefile export
  - _Requirements: 14.1, 14.2, 14.3, 14.6, 14.7_

- [x] 24.4 Write auth flow integration test
  - Login with valid credentials → receive JWT → call protected endpoint → assert 200
  - Login with invalid credentials 3 times → assert account locked (403)
  - Use expired token → assert 401
  - _Requirements: 1.2, 1.3, 1.4, 16.6_

---

## Field Pilot (UAT — 2 LGAs)

### 25. Field Pilot Preparation and Execution

- [x] 25.1 Prepare test data and device provisioning scripts
  - Write script to provision test devices: install APK, load Shapefile boundaries for 2 pilot LGAs, seed dropdown config, create Enumerator and Supervisor test accounts
  - _Requirements: 8.1, 18.1, 19.1_

- [x] 25.2 Write automated smoke test suite for field pilot build
  - Automated tests covering: login, GPS fix acquisition, street capture, building capture, photo attach, offline save, sync, boundary containment check, duplicate detection
  - Run against pilot build before deployment; all tests must pass
  - _Requirements: 19.1, 19.3, 19.4, 19.7_

- [x] 25.3 Implement field pilot feedback collection endpoint
  - `POST /api/v1/admin/pilot-feedback` — accept structured feedback JSON from Supervisor devices during UAT
  - Store in a `pilot_feedback` table (not part of certified dataset); Admin-readable only
  - _Requirements: 20.2_

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP; all property tests are optional sub-tasks
- Each task references specific requirements for traceability
- Checkpoints at tasks 11.6, 13.2, 21.3, and 23.4 gate phase transitions
- Phase 1 exit criteria: Properties 1–3, 13, 15 passing; end-to-end sync test green
- Phase 2 exit criteria: All 28 properties passing; export round-trip verified; QA dashboard live; boundary discrepancy detection green; monthly coverage and DQ metrics bundled
- Phase 3 exit criteria: Properties 18, 24, 25 passing; QR scan integration test green; compliance report per LGA
- Property tests use Hypothesis (Python backend) and glados (Dart mobile); minimum 100 iterations each
- Every property test must include a comment: `# Feature: feva-mobile-app, Property N: <Title>`
- No third-party analytics, telemetry, or advertising SDKs may be added (Requirement 20.4)
- All source code lives in IGSL GitHub organisation; all data on IGSL-provisioned infrastructure (Requirements 20.1–20.3)

---

## Feature: Street Address Field

### 28. Street Address Field — Data Layer

- [ ] 28.1 Add `street_address` column to Streets Drift table
  - In `feva-mobile/lib/database/tables/streets_table.dart`, add `TextColumn get streetAddress => text()();`
  - Increment the Drift schema version in `AppDatabase` and add a migration step: `ALTER TABLE streets ADD COLUMN street_address TEXT NOT NULL DEFAULT ''`
  - _Requirements: 23.1, 23.3_

- [ ] 28.2 Add `street_address` column to Buildings Drift table
  - In `feva-mobile/lib/database/tables/buildings_table.dart`, add `TextColumn get streetAddress => text().nullable()();`
  - Include in the same schema migration as 28.1
  - _Requirements: 24.3, 24.6_

### 29. Street Address Field — Street Capture Module

- [ ] 29.1 Add `street_address` to `StreetFormData` and `StreetBloc`
  - In `feva-mobile/lib/streets/bloc/street_bloc.dart`, add `final String streetAddress` field to `StreetFormData`
  - Add `'Street Address'` to `_validateMandatoryFields` when `streetAddress.trim().isEmpty`
  - Pass `streetAddress` into `StreetsCompanion.insert(...)` when saving
  - Include `'street_address': s.streetAddress` in `_streetToJson` for sync payload
  - _Requirements: 23.2, 23.3, 23.4_

- [ ] 29.2 Add `street_address` input field to `StreetFormScreen`
  - In `feva-mobile/lib/streets/screens/street_form_screen.dart`, add `final _streetAddressCtrl = TextEditingController()`
  - Render a mandatory `TextFormField` labelled `'Street Address *'` in the form, positioned after Street Name
  - Pre-populate from `widget.existingStreet?.streetAddress` in `initState`
  - Pass `streetAddress: _streetAddressCtrl.text.trim()` in the `SaveStreet` event dispatch
  - Dispose `_streetAddressCtrl` in `dispose()`
  - _Requirements: 23.1, 23.5_

### 30. Street Address Auto-Population — Building Capture Module

- [ ] 30.1 Add `streetAddress` to `BuildingFormData` and `BuildingBloc`
  - In `feva-mobile/lib/buildings/bloc/building_bloc.dart`, add `final String? streetAddress` field to `BuildingFormData`
  - When saving, look up the parent street: `final street = await (db.select(db.streets)..where((t) => t.streetId.equals(data.streetId))).getSingleOrNull()`
  - Pass `streetAddress: Value(street?.streetAddress)` into `BuildingsCompanion.insert(...)`
  - Include `'street_address': b.streetAddress` in `_buildingToJson` for sync payload
  - _Requirements: 24.3, 24.5, 24.6_

- [ ] 30.2 Add read-only `street_address` display to `BuildingFormScreen` with live lookup
  - In `feva-mobile/lib/buildings/screens/building_form_screen.dart`, add `String? _streetAddress` state variable
  - Add `_onStreetIdChanged(String streetId)` async method: query `db.streets` for the entered `streetId`; call `setState(() => _streetAddress = street?.streetAddress)` on result
  - Attach `onChanged: _onStreetIdChanged` to the Street ID `TextFormField`
  - Render a read-only `TextFormField` labelled `'Street Address'` below the Street ID field, with `controller` set to a controller whose text is `_streetAddress ?? ''` and `enabled: false`
  - Pre-populate `_streetAddress` in `initState` when `existingBuilding` is non-null
  - _Requirements: 24.1, 24.2, 24.4_

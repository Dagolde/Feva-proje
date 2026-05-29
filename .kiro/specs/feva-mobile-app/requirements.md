# Requirements Document

## Introduction

The Field Enumeration and Verification App (FEVA) is a purpose-built mobile data collection tool commissioned by Inspired Global Systems Ltd (IGSL) on behalf of a Nigerian State Government as part of a statewide Addressing Infrastructure Programme. FEVA enables systematic enumeration of all streets and buildings across all Local Government Areas (LGAs) in the State, supporting offline-first data capture, geospatial validation, supervisory QA/QC workflows, and certified data export. The system is delivered in three phases: Phase 1 (core MVP), Phase 2 (supervisory and validation workflows), and Phase 3 (physical verification mode).

---

## Glossary

- **FEVA**: Field Enumeration and Verification App — the mobile application described in this document.
- **App**: The FEVA mobile application running on Android (mandatory) or iOS (optional).
- **Backend**: The server-side API and database system (Node.js/Python/PHP + PostgreSQL/PostGIS) provisioned by IGSL.
- **Enumerator**: A field agent who captures street and building data using the App.
- **Supervisor**: A user role with authority to review, approve, or reject Enumerator submissions and conduct spot-checks.
- **Admin**: A user role with full system access including configuration, user management, and data export.
- **LGA**: Local Government Area — the primary administrative subdivision used for data organisation.
- **Ward**: A sub-unit of an LGA used for spatial assignment.
- **Zone**: An administrative boundary layer derived from Shapefile data.
- **Street_Record**: A captured record representing a single street, stored as a LineString GeoJSON feature.
- **Building_Record**: A captured record representing a single building, stored as a Point GeoJSON feature.
- **Building_ID**: Auto-generated unique identifier for a building in the format BLD-[LGA]-[SEQ].
- **Street_ID**: Auto-generated unique identifier for a street in the format STR-[LGA]-[SEQ].
- **Shapefile**: An ESRI Shapefile containing government-issued administrative boundary layers preloaded onto the device.
- **Offline_Store**: The local SQLite database on the device used to persist records when no network is available.
- **Sync_Engine**: The component responsible for uploading locally stored records to the Backend when connectivity is available.
- **GPS_Fix**: A location reading obtained from the device's Fused Location Provider with at least 5 decimal places of precision.
- **Boundary_Containment_Check**: A spatial validation confirming that a GPS_Fix falls within the assigned Shapefile Zone.
- **NIPOST**: Nigerian Postal Service — the authority defining postcode boundary polygons used for postcode validation.
- **QA_Dashboard**: A web or in-app view presenting data quality metrics and submission statistics for Supervisors and Admins.
- **Duplicate_Flag**: A system-generated alert raised when two Building_Records have GPS coordinates within 1 metre of each other.
- **Verification_Mode**: Phase 3 functionality enabling physical-to-digital validation via QR code scanning.
- **QR_Code**: A machine-readable code affixed to a building during Phase 1/2 enumeration, linking to its Building_Record.
- **GeoJSON**: The RFC 7946 standard for encoding geographic data structures.
- **WMS/WFS/REST**: Standard geospatial web service protocols used for live GIS platform connectivity.
- **TLS**: Transport Layer Security — the encryption protocol required for all network communication.
- **2FA**: Two-Factor Authentication — a recommended additional authentication step for user login.
- **Audit_Log**: An immutable, timestamped record of all create, update, delete, and sync operations performed by any user.

---

## Requirements

### Requirement 1: User Authentication and Role-Based Access Control

**User Story:** As an Admin, I want to manage user accounts with distinct roles, so that only authorised personnel can access and operate the system.

#### Acceptance Criteria

1. THE App SHALL support three user roles: Enumerator, Supervisor, and Admin.
2. WHEN a user attempts to log in, THE App SHALL authenticate the user against the Backend using a username and password over TLS 1.2 or higher.
3. WHEN authentication succeeds, THE App SHALL issue a session token valid for the duration of the field session.
4. IF a login attempt fails three consecutive times, THEN THE App SHALL lock the account and notify the Admin.
5. WHERE 2FA is enabled by the Admin, THE App SHALL require a second authentication factor before granting access.
6. WHEN a user's role is Enumerator, THE App SHALL restrict access to street capture, building capture, and personal submission history only.
7. WHEN a user's role is Supervisor, THE App SHALL grant access to Enumerator functions plus spot-check review, submission approval or rejection, and the QA_Dashboard.
8. WHEN a user's role is Admin, THE App SHALL grant access to all system functions including user management, configuration, and data export.
9. THE Audit_Log SHALL record every login, logout, and failed login attempt with a timestamp and user identifier.

---

### Requirement 2: Street Enumeration

**User Story:** As an Enumerator, I want to capture complete street data in the field, so that every street in my assigned area is accurately recorded.

#### Acceptance Criteria

1. WHEN an Enumerator initiates a new street record, THE App SHALL auto-generate a Street_ID in the format STR-[LGA]-[SEQ] where SEQ is a zero-padded sequential integer unique within the LGA.
2. THE App SHALL capture the following mandatory fields for each Street_Record: street_name, street_type, surface_type, street_condition, and at least one geotagged photo.
3. WHEN the Enumerator saves a Street_Record, THE App SHALL record the GPS_Fix as a LineString geometry with coordinates expressed to a minimum of 5 decimal places.
4. WHEN a Street_Record is saved, THE App SHALL automatically populate the zone, lga, and ward fields by performing a point-in-polygon lookup against the preloaded Shapefile boundary layers.
5. IF a mandatory field is empty when the Enumerator attempts to submit a Street_Record, THEN THE App SHALL prevent submission and display the names of all missing mandatory fields.
6. THE App SHALL allow the Enumerator to attach notes as free text to any Street_Record.
7. WHEN a Street_Record is saved to the Offline_Store, THE App SHALL record the enumerator_id and enumeration_date automatically.
8. THE App SHALL set the initial verification_status of every new Street_Record to "pending".

---

### Requirement 3: Building Enumeration

**User Story:** As an Enumerator, I want to capture complete building data linked to a street, so that every building in my assigned area is accurately recorded with a unique identifier.

#### Acceptance Criteria

1. WHEN an Enumerator initiates a new building record, THE App SHALL auto-generate a Building_ID in the format BLD-[LGA]-[SEQ] where SEQ is a zero-padded sequential integer unique within the LGA.
2. THE App SHALL capture the following mandatory fields for each Building_Record: building_type, number_of_floors, number_of_units, building_condition, frontage_photo, and a reference to a valid Street_ID.
3. WHEN the Enumerator captures the building frontage GPS, THE App SHALL record the GPS_Fix as a Point geometry at the building frontage with coordinates expressed to a minimum of 5 decimal places.
4. WHEN a Building_Record is saved, THE App SHALL automatically populate the zone, lga, ward, and postcode fields by performing a point-in-polygon lookup against the preloaded Shapefile and NIPOST boundary layers.
5. IF the Enumerator attempts to submit a Building_Record without selecting a valid Street_ID, THEN THE App SHALL prevent submission and display an error message indicating that a street link is required.
6. IF a mandatory field is empty when the Enumerator attempts to submit a Building_Record, THEN THE App SHALL prevent submission and display the names of all missing mandatory fields.
7. THE App SHALL allow the Enumerator to record has_signage as a boolean and capture one or more business_names when has_signage is true.
8. WHEN a Building_Record is saved to the Offline_Store, THE App SHALL record the enumerator_id and enumeration_date automatically.
9. THE App SHALL set the initial verification_status of every new Building_Record to "pending".

---

### Requirement 4: GPS Acquisition

**User Story:** As an Enumerator, I want the App to acquire an accurate GPS fix quickly, so that all captured locations meet the programme's precision requirements.

#### Acceptance Criteria

1. THE App SHALL use the device's Fused Location Provider to obtain GPS coordinates.
2. WHEN the Enumerator requests a GPS_Fix, THE App SHALL acquire a location reading within 30 seconds under normal field conditions.
3. THE App SHALL store all GPS coordinates with a minimum of 5 decimal places of precision.
4. WHEN a GPS_Fix has a reported accuracy greater than 10 metres, THE App SHALL display a warning to the Enumerator and flag the record for Supervisor review.
5. WHILE the App is acquiring a GPS_Fix, THE App SHALL display the current accuracy estimate and satellite count to the Enumerator in real time.
6. IF the GPS_Fix cannot be acquired within 30 seconds, THEN THE App SHALL notify the Enumerator and allow manual retry or manual coordinate entry with a mandatory accuracy disclaimer flag.

---

### Requirement 5: Geotagged Photo Capture

**User Story:** As an Enumerator, I want to attach geotagged photos to street and building records, so that visual evidence is linked to each captured location.

#### Acceptance Criteria

1. WHEN an Enumerator captures a photo within the App, THE App SHALL embed the current GPS_Fix coordinates and timestamp into the photo's EXIF metadata.
2. THE App SHALL store photo files locally in the Offline_Store and record the file path in the photo_paths or frontage_photo field of the associated record.
3. IF a photo file path recorded in a Street_Record or Building_Record does not resolve to an existing file on the device, THEN THE App SHALL flag the record as having a broken photo reference before sync.
4. WHEN a Building_Record is submitted, THE App SHALL require at least one frontage photo; if absent, THE App SHALL prevent submission.
5. THE App SHALL support capture of multiple photos per Street_Record and per Building_Record.

---

### Requirement 6: Offline-First Operation and Local Storage

**User Story:** As an Enumerator, I want the App to work fully without an internet connection, so that I can collect data in areas with no network coverage.

#### Acceptance Criteria

1. THE App SHALL operate in full offline mode for all street and building capture functions without requiring any network connectivity.
2. THE App SHALL use SQLite as the mandatory local database engine on the Enumerator device, accessed via an ORM, with geometry fields stored in PostGIS-compatible geometry types to ensure spatial query support offline.
3. THE Offline_Store SHALL persist a minimum of 5,000 Building_Records and their associated photos on a single device without data loss.
4. WHEN the device has no network connectivity, THE App SHALL store all new and updated Street_Records and Building_Records in the SQLite Offline_Store and queue them for sync.
5. THE SQLite Offline_Store SHALL store all Shapefile boundary layers, NIPOST postcode polygons, and dropdown configuration data required for full offline operation.
6. WHILE the device is offline, THE App SHALL display the current count of unsynced records to the Enumerator.
7. THE App SHALL maintain full functionality for a minimum of 8 hours of continuous operation on a single battery charge under normal field use conditions.

---

### Requirement 7: Data Synchronisation

**User Story:** As an Enumerator, I want the App to automatically sync my captured data to the server when connectivity is available, so that the central database stays up to date.

#### Acceptance Criteria

1. WHEN network connectivity is detected, THE Sync_Engine SHALL automatically initiate upload of all queued records from the Offline_Store to the Backend.
2. THE Sync_Engine SHALL complete the upload of 100 records with associated photos within 2 minutes on a 3G network connection.
3. WHEN a sync operation completes successfully, THE Sync_Engine SHALL mark the uploaded records as synced in the Offline_Store and update the unsynced record count displayed to the Enumerator.
4. IF a sync operation fails for any record, THEN THE Sync_Engine SHALL retain the record in the queue, log the failure with a timestamp and error code, and retry on the next sync cycle.
5. THE Sync_Engine SHALL support incremental sync, uploading only records created or modified since the last successful sync.
6. THE App SHALL allow the Enumerator to manually trigger a sync at any time when connectivity is available.
7. THE Backend SHALL support a minimum of 200 simultaneous Enumerator sync sessions without degradation of the 2-minute sync performance target.

---

### Requirement 8: Shapefile Ingestion and Offline Boundary Layers

**User Story:** As an Admin, I want to preload government boundary Shapefiles onto devices, so that Enumerators can perform spatial validation without network access.

#### Acceptance Criteria

1. THE App SHALL ingest ESRI Shapefile boundary layers during device provisioning and store them in the Offline_Store for offline use.
2. WHEN a GPS_Fix is captured, THE App SHALL perform a Boundary_Containment_Check by testing whether the coordinate falls within the Enumerator's assigned Shapefile Zone.
3. IF a GPS_Fix falls outside the Enumerator's assigned Shapefile Zone, THEN THE App SHALL display a boundary violation warning and flag the record for Supervisor review.
4. THE App SHALL render offline Shapefile boundary layers and tile maps on the in-app map view without requiring network connectivity.
5. WHEN an Admin uploads a new Shapefile version to the Backend, THE App SHALL download and replace the local boundary layers during the next sync cycle.
6. THE App SHALL support map rendering using MapLibre, OpenLayers, or an equivalent open-source library.

---

### Requirement 9: Live GIS Platform Connectivity

**User Story:** As a Supervisor, I want the App to connect to live GIS services when online, so that I can view up-to-date spatial data alongside captured records.

#### Acceptance Criteria

1. WHEN the device has network connectivity, THE App SHALL support connection to external GIS platforms via WMS, WFS, and REST protocols.
2. THE App SHALL render live WMS and WFS layers on the in-app map view alongside locally stored boundary layers.
3. IF a live GIS connection fails, THEN THE App SHALL fall back to the offline boundary layers without interrupting field capture operations.

---

### Requirement 10: NIPOST Postcode Boundary Validation

**User Story:** As a data quality manager, I want every captured GPS point to be validated against NIPOST postcode boundaries, so that all records carry a verified postcode.

#### Acceptance Criteria

1. WHEN a Building_Record or Street_Record GPS_Fix is captured, THE App SHALL perform a point-in-polygon check against the preloaded NIPOST postcode boundary polygons.
2. WHEN the GPS_Fix falls within a NIPOST postcode boundary, THE App SHALL automatically populate the postcode field of the record with the corresponding postcode value.
3. IF the GPS_Fix does not fall within any NIPOST postcode boundary polygon, THEN THE App SHALL flag the record with a "postcode unresolved" status and require Supervisor review before the record can be marked as verified.

---

### Requirement 11: QA/QC Automated Validation Rules

**User Story:** As a Supervisor, I want the system to automatically validate all captured records against defined quality rules, so that data quality issues are caught before records enter the certified dataset.

#### Acceptance Criteria

1. THE App SHALL enforce GPS precision validation: any GPS_Fix stored with fewer than 5 decimal places SHALL be rejected and the Enumerator SHALL be prompted to recapture.
2. WHEN a Building_Record is saved, THE App SHALL check whether any existing Building_Record in the Offline_Store or Backend has a GPS_Fix within 1 metre of the new record's GPS_Fix.
3. IF a Duplicate_Flag condition is detected, THEN THE App SHALL display a duplicate warning to the Enumerator and flag both records for Supervisor review without blocking submission.
4. THE App SHALL prevent submission of any record with missing mandatory fields as defined in Requirements 2 and 3.
5. THE App SHALL validate that every Building_Record references a Street_ID that exists in the Offline_Store or Backend before allowing submission.
6. WHEN a record is flagged by any automated validation rule, THE App SHALL record the specific rule name and flag timestamp in the record's metadata.
7. THE Backend SHALL enforce all validation rules server-side upon receipt of synced records, rejecting non-compliant records and returning structured error responses to the Sync_Engine.

---

### Requirement 12: Supervisor Spot-Check Module

**User Story:** As a Supervisor, I want to review and approve or reject Enumerator submissions in the field, so that data quality is maintained throughout the enumeration campaign.

#### Acceptance Criteria

1. WHEN a Supervisor opens the spot-check module, THE App SHALL display a list of Building_Records and Street_Records submitted by Enumerators in the Supervisor's assigned area, sorted by submission date descending.
2. THE App SHALL allow the Supervisor to approve or reject any individual record, with a mandatory rejection reason when rejecting.
3. WHEN a Supervisor rejects a record, THE App SHALL notify the originating Enumerator and set the record's verification_status to "rejected".
4. WHEN a Supervisor approves a record, THE App SHALL set the record's verification_status to "approved".
5. THE Audit_Log SHALL record every approval and rejection action with the Supervisor's user identifier, the record identifier, and a timestamp.

---

### Requirement 13: QA Dashboard

**User Story:** As a Supervisor or Admin, I want a dashboard showing data quality metrics and submission progress, so that I can monitor the enumeration campaign in real time.

#### Acceptance Criteria

1. THE QA_Dashboard SHALL display daily and weekly submission counts broken down by Enumerator, LGA, and Ward.
2. THE QA_Dashboard SHALL display the current values of the following quality metrics: median GPS accuracy, percentage of records with 100% boundary containment, percentage of mandatory field completion, percentage of records with valid photo references, and percentage of records with approved verification_status.
3. WHEN the median GPS accuracy across all records in a reporting period exceeds 5 metres, THE QA_Dashboard SHALL highlight the metric in a visually distinct manner to alert the Supervisor or Admin.
4. THE QA_Dashboard SHALL display a list of all records currently carrying a Duplicate_Flag, boundary violation flag, or "postcode unresolved" status.
5. THE QA_Dashboard SHALL refresh its data at intervals of no more than 5 minutes when the Backend is reachable.

---

### Requirement 14: Data Export

**User Story:** As an Admin, I want to export the certified dataset in standard geospatial formats, so that the State Government and IGSL can use the data in their GIS platforms.

#### Acceptance Criteria

1. THE Backend SHALL support export of Street_Records as GeoJSON LineString features compliant with RFC 7946, including all fields defined in Appendix A of the RFP.
2. THE Backend SHALL support export of Building_Records as GeoJSON Point features compliant with RFC 7946, including all fields defined in Appendix A of the RFP.
3. THE Backend SHALL support export of Street_Records and Building_Records as ESRI Shapefile format.
4. THE Backend SHALL generate monthly export packages automatically and make them available for Admin download.
5. WHEN an Admin requests a final certified dataset export, THE Backend SHALL include only records with verification_status of "approved".
6. THE Backend SHALL produce a GeoJSON export that, when parsed and re-exported, produces an output equivalent to the original export (round-trip property).
7. THE Backend SHALL produce a Shapefile export that, when imported into a standard GIS tool and re-exported as GeoJSON, preserves all attribute fields and geometry coordinates to 5 decimal places.

---

### Requirement 15: GeoJSON Parser and Serialiser

**User Story:** As a developer, I want a reliable GeoJSON parser and serialiser, so that all spatial data is correctly encoded and decoded throughout the system.

#### Acceptance Criteria

1. WHEN a valid GeoJSON feature is provided, THE GeoJSON_Parser SHALL parse it into the internal record representation without data loss.
2. WHEN an invalid or malformed GeoJSON document is provided, THE GeoJSON_Parser SHALL return a descriptive error identifying the location and nature of the malformation.
3. THE GeoJSON_Serialiser SHALL format internal Street_Records and Building_Records into valid RFC 7946 GeoJSON features.
4. FOR ALL valid internal records, parsing a GeoJSON export then serialising then parsing again SHALL produce an equivalent record (round-trip property).
5. THE GeoJSON_Parser SHALL reject any feature whose geometry type does not match the expected type (LineString for streets, Point for buildings) and return a descriptive type mismatch error.

---

### Requirement 16: Security and Audit Logging

**User Story:** As an Admin, I want all data transmissions and stored data to be encrypted and all actions to be logged, so that the system meets the programme's security and accountability requirements.

#### Acceptance Criteria

1. THE App SHALL encrypt all data transmitted between the App and the Backend using TLS 1.2 or higher.
2. THE App SHALL encrypt all data stored in the Offline_Store at rest using AES-256 or an equivalent standard.
3. THE Audit_Log SHALL record every create, update, delete, and sync operation with the user identifier, record identifier, operation type, and UTC timestamp.
4. THE Audit_Log SHALL be immutable: no user role, including Admin, SHALL be able to delete or modify existing Audit_Log entries.
5. THE Backend SHALL retain Audit_Log entries for a minimum of 24 months.
6. WHEN a session token expires, THE App SHALL require the user to re-authenticate before performing any further operations.

---

### Requirement 17: Phase 3 — Verification Mode

**User Story:** As a Supervisor, I want to scan QR codes on buildings to validate physical structures against digital records, so that the certified dataset accurately reflects the built environment.

#### Acceptance Criteria

1. WHEN the Verification_Mode is activated, THE App SHALL enable the device camera to scan QR codes affixed to buildings.
2. WHEN a QR code is scanned, THE App SHALL retrieve the corresponding Building_Record from the Backend or Offline_Store and display its captured attributes to the Supervisor.
3. THE App SHALL allow the Supervisor to confirm or dispute the physical attributes of the building against the displayed Building_Record.
4. WHEN a Supervisor confirms a building during verification, THE App SHALL update the Building_Record's verification_status to "verified" and record the Supervisor's user identifier and UTC timestamp.
5. WHEN a Supervisor disputes a building during verification, THE App SHALL set the Building_Record's verification_status to "disputed", record the dispute reason, and queue the record for Admin review.
6. THE App SHALL generate a compliance report per LGA showing the count and percentage of buildings with verification_status of "verified", "disputed", and "pending".
7. IF a scanned QR code does not match any Building_Record in the Offline_Store or Backend, THEN THE App SHALL display a "record not found" error and log the scan attempt in the Audit_Log.

---

### Requirement 18: Configurable Dropdown Values

**User Story:** As an Admin, I want to configure the values available in dropdown fields, so that the App reflects the programme's current classification taxonomy without requiring a code release.

#### Acceptance Criteria

1. THE App SHALL source the values for street_type, surface_type, street_condition, building_type, and building_condition fields from a configuration dataset managed by the Admin.
2. WHEN an Admin updates a dropdown configuration on the Backend, THE App SHALL download the updated configuration during the next sync cycle and apply it to all subsequent capture sessions.
3. WHILE the device is offline, THE App SHALL use the most recently downloaded dropdown configuration.
4. IF a dropdown configuration download fails, THEN THE App SHALL retain the previous configuration and log the failure with a timestamp.

---

### Requirement 19: Platform and Performance Requirements

**User Story:** As a programme manager, I want the App to meet defined platform and performance targets, so that it is deployable across the Enumerator fleet and reliable under field conditions.

#### Acceptance Criteria

1. THE App SHALL be deployable on Android devices running Android 8.0 (API level 26) or higher.
2. WHERE an iOS build is produced, THE App SHALL be deployable on iOS 14 or higher.
3. THE App SHALL acquire a GPS_Fix within 30 seconds under open-sky conditions.
4. THE App SHALL complete a sync of 100 records with associated photos within 2 minutes on a 3G network connection.
5. THE Backend SHALL support a minimum of 200 simultaneous Enumerator sync sessions.
6. THE App SHALL sustain continuous field operation for a minimum of 8 hours on a single device battery charge under normal enumeration workload.
7. THE App SHALL store a minimum of 5,000 Building_Records with associated photos in the Offline_Store without data loss or performance degradation.

---

### Requirement 20: Source Code and Data Ownership

**User Story:** As IGSL and the State Government, we want clear ownership of the App source code and all collected data, so that our contractual obligations are met.

#### Acceptance Criteria

1. THE App source code SHALL be developed and maintained within IGSL's GitHub organisation and infrastructure exclusively.
2. THE Backend SHALL store all collected data on IGSL-provisioned infrastructure.
3. THE Backend SHALL treat all Street_Records and Building_Records as the property of the State Government and SHALL not transmit them to any third-party system without explicit Admin authorisation.
4. THE App SHALL not embed any third-party analytics, telemetry, or advertising SDK that transmits user or data information to parties other than IGSL's Backend.

---

### Requirement 21: NIPOST Boundary Discrepancy Reporting

**User Story:** As a data quality manager, I want the system to detect and report geometric discrepancies between NIPOST postcode boundary polygons and State administrative boundary polygons (LGA/Ward), so that boundary conflicts are visible to Admins and included in certified export packages.

#### Acceptance Criteria

1. WHEN an Admin uploads a new Shapefile version to the Backend (as defined in Requirement 8), THE Shapefile_Ingestion_Pipeline SHALL detect geometric discrepancies between NIPOST postcode boundary polygons and State administrative boundary polygons (LGA and Ward layers) by computing polygon intersections using PostGIS spatial functions.
2. WHEN a geometric discrepancy is detected, THE Backend SHALL store a discrepancy record containing: the NIPOST postcode polygon identifier, the overlapping LGA or Ward polygon identifier, the area of overlap in square metres, and the UTC timestamp of detection.
3. THE QA_Dashboard (as defined in Requirement 13) SHALL display the total count of active boundary discrepancy records, broken down by LGA, and SHALL provide access to the full list of discrepancy details including postcode identifier, administrative polygon identifier, and overlap area.
4. WHEN the median GPS accuracy alert condition defined in Requirement 13.3 is evaluated, THE QA_Dashboard SHALL also highlight any LGA where the count of boundary discrepancy records exceeds zero in a visually distinct manner.
5. WHEN an Admin generates a certified export package (as defined in Requirement 14), THE Export_Service SHALL include a boundary discrepancy report as an additional file in the export package, listing all discrepancy records current at the time of export.
6. THE Backend SHALL expose a boundary discrepancy report via the export API, available on demand, returning all current discrepancy records in JSON or CSV format.
7. IF no geometric discrepancy exists between a NIPOST postcode polygon and any State administrative boundary polygon, THEN THE Shapefile_Ingestion_Pipeline SHALL record a zero-discrepancy result for that postcode polygon and SHALL not raise a false positive alert.

---

### Requirement 22: Monthly Export Package Format

**User Story:** As an Admin, I want the automated monthly export package to include a coverage report and a data quality metrics snapshot in addition to the geospatial data files, so that the State Government receives a complete picture of enumeration progress and data quality for each month.

#### Acceptance Criteria

1. WHEN THE Backend generates a monthly export package (as defined in Requirement 14.4), THE Export_Service SHALL include a coverage report file containing the count of Street_Records and Building_Records captured per LGA and per Enumerator for the calendar month covered by the package.
2. WHEN THE Backend generates a monthly export package, THE Export_Service SHALL include a data quality metrics snapshot file containing the following QA metrics (as defined in Requirement 13.2) computed for the calendar month covered by the package: median GPS accuracy, boundary containment percentage, mandatory field completion percentage, duplicate flag percentage, and verification approval percentage.
3. THE coverage report and data quality metrics snapshot SHALL be bundled into the monthly export package as additional files in CSV or JSON format alongside the GeoJSON and Shapefile exports.
4. THE Backend SHALL expose the coverage report and data quality metrics snapshot for any given month via the export API on demand, independently of the full monthly package, returning the files in CSV or JSON format.
5. WHEN an Admin requests a certified export package (as defined in Requirement 14.5), THE Export_Service SHALL include the coverage report and data quality metrics snapshot scoped to the same record filter (LGA, date range, and verification_status) applied to the geospatial export.
6. IF no Street_Records or Building_Records exist for a given LGA or Enumerator within the reporting month, THEN THE Export_Service SHALL include a zero-count row for that LGA or Enumerator in the coverage report rather than omitting the row.

---

### Requirement 23: Street Address Field — Street Enumeration Module

**User Story:** As an Enumerator, I want to enter a street address when creating a street record, so that every street has a human-readable address that can be referenced by buildings on that street.

#### Acceptance Criteria

1. THE App SHALL include a `street_address` text field in the Street_Record capture form.
2. WHEN an Enumerator attempts to save a Street_Record, THE App SHALL treat `street_address` as a mandatory field and prevent submission if it is empty, displaying "Street Address" in the list of missing mandatory fields.
3. THE App SHALL persist the `street_address` value in the `streets` table of the Offline_Store alongside all other Street_Record fields.
4. WHEN a Street_Record is synced to the Backend, THE Sync_Engine SHALL include the `street_address` field in the sync payload so that the Backend persists it in the server-side `streets` table.
5. THE App SHALL display the `street_address` field when an Enumerator views or edits an existing Street_Record.

---

### Requirement 24: Street Address Auto-Population — Building Enumeration Module

**User Story:** As an Enumerator, I want the building form to automatically show the street address from the linked street, so that I do not have to re-enter address information that is already recorded on the parent street.

#### Acceptance Criteria

1. WHEN an Enumerator enters or selects a valid `street_id` in the Building_Record capture form, THE App SHALL look up the corresponding Street_Record in the Offline_Store and populate the `street_address` field of the building form with the street's `street_address` value.
2. THE App SHALL display the auto-populated `street_address` as a read-only field in the Building_Record capture form; the Enumerator SHALL NOT be able to manually edit this value.
3. WHEN a Building_Record is saved, THE App SHALL copy the `street_address` value from the Parent_Street record into the `street_address` column of the `buildings` table in the Offline_Store.
4. IF the `street_id` entered by the Enumerator does not match any Street_Record in the Offline_Store, THEN THE App SHALL leave the `street_address` field blank and display no address until a valid `street_id` is provided.
5. WHEN a Building_Record is synced to the Backend, THE Sync_Engine SHALL include the `street_address` field in the sync payload so that the Backend persists it in the server-side `buildings` table.
6. THE App SHALL persist the `street_address` on the Building_Record independently of the Parent_Street, so that the building retains its address even if the parent street record is later modified or unavailable.

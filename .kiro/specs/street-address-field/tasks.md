# Implementation Plan: Street Address Field

## Overview

Add `street_address` as a mandatory field to the Street Enumeration Module and auto-populate it in the Building Enumeration Module when a building is linked to a parent street.

---

## Tasks

### 28. Street Address Field — Data Layer

- [x] 28.1 Add `street_address` column to Streets Drift table
  - In `feva-mobile/lib/database/tables/streets_table.dart`, add `TextColumn get streetAddress => text()();`
  - Increment the Drift schema version in `AppDatabase` and add a migration step: `ALTER TABLE streets ADD COLUMN street_address TEXT NOT NULL DEFAULT ''`
  - _Requirements: 23.1, 23.3_

- [x] 28.2 Add `street_address` column to Buildings Drift table
  - In `feva-mobile/lib/database/tables/buildings_table.dart`, add `TextColumn get streetAddress => text().nullable()();`
  - Include in the same schema migration as 28.1
  - _Requirements: 24.3, 24.6_

### 29. Street Address Field — Street Capture Module

- [x] 29.1 Add `street_address` to `StreetFormData` and `StreetBloc`
  - In `feva-mobile/lib/streets/bloc/street_bloc.dart`, add `final String streetAddress` field to `StreetFormData`
  - Add `'Street Address'` to `_validateMandatoryFields` when `streetAddress.trim().isEmpty`
  - Pass `streetAddress` into `StreetsCompanion.insert(...)` when saving
  - Include `'street_address': s.streetAddress` in `_streetToJson` for sync payload
  - _Requirements: 23.2, 23.3, 23.4_

- [x] 29.2 Add `street_address` input field to `StreetFormScreen`
  - In `feva-mobile/lib/streets/screens/street_form_screen.dart`, add `final _streetAddressCtrl = TextEditingController()`
  - Render a mandatory `TextFormField` labelled `'Street Address *'` in the form, positioned after Street Name
  - Pre-populate from `widget.existingStreet?.streetAddress` in `initState`
  - Pass `streetAddress: _streetAddressCtrl.text.trim()` in the `SaveStreet` event dispatch
  - Dispose `_streetAddressCtrl` in `dispose()`
  - _Requirements: 23.1, 23.5_

### 30. Street Address Auto-Population — Building Capture Module

- [x] 30.1 Add `streetAddress` to `BuildingFormData` and `BuildingBloc`
  - In `feva-mobile/lib/buildings/bloc/building_bloc.dart`, add `final String? streetAddress` field to `BuildingFormData`
  - When saving, look up the parent street: `final street = await (db.select(db.streets)..where((t) => t.streetId.equals(data.streetId))).getSingleOrNull()`
  - Pass `streetAddress: Value(street?.streetAddress)` into `BuildingsCompanion.insert(...)`
  - Include `'street_address': b.streetAddress` in `_buildingToJson` for sync payload
  - _Requirements: 24.3, 24.5, 24.6_

- [x] 30.2 Add read-only `street_address` display to `BuildingFormScreen` with live lookup
  - In `feva-mobile/lib/buildings/screens/building_form_screen.dart`, add `String? _streetAddress` state variable
  - Add `_onStreetIdChanged(String streetId)` async method: query `db.streets` for the entered `streetId`; call `setState(() => _streetAddress = street?.streetAddress)` on result
  - Attach `onChanged: _onStreetIdChanged` to the Street ID `TextFormField`
  - Render a read-only `TextFormField` labelled `'Street Address'` below the Street ID field, with `controller` set to a controller whose text is `_streetAddress ?? ''` and `enabled: false`
  - Pre-populate `_streetAddress` in `initState` when `existingBuilding` is non-null
  - _Requirements: 24.1, 24.2, 24.4_

---

## Notes

- Tasks 28.1 and 28.2 must be completed before any other tasks in this plan (schema migration dependency)
- The Drift schema version bump covers both `streets` and `buildings` table changes in a single migration
- The `street_address` column on `buildings` is nullable to remain backward-compatible with building records created before this feature was deployed
- No backend Alembic migration is required in this plan; the backend `streets` and `buildings` tables already accept arbitrary JSON fields via the sync payload, and a separate backend migration task should be tracked in the feva-backend project

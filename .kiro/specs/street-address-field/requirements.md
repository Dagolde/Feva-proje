# Requirements Document

## Introduction

This feature adds a `street_address` field to the Street Enumeration Module (C.1.1) and auto-populates it in the Building Enumeration Module (C.1.2). When an Enumerator creates a street record, they must enter a street address as a mandatory text field. When a building record is subsequently linked to that street via its Street_ID, the building form automatically inherits and displays the parent street's address as a read-only field, ensuring address consistency across linked records without requiring re-entry.

---

## Glossary

- **Street_Address**: A free-text field capturing the civic or postal address of a street, entered by the Enumerator during street record creation.
- **Parent_Street**: The Street_Record referenced by a Building_Record via the `street_id` foreign key.
- **Auto-Population**: The automatic transfer of the `street_address` value from a Parent_Street record into the corresponding field of a Building_Record at the time the building is saved.

---

## Requirements

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

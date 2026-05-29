# Requirements Document

## Introduction

This document specifies requirements for implementing separate role-based dashboards for the FEVA (Field Enumeration and Verification App) system. The feature introduces two distinct web dashboards: an Admin Dashboard for system administrators with full control capabilities, and a QA Officer Dashboard for quality assurance personnel focused on record review and approval workflows.

The current system has a single dashboard accessible to all roles. This feature separates concerns by providing role-appropriate interfaces with proper access controls, improving usability and security.

## Glossary

- **Admin_Dashboard**: Web interface at `/admin/` providing full system administration capabilities
- **QA_Dashboard**: Web interface at `/qa/` providing quality assurance and record review capabilities
- **Admin_User**: User with admin role having full system access
- **QA_Officer**: User with qa_officer role having access to record review features only
- **Record**: A building or street enumeration entry submitted by enumerators
- **Record_Status**: State of a record (pending, approved, rejected, flagged)
- **LGA**: Local Government Area - administrative boundary unit
- **Ward**: Administrative subdivision within an LGA
- **Shapefile**: Geospatial vector data file defining boundary polygons
- **Audit_Log**: System-generated log of user actions and data changes
- **Sync_Session**: A synchronization event where mobile devices upload/download data
- **JWT_Token**: JSON Web Token used for session authentication
- **Dropdown_Config**: System configuration for dropdown menu options in mobile app
- **Role**: User permission level (admin, enumerator, supervisor, qa_officer)

## Requirements

### Requirement 1: Admin Dashboard Access Control

**User Story:** As an admin user, I want to access a dedicated admin dashboard, so that I can manage the system without navigating through features irrelevant to my role.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL be accessible at the `/admin/` route
2. WHEN an unauthenticated user attempts to access `/admin/`, THE System SHALL redirect to the login page
3. WHEN an authenticated Admin_User accesses `/admin/`, THE System SHALL display the Admin_Dashboard
4. WHEN an authenticated QA_Officer attempts to access `/admin/`, THE System SHALL return a 403 Forbidden error
5. WHEN an authenticated user with enumerator or supervisor role attempts to access `/admin/`, THE System SHALL return a 403 Forbidden error

### Requirement 2: QA Dashboard Access Control

**User Story:** As a QA officer, I want to access a dedicated QA dashboard, so that I can focus on record review without being overwhelmed by administrative features.

#### Acceptance Criteria

1. THE QA_Dashboard SHALL be accessible at the `/qa/` route
2. WHEN an unauthenticated user attempts to access `/qa/`, THE System SHALL redirect to the login page
3. WHEN an authenticated QA_Officer accesses `/qa/`, THE System SHALL display the QA_Dashboard
4. WHEN an authenticated Admin_User accesses `/qa/`, THE System SHALL display the QA_Dashboard
5. WHEN an authenticated user with enumerator or supervisor role attempts to access `/qa/`, THE System SHALL return a 403 Forbidden error

### Requirement 3: User Authentication

**User Story:** As a system user, I want to log in with my credentials, so that I can access the dashboard appropriate for my role.

#### Acceptance Criteria

1. THE System SHALL provide a login endpoint accepting username and password
2. WHEN valid credentials are provided, THE System SHALL generate a JWT_Token with user role information
3. WHEN invalid credentials are provided, THE System SHALL return a 401 Unauthorized error
4. THE JWT_Token SHALL expire after 8 hours of inactivity
5. WHEN a JWT_Token expires, THE System SHALL require re-authentication
6. THE System SHALL redirect authenticated users to their appropriate dashboard based on role after login

### Requirement 4: User Management

**User Story:** As an admin user, I want to manage user accounts, so that I can control who has access to the system and what they can do.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL display a list of all users with their roles and status
2. THE Admin_Dashboard SHALL provide functionality to create new user accounts with username, password, and role assignment
3. THE Admin_Dashboard SHALL provide functionality to edit existing user information including role changes
4. THE Admin_Dashboard SHALL provide functionality to deactivate user accounts
5. THE Admin_Dashboard SHALL provide functionality to reset user passwords
6. WHEN a user account is created or modified, THE System SHALL log the action in the Audit_Log
7. THE Admin_Dashboard SHALL validate that usernames are unique before creating accounts

### Requirement 5: Role and Permissions Management

**User Story:** As an admin user, I want to manage roles and permissions, so that I can ensure users have appropriate access levels.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL display all available roles (admin, enumerator, supervisor, qa_officer)
2. THE Admin_Dashboard SHALL allow assignment of roles to users
3. THE Admin_Dashboard SHALL display permissions associated with each role
4. WHEN a user's role is changed, THE System SHALL immediately apply the new permissions
5. THE System SHALL prevent removal of the last Admin_User from the system

### Requirement 6: System Configuration Management

**User Story:** As an admin user, I want to manage system configurations, so that I can customize dropdown options and LGA assignments for enumerators.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL provide an interface to view and edit Dropdown_Config entries
2. THE Admin_Dashboard SHALL allow creation of new dropdown options for building types, street types, and other enumeration fields
3. THE Admin_Dashboard SHALL allow editing and deletion of existing dropdown options
4. THE Admin_Dashboard SHALL provide functionality to assign LGAs to enumerators and supervisors
5. WHEN Dropdown_Config is modified, THE System SHALL log the change in the Audit_Log
6. THE System SHALL validate that dropdown options are not empty before saving

### Requirement 7: Shapefile Management

**User Story:** As an admin user, I want to upload and manage boundary shapefiles, so that enumerators have accurate geographic boundaries for their work areas.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL provide functionality to upload shapefile archives (zip files containing .shp, .shx, .dbf, .prj files)
2. WHEN a shapefile is uploaded, THE System SHALL validate the file format and geometry type
3. WHEN a valid shapefile is uploaded, THE System SHALL create a new Shapefile_Version record with version number and upload timestamp
4. THE Admin_Dashboard SHALL display a list of all Shapefile_Version records with version numbers and upload dates
5. THE Admin_Dashboard SHALL allow marking a specific Shapefile_Version as active for mobile device downloads
6. IF a shapefile upload fails validation, THEN THE System SHALL return a descriptive error message
7. THE System SHALL store shapefile geometry data in WKB format in the database

### Requirement 8: Data Export and Reporting

**User Story:** As an admin user, I want to export enumeration data and audit logs, so that I can perform external analysis and maintain compliance records.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL provide functionality to export all building records to CSV format
2. THE Admin_Dashboard SHALL provide functionality to export all street records to CSV format
3. THE Admin_Dashboard SHALL provide functionality to export building and street records to GeoJSON format
4. THE Admin_Dashboard SHALL provide functionality to export Audit_Log entries to CSV format
5. THE Admin_Dashboard SHALL allow filtering exports by date range, LGA, ward, and Record_Status
6. WHEN an export is requested, THE System SHALL generate the file asynchronously and provide a download link
7. THE System SHALL include all record metadata in exports including GPS coordinates, photos, and timestamps

### Requirement 9: Application Monitoring

**User Story:** As an admin user, I want to monitor system health and sync activity, so that I can identify and resolve issues proactively.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL display a list of recent Sync_Session records with device ID, user, timestamp, and status
2. THE Admin_Dashboard SHALL display system health metrics including database connection status and disk space
3. THE Admin_Dashboard SHALL display counts of records by status (pending, approved, rejected)
4. THE Admin_Dashboard SHALL display counts of active users by role
5. THE Admin_Dashboard SHALL refresh monitoring data automatically every 30 seconds
6. THE Admin_Dashboard SHALL provide functionality to view detailed logs for failed Sync_Session records

### Requirement 10: QA Record Viewing and Filtering

**User Story:** As a QA officer, I want to view and filter submitted records, so that I can efficiently review enumeration data.

#### Acceptance Criteria

1. THE QA_Dashboard SHALL display a paginated list of all building and street records
2. THE QA_Dashboard SHALL provide filters for Record_Status (pending, approved, rejected, flagged)
3. THE QA_Dashboard SHALL provide filters for LGA and ward
4. THE QA_Dashboard SHALL provide filters for enumerator username
5. THE QA_Dashboard SHALL provide filters for date range (submission date)
6. THE QA_Dashboard SHALL display record summary information including ID, type, location, enumerator, submission date, and status
7. WHEN filters are applied, THE System SHALL return matching records within 2 seconds for datasets up to 100,000 records
8. THE QA_Dashboard SHALL support pagination with configurable page size (10, 25, 50, 100 records per page)

### Requirement 11: QA Record Detail Review

**User Story:** As a QA officer, I want to view detailed information for individual records, so that I can thoroughly assess data quality.

#### Acceptance Criteria

1. WHEN a QA_Officer selects a record from the list, THE QA_Dashboard SHALL display the complete record details
2. THE QA_Dashboard SHALL display all form field values submitted by the enumerator
3. THE QA_Dashboard SHALL display GPS coordinates with accuracy information
4. THE QA_Dashboard SHALL display all photos associated with the record as thumbnails with full-size preview capability
5. THE QA_Dashboard SHALL display the record geometry on an interactive map
6. THE QA_Dashboard SHALL display submission timestamp and enumerator information
7. THE QA_Dashboard SHALL display the current Record_Status and any previous review comments

### Requirement 12: QA Record Approval and Rejection

**User Story:** As a QA officer, I want to approve or reject records with comments, so that I can ensure data quality and provide feedback to enumerators.

#### Acceptance Criteria

1. THE QA_Dashboard SHALL provide an "Approve" button for records with pending or flagged status
2. THE QA_Dashboard SHALL provide a "Reject" button for records with pending or flagged status
3. WHEN the "Reject" button is clicked, THE System SHALL require the QA_Officer to enter a rejection comment
4. WHEN a record is approved, THE System SHALL update the Record_Status to approved and record the QA_Officer username and timestamp
5. WHEN a record is rejected, THE System SHALL update the Record_Status to rejected, store the rejection comment, and record the QA_Officer username and timestamp
6. THE System SHALL log all approval and rejection actions in the Audit_Log
7. THE QA_Dashboard SHALL prevent modification of records that have already been approved or rejected

### Requirement 13: QA Reports and Statistics

**User Story:** As a QA officer, I want to generate reports and view statistics, so that I can track review progress and identify quality trends.

#### Acceptance Criteria

1. THE QA_Dashboard SHALL display summary statistics including total records, pending records, approved records, and rejected records
2. THE QA_Dashboard SHALL display approval rate percentage by enumerator
3. THE QA_Dashboard SHALL display average review time per record
4. THE QA_Dashboard SHALL provide functionality to generate a QA summary report for a specified date range
5. THE QA_Dashboard SHALL display a chart showing daily submission and review volumes
6. THE QA_Dashboard SHALL allow filtering statistics by LGA and ward

### Requirement 14: QA Audit Trail Viewing

**User Story:** As a QA officer, I want to view the audit trail for records, so that I can understand the history of changes and reviews.

#### Acceptance Criteria

1. THE QA_Dashboard SHALL display Audit_Log entries related to a specific record when viewing record details
2. THE Audit_Log display SHALL include timestamp, user, action type, and changes made
3. THE QA_Dashboard SHALL display the complete review history including all previous approvals, rejections, and status changes
4. THE Audit_Log entries SHALL be displayed in reverse chronological order (newest first)

### Requirement 15: Responsive Web Interface

**User Story:** As a dashboard user, I want the interface to work on different screen sizes, so that I can use it on desktop computers and tablets.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL render correctly on desktop screens with minimum resolution 1280x720 pixels
2. THE Admin_Dashboard SHALL render correctly on tablet screens with minimum resolution 768x1024 pixels
3. THE QA_Dashboard SHALL render correctly on desktop screens with minimum resolution 1280x720 pixels
4. THE QA_Dashboard SHALL render correctly on tablet screens with minimum resolution 768x1024 pixels
5. THE System SHALL use responsive CSS layouts that adapt to screen width
6. THE System SHALL ensure all interactive elements are accessible via touch on tablet devices

### Requirement 16: Session Management

**User Story:** As a dashboard user, I want my session to remain active while I'm working, so that I don't lose progress due to unexpected logouts.

#### Acceptance Criteria

1. THE System SHALL maintain user sessions using JWT_Token stored in HTTP-only cookies
2. THE System SHALL refresh JWT_Token automatically when user performs actions within 7 hours of token creation
3. WHEN a JWT_Token expires, THE System SHALL redirect the user to the login page
4. THE System SHALL provide a logout function that invalidates the current JWT_Token
5. THE System SHALL prevent concurrent sessions from the same user account on different devices

### Requirement 17: Real-time Data Updates

**User Story:** As a dashboard user, I want to see updated data without manually refreshing the page, so that I have current information for decision-making.

#### Acceptance Criteria

1. WHERE real-time updates are enabled, THE QA_Dashboard SHALL poll for new records every 60 seconds
2. WHERE real-time updates are enabled, THE Admin_Dashboard SHALL poll for monitoring data every 30 seconds
3. WHEN new data is available, THE System SHALL update the display without requiring a full page reload
4. THE System SHALL provide a manual refresh button for immediate data updates
5. THE System SHALL display the last update timestamp on dashboards with real-time updates

### Requirement 18: API Endpoints for Admin Dashboard

**User Story:** As a system developer, I want well-defined API endpoints for admin operations, so that the frontend can interact with backend services reliably.

#### Acceptance Criteria

1. THE System SHALL provide RESTful API endpoints for user CRUD operations at `/api/v1/admin/users`
2. THE System SHALL provide RESTful API endpoints for role management at `/api/v1/admin/roles`
3. THE System SHALL provide RESTful API endpoints for dropdown configuration at `/api/v1/admin/dropdown-config`
4. THE System SHALL provide RESTful API endpoints for shapefile upload and management at `/api/v1/admin/shapefiles`
5. THE System SHALL provide RESTful API endpoints for data export at `/api/v1/admin/export`
6. THE System SHALL provide RESTful API endpoints for monitoring data at `/api/v1/admin/monitoring`
7. ALL admin API endpoints SHALL require authentication with Admin_User role
8. ALL admin API endpoints SHALL return appropriate HTTP status codes (200, 201, 400, 401, 403, 404, 500)

### Requirement 19: API Endpoints for QA Dashboard

**User Story:** As a system developer, I want well-defined API endpoints for QA operations, so that the frontend can interact with backend services reliably.

#### Acceptance Criteria

1. THE System SHALL provide RESTful API endpoints for record listing with filters at `/api/v1/qa/records`
2. THE System SHALL provide RESTful API endpoints for record detail retrieval at `/api/v1/qa/records/{id}`
3. THE System SHALL provide RESTful API endpoints for record approval at `/api/v1/qa/records/{id}/approve`
4. THE System SHALL provide RESTful API endpoints for record rejection at `/api/v1/qa/records/{id}/reject`
5. THE System SHALL provide RESTful API endpoints for QA statistics at `/api/v1/qa/statistics`
6. THE System SHALL provide RESTful API endpoints for audit trail retrieval at `/api/v1/qa/records/{id}/audit`
7. ALL QA API endpoints SHALL require authentication with QA_Officer or Admin_User role
8. ALL QA API endpoints SHALL return appropriate HTTP status codes (200, 201, 400, 401, 403, 404, 500)

### Requirement 20: Security and Input Validation

**User Story:** As a system administrator, I want all user inputs to be validated and sanitized, so that the system is protected from malicious attacks.

#### Acceptance Criteria

1. THE System SHALL validate all API request parameters against expected types and formats
2. THE System SHALL sanitize all text inputs to prevent SQL injection attacks
3. THE System SHALL sanitize all text inputs to prevent cross-site scripting (XSS) attacks
4. THE System SHALL enforce password complexity requirements (minimum 8 characters, at least one uppercase, one lowercase, one number)
5. THE System SHALL rate-limit login attempts to 5 attempts per username per 15 minutes
6. IF rate limit is exceeded, THEN THE System SHALL temporarily block login attempts for that username
7. THE System SHALL validate file uploads to ensure only allowed file types are accepted
8. THE System SHALL limit file upload sizes to 50MB maximum

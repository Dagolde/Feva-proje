# Implementation Plan: Admin and QA Dashboards

## Overview

This implementation plan breaks down the admin-qa-dashboards feature into discrete coding tasks. The feature implements two separate role-based web dashboards for the FEVA system: an Admin Dashboard at `/admin/` for system administration and a QA Dashboard at `/qa/` for record review workflows.

The implementation uses FastAPI for the backend with Jinja2 templates for server-side rendering, enhanced with vanilla JavaScript for dynamic interactions. Authentication uses JWT tokens with role-based access control. All tasks build incrementally, with checkpoints to ensure functionality is validated early.

## Tasks

- [ ] 1. Set up authentication and authorization infrastructure
  - [x] 1.1 Implement JWT token management with role claims
    - Extend existing JWT utilities to include role information in token payload
    - Implement token creation with 8-hour expiration
    - Implement token validation and decoding
    - _Requirements: 3.2, 3.4_

  - [ ]* 1.2 Write property test for JWT token expiration
    - **Property 6: JWT Tokens Expire After 8 Hours**
    - **Validates: Requirements 3.4**

  - [x] 1.3 Create role-based authorization middleware
    - Implement `require_role()` dependency for FastAPI routes
    - Support multiple allowed roles (e.g., admin, qa_officer)
    - Return 403 Forbidden for unauthorized roles
    - _Requirements: 1.4, 1.5, 2.5_

  - [ ]* 1.4 Write property tests for role-based authorization
    - **Property 2: Admin Routes Require Admin Role**
    - **Property 3: QA Routes Require QA or Admin Role**
    - **Validates: Requirements 1.4, 1.5, 2.5, 18.7, 19.7**

  - [x] 1.5 Implement authentication redirect for unauthenticated users
    - Add middleware to redirect unauthenticated requests to login page
    - Handle both HTML and API endpoints appropriately
    - _Requirements: 1.2, 2.2_

  - [ ]* 1.6 Write property test for unauthenticated access redirects
    - **Property 1: Unauthenticated Access Redirects to Login**
    - **Validates: Requirements 1.2, 2.2**

  - [x] 1.7 Implement session management with HTTP-only cookies
    - Store JWT tokens in HTTP-only cookies
    - Implement token refresh logic for active sessions
    - Implement logout functionality to invalidate tokens
    - _Requirements: 16.1, 16.2, 16.4_

  - [ ]* 1.8 Write property test for expired token rejection
    - **Property 7: Expired Tokens Are Rejected**
    - **Validates: Requirements 3.5, 16.3**

- [ ] 2. Implement login and session management
  - [x] 2.1 Create login endpoint at `/api/v1/auth/login`
    - Accept username and password in request body
    - Validate credentials against database
    - Generate JWT token with role information on success
    - Return 401 for invalid credentials
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ]* 2.2 Write property tests for login functionality
    - **Property 4: Valid Login Generates JWT with Role**
    - **Property 5: Invalid Credentials Return 401**
    - **Validates: Requirements 3.2, 3.3**

  - [x] 2.3 Implement password complexity validation
    - Validate minimum 8 characters, one uppercase, one lowercase, one number
    - Return descriptive error messages for validation failures
    - _Requirements: 20.4_

  - [ ]* 2.4 Write property test for password complexity
    - **Property 36: Password Complexity Requirements Enforced**
    - **Validates: Requirements 20.4**

  - [x] 2.5 Implement login rate limiting
    - Track failed login attempts per username
    - Block login after 5 failed attempts within 15 minutes
    - Return 429 Too Many Requests when rate limit exceeded
    - _Requirements: 20.5, 20.6_

  - [ ]* 2.6 Write property test for login rate limiting
    - **Property 37: Login Rate Limiting Enforced**
    - **Validates: Requirements 20.5, 20.6**

  - [x] 2.7 Implement post-login redirect based on role
    - Redirect admin users to `/admin/` after login
    - Redirect qa_officer users to `/qa/` after login
    - _Requirements: 3.6_

  - [ ]* 2.8 Write property test for post-login redirect
    - **Property 8: Post-Login Redirect Based on Role**
    - **Validates: Requirements 3.6**

- [ ] 3. Implement user management service and API endpoints
  - [x] 3.1 Create UserService with CRUD operations
    - Implement `create_user()` with username uniqueness validation
    - Implement `update_user()` for role and LGA assignment changes
    - Implement `reset_password()` with password hashing
    - Implement `list_users()` with pagination
    - Implement `deactivate_user()` for soft delete
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ]* 3.2 Write property test for username uniqueness
    - **Property 9: User Creation Requires Unique Username**
    - **Validates: Requirements 4.7**

  - [ ]* 3.3 Write property test for user management audit logging
    - **Property 10: User Management Operations Are Audited**
    - **Validates: Requirements 4.6**

  - [x] 3.2 Create user management API endpoints at `/api/v1/admin/users`
    - GET `/api/v1/admin/users` - List users with pagination
    - POST `/api/v1/admin/users` - Create new user
    - PATCH `/api/v1/admin/users/{user_id}` - Update user
    - DELETE `/api/v1/admin/users/{user_id}` - Deactivate user
    - POST `/api/v1/admin/users/{user_id}/reset-password` - Reset password
    - All endpoints require admin role
    - _Requirements: 18.1, 18.7_

  - [ ]* 3.5 Write property test for role changes taking effect
    - **Property 11: Role Changes Take Effect Immediately**
    - **Validates: Requirements 5.4**

- [ ] 4. Implement role management API endpoints
  - [x] 4.1 Create role management endpoints at `/api/v1/admin/roles`
    - GET `/api/v1/admin/roles` - List all roles with permissions
    - Return role definitions (admin, enumerator, supervisor, qa_officer)
    - All endpoints require admin role
    - _Requirements: 5.1, 5.2, 5.3, 18.2, 18.7_

  - [x] 4.2 Add validation to prevent removing last admin user
    - Check admin count before role changes or user deactivation
    - Return validation error if attempting to remove last admin
    - _Requirements: 5.5_

- [ ] 5. Implement dropdown configuration management
  - [x] 5.1 Create dropdown configuration API endpoints at `/api/v1/admin/dropdown-config`
    - GET `/api/v1/admin/dropdown-config` - List dropdown options with category filter
    - POST `/api/v1/admin/dropdown-config` - Create new dropdown option
    - PATCH `/api/v1/admin/dropdown-config/{id}` - Update dropdown option
    - DELETE `/api/v1/admin/dropdown-config/{id}` - Delete dropdown option
    - All endpoints require admin role
    - _Requirements: 6.1, 6.2, 6.3, 18.3, 18.7_

  - [x] 5.2 Implement dropdown value validation
    - Validate that value and label fields are not empty or whitespace-only
    - Return descriptive validation errors
    - _Requirements: 6.6_

  - [ ]* 5.3 Write property test for empty dropdown validation
    - **Property 13: Empty Dropdown Values Are Rejected**
    - **Validates: Requirements 6.6**

  - [ ]* 5.4 Write property test for dropdown configuration audit logging
    - **Property 12: Dropdown Configuration Changes Are Audited**
    - **Validates: Requirements 6.5**

- [ ] 6. Implement shapefile management endpoints
  - [x] 6.1 Create shapefile upload endpoint at `/api/v1/admin/shapefiles`
    - POST `/api/v1/admin/shapefiles` - Upload shapefile ZIP archive
    - Validate file is ZIP format with required components (.shp, .shx, .dbf, .prj)
    - Create ShapefileVersion record with version number and timestamp
    - Store geometry in WKB format
    - Return descriptive errors for invalid files
    - _Requirements: 7.1, 7.2, 7.3, 7.6, 7.7_

  - [ ]* 6.2 Write property test for shapefile format validation
    - **Property 14: Shapefile Upload Validates File Format**
    - **Validates: Requirements 7.2, 7.6**

  - [ ]* 6.3 Write property test for shapefile version creation
    - **Property 15: Valid Shapefile Upload Creates Version Record**
    - **Validates: Requirements 7.3**

  - [x] 6.4 Create shapefile management endpoints
    - GET `/api/v1/admin/shapefiles` - List all shapefile versions
    - PATCH `/api/v1/admin/shapefiles/{id}/activate` - Mark version as active
    - All endpoints require admin role
    - _Requirements: 7.4, 7.5, 18.4, 18.7_

  - [ ]* 6.5 Write property test for WKB geometry storage
    - **Property 16: Shapefile Geometry Stored in WKB Format**
    - **Validates: Requirements 7.7**

- [ ] 7. Implement export functionality
  - [x] 7.1 Create ExportTask model and database migration
    - Define ExportTask model with id, created_by, format, entity_type, filters, status, file_path, error_message, timestamps
    - Create Alembic migration to add export_tasks table
    - Add indexes for created_by, status, and created_at
    - _Requirements: 8.6_

  - [x] 7.2 Create ExportService for async export generation
    - Implement `create_export_task()` to create pending task and return task_id
    - Implement `get_export_status()` to check task status and download URL
    - Implement `generate_csv_export()` for CSV format
    - Implement `generate_geojson_export()` for GeoJSON format
    - _Requirements: 8.1, 8.2, 8.3, 8.6_

  - [ ]* 7.3 Write property test for export task creation
    - **Property 17: Export Requests Create Async Tasks**
    - **Validates: Requirements 8.6**

  - [x] 7.4 Implement export filtering and metadata inclusion
    - Support filters for date range, LGA, ward, and record status
    - Include all metadata: GPS coordinates, photos, timestamps, enumerator info, verification status
    - _Requirements: 8.5, 8.7_

  - [ ]* 7.5 Write property test for export metadata inclusion
    - **Property 18: Exports Include All Record Metadata**
    - **Validates: Requirements 8.7**

  - [x] 7.6 Create export API endpoints at `/api/v1/admin/export`
    - POST `/api/v1/admin/export` - Create export task
    - GET `/api/v1/admin/export/{task_id}` - Get export status and download URL
    - POST `/api/v1/admin/export/audit-log` - Export audit log to CSV
    - All endpoints require admin role
    - _Requirements: 8.4, 18.5, 18.7_

- [ ] 8. Implement monitoring and audit log endpoints
  - [x] 8.1 Create monitoring endpoints at `/api/v1/admin/monitoring`
    - GET `/api/v1/admin/monitoring/health` - System health metrics (database, disk space, uptime)
    - GET `/api/v1/admin/monitoring/sync-sessions` - Recent sync sessions with pagination and status filter
    - GET `/api/v1/admin/monitoring/statistics` - Record counts by status and user counts by role
    - All endpoints require admin role
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.6, 18.6, 18.7_

  - [x] 8.2 Create audit log query endpoint at `/api/v1/admin/audit-log`
    - GET `/api/v1/admin/audit-log` - Query audit logs with pagination
    - Support filters for user_id, operation, date range
    - Return audit entries with timestamp, user, operation, entity details
    - Require admin role
    - _Requirements: 18.7_

- [x] 9. Checkpoint - Ensure all admin backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Implement QA record listing and filtering
  - [x] 10.1 Create QAService for record operations
    - Implement `list_records()` with filtering and pagination
    - Support filters for status, LGA, ward, enumerator, date range, entity_type
    - Query both Building and Street tables
    - Return RecordSummary objects with id, entity_type, record_id, location, enumerator, timestamp, status
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

  - [ ]* 10.2 Write property test for record filtering
    - **Property 19: Record Filters Return Matching Records**
    - **Validates: Requirements 10.2, 10.3, 10.4, 10.5**

  - [ ]* 10.3 Write property test for pagination
    - **Property 20: Record Pagination Works for All Page Sizes**
    - **Validates: Requirements 10.8**

  - [x] 10.4 Create record listing endpoint at `/api/v1/qa/records`
    - GET `/api/v1/qa/records` - List records with filters and pagination
    - Support query parameters for all filters
    - Return within 2 seconds for datasets up to 100,000 records
    - Require qa_officer or admin role
    - _Requirements: 10.7, 19.1, 19.7_

- [ ] 11. Implement QA record detail and review operations
  - [x] 11.1 Implement record detail retrieval in QAService
    - Implement `get_record_detail()` to fetch complete record information
    - Include all form fields, GPS coordinates with accuracy, photos, geometry
    - Include submission timestamp, enumerator info, review status and comments
    - Support both building and street entity types
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_

  - [ ]* 11.2 Write property test for record detail completeness
    - **Property 21: Record Details Include All Required Fields**
    - **Validates: Requirements 11.1-11.7**

  - [x] 11.3 Create record detail endpoint
    - GET `/api/v1/qa/records/{id}` - Get detailed record information
    - Require entity_type query parameter
    - Require qa_officer or admin role
    - _Requirements: 19.2, 19.7_

  - [x] 11.4 Implement record approval operation
    - Implement `approve_record()` in QAService
    - Update verification_status to "approved"
    - Set reviewed_by and reviewed_at fields
    - Prevent re-review of already-reviewed records
    - Create audit log entry
    - _Requirements: 12.1, 12.4, 12.6, 12.7_

  - [ ]* 11.5 Write property test for record approval
    - **Property 23: Record Approval Updates Status and Metadata**
    - **Validates: Requirements 12.4**

  - [x] 11.6 Implement record rejection operation
    - Implement `reject_record()` in QAService
    - Require non-empty rejection reason
    - Update verification_status to "rejected"
    - Set reviewed_by, reviewed_at, and rejection_reason fields
    - Prevent re-review of already-reviewed records
    - Create audit log entry
    - _Requirements: 12.2, 12.3, 12.5, 12.6, 12.7_

  - [ ]* 11.7 Write property test for rejection reason requirement
    - **Property 22: Record Rejection Requires Comment**
    - **Validates: Requirements 12.3**

  - [ ]* 11.8 Write property test for record rejection
    - **Property 24: Record Rejection Updates Status and Stores Reason**
    - **Validates: Requirements 12.5**

  - [ ]* 11.9 Write property test for preventing re-review
    - **Property 26: Already-Reviewed Records Cannot Be Re-Reviewed**
    - **Validates: Requirements 12.7**

  - [x] 11.10 Create approval and rejection endpoints
    - POST `/api/v1/qa/records/{id}/approve` - Approve record
    - POST `/api/v1/qa/records/{id}/reject` - Reject record with reason
    - Both require entity_type query parameter
    - Both require qa_officer or admin role
    - _Requirements: 19.3, 19.4, 19.7_

  - [ ]* 11.11 Write property test for review action audit logging
    - **Property 25: Review Actions Are Audited**
    - **Validates: Requirements 12.6**

- [ ] 12. Implement QA statistics and audit trail
  - [x] 12.1 Implement QA statistics in QAService
    - Implement `get_statistics()` with filtering by LGA, ward, date range
    - Calculate total, pending, approved, rejected record counts
    - Calculate approval rate by enumerator
    - Calculate average review time
    - Generate daily submission and review volume data
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6_

  - [x] 12.2 Create statistics endpoint
    - GET `/api/v1/qa/statistics` - Get QA statistics with filters
    - Require qa_officer or admin role
    - _Requirements: 19.5, 19.7_

  - [x] 12.3 Implement audit trail retrieval
    - Implement `get_audit_trail()` in QAService
    - Query audit logs for specific record
    - Include timestamp, user, action, and detail fields
    - Sort chronologically descending (newest first)
    - _Requirements: 14.1, 14.2, 14.3, 14.4_

  - [ ]* 12.4 Write property test for audit trail completeness
    - **Property 27: Audit Trail Includes All Record Operations**
    - **Validates: Requirements 14.1, 14.3**

  - [ ]* 12.5 Write property test for audit entry fields
    - **Property 28: Audit Entries Include Required Fields**
    - **Validates: Requirements 14.2**

  - [ ]* 12.6 Write property test for audit trail sorting
    - **Property 29: Audit Trail Sorted Chronologically Descending**
    - **Validates: Requirements 14.4**

  - [x] 12.7 Create audit trail endpoint
    - GET `/api/v1/qa/records/{id}/audit` - Get audit trail for record
    - Require entity_type query parameter
    - Require qa_officer or admin role
    - _Requirements: 19.6, 19.7_

- [x] 13. Checkpoint - Ensure all QA backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Implement security and input validation
  - [x] 14.1 Implement input sanitization utilities
    - Create `sanitize_html_input()` to prevent XSS attacks
    - Create `sanitize_sql_input()` for additional SQL injection protection
    - Apply sanitization to all text inputs in API endpoints
    - _Requirements: 20.2, 20.3_

  - [ ]* 14.2 Write property test for SQL injection prevention
    - **Property 34: SQL Injection Patterns Are Rejected**
    - **Validates: Requirements 20.2**

  - [ ]* 14.3 Write property test for XSS prevention
    - **Property 35: XSS Patterns Are Sanitized**
    - **Validates: Requirements 20.3**

  - [x] 14.4 Implement file upload validation
    - Create `validate_file_upload()` to check extension, size, and MIME type
    - Enforce 50MB maximum file size
    - Allow only ZIP files for shapefile uploads
    - _Requirements: 20.7, 20.8_

  - [ ]* 14.5 Write property test for file type validation
    - **Property 38: File Upload Type Validation**
    - **Validates: Requirements 20.7**

  - [ ]* 14.6 Write property test for file size limit
    - **Property 39: File Upload Size Limit Enforced**
    - **Validates: Requirements 20.8**

  - [x] 14.7 Implement API input validation
    - Validate all request parameters against expected types and formats
    - Return 400 Bad Request with descriptive errors for invalid inputs
    - _Requirements: 20.1_

  - [ ]* 14.8 Write property test for input type validation
    - **Property 33: Input Validation Rejects Invalid Types**
    - **Validates: Requirements 20.1**

  - [x] 14.9 Implement consistent error response format
    - Create error response schema with code, message, and details
    - Apply to all API endpoints
    - Ensure appropriate HTTP status codes (200, 201, 400, 401, 403, 404, 500)
    - _Requirements: 18.8, 19.8_

  - [ ]* 14.10 Write property test for API status codes
    - **Property 32: API Endpoints Return Appropriate Status Codes**
    - **Validates: Requirements 18.8, 19.8**

- [ ] 15. Create base templates and layouts
  - [x] 15.1 Create base template structure
    - Create `app/templates/base.html` with common HTML structure
    - Include meta tags, CSS links, and JavaScript imports
    - Define blocks for title, content, and scripts
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

  - [x] 15.2 Create admin dashboard layout
    - Create `app/templates/admin/layout.html` extending base template
    - Include navigation menu with links to all admin pages
    - Add user info display and logout button
    - Apply responsive CSS for desktop and tablet
    - _Requirements: 15.1, 15.2, 15.5_

  - [x] 15.3 Create QA dashboard layout
    - Create `app/templates/qa/layout.html` extending base template
    - Include navigation menu with links to all QA pages
    - Add user info display and logout button
    - Apply responsive CSS for desktop and tablet
    - _Requirements: 15.3, 15.4, 15.5_

  - [x] 15.4 Create base CSS stylesheet
    - Create `app/static/css/base.css` with variables and common styles
    - Implement responsive grid layout
    - Style forms, tables, buttons, and navigation
    - Ensure touch-friendly elements for tablets
    - _Requirements: 15.5, 15.6_

- [ ] 16. Create admin dashboard pages
  - [x] 16.1 Create admin dashboard home page
    - Create `app/templates/admin/index.html` with system overview
    - Display system health metrics, recent activity summary, quick action buttons
    - Create route handler at `/admin/` requiring admin role
    - _Requirements: 1.1, 1.3_

  - [x] 16.2 Create user management page
    - Create `app/templates/admin/users.html` with user list table
    - Include search/filter controls, create user modal, edit user modal
    - Create route handler at `/admin/users` requiring admin role
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 16.3 Create role management page
    - Create `app/templates/admin/roles.html` with role list and permissions
    - Display role assignment interface
    - Create route handler at `/admin/roles` requiring admin role
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 16.4 Create system configuration page
    - Create `app/templates/admin/config.html` with dropdown configuration editor
    - Include LGA assignment interface
    - Create route handler at `/admin/config` requiring admin role
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [x] 16.5 Create shapefile management page
    - Create `app/templates/admin/shapefiles.html` with upload interface
    - Display version history table and activation controls
    - Create route handler at `/admin/shapefiles` requiring admin role
    - _Requirements: 7.1, 7.4, 7.5_

  - [x] 16.6 Create data export page
    - Create `app/templates/admin/export.html` with export format selection
    - Include filter configuration and download links
    - Create route handler at `/admin/export` requiring admin role
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 16.7 Create monitoring page
    - Create `app/templates/admin/monitoring.html` with sync session logs
    - Display system health dashboard and record statistics
    - Create route handler at `/admin/monitoring` requiring admin role
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.6_

  - [x] 16.8 Create audit log viewer page
    - Create `app/templates/admin/audit.html` with paginated audit log
    - Include filters for user, operation, and date
    - Create route handler at `/admin/audit` requiring admin role

- [ ] 17. Create QA dashboard pages
  - [x] 17.1 Create QA dashboard home page
    - Create `app/templates/qa/index.html` with QA statistics summary
    - Display pending records count and recent activity
    - Create route handler at `/qa/` requiring qa_officer or admin role
    - _Requirements: 2.1, 2.3, 2.4_

  - [x] 17.2 Create record list page
    - Create `app/templates/qa/records.html` with paginated record table
    - Include multi-dimensional filters (status, LGA, ward, enumerator, date)
    - Display quick status indicators
    - Create route handler at `/qa/records` requiring qa_officer or admin role
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.8_

  - [x] 17.3 Create record detail page
    - Create `app/templates/qa/record_detail.html` with complete record information
    - Include photo gallery, interactive map, approval/rejection controls
    - Display audit trail
    - Create route handler at `/qa/records/{id}` requiring qa_officer or admin role
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 12.1, 12.2_

  - [x] 17.4 Create QA reports page
    - Create `app/templates/qa/reports.html` with QA statistics by enumerator
    - Display approval rate charts and review time metrics
    - Create route handler at `/qa/reports` requiring qa_officer or admin role
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6_

  - [x] 17.5 Create flagged records page
    - Create `app/templates/qa/flagged.html` with records that have QA flags
    - Include bulk review interface
    - Create route handler at `/qa/flagged` requiring qa_officer or admin role

- [x] 18. Implement JavaScript utilities and interactions
  - [x] 18.1 Create common JavaScript utilities
    - Create `app/static/js/common.js` with AJAX helper functions
    - Implement notification/toast system for user feedback
    - Implement error handling for API requests
    - _Requirements: 17.3, 17.4_

  - [x] 18.2 Create admin JavaScript modules
    - Create `app/static/js/admin/users.js` for user management interactions
    - Create `app/static/js/admin/config.js` for configuration editor
    - Create `app/static/js/admin/shapefiles.js` for shapefile upload handling
    - Create `app/static/js/admin/export.js` for export task management
    - Create `app/static/js/admin/monitoring.js` for real-time monitoring updates
    - _Requirements: 17.2_

  - [x] 18.3 Create QA JavaScript modules
    - Create `app/static/js/qa/records.js` for record list filtering and pagination
    - Create `app/static/js/qa/record_detail.js` for record detail interactions
    - Create `app/static/js/qa/reports.js` for report generation
    - _Requirements: 17.1_

  - [x] 18.4 Implement real-time data updates
    - Add polling for QA dashboard (60 second interval for new records)
    - Add polling for admin monitoring (30 second interval for metrics)
    - Display last update timestamp
    - Provide manual refresh button
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5_

- [x] 19. Implement session management and token refresh
  - [x] 19.1 Implement automatic token refresh
    - Add middleware to refresh JWT tokens for active sessions (within 7 hours)
    - Update HTTP-only cookie with new token
    - _Requirements: 16.2_

  - [ ]* 19.2 Write property test for token refresh
    - **Property 30: Token Refresh Within Valid Window**
    - **Validates: Requirements 16.2**

  - [x] 19.3 Implement single session per user enforcement
    - Track active sessions per user account
    - Invalidate existing sessions on new login
    - _Requirements: 16.5_

  - [ ]* 19.4 Write property test for single session enforcement
    - **Property 31: Single Session Per User Account**
    - **Validates: Requirements 16.5**

  - [x] 19.5 Implement logout functionality
    - Create logout endpoint to invalidate current token
    - Clear HTTP-only cookie
    - Redirect to login page
    - _Requirements: 16.4_

- [x] 20. Implement error handling and logging
  - [x] 20.1 Create consistent error response format
    - Define error response schema with code, message, and details
    - Implement error handler middleware for FastAPI
    - Map exceptions to appropriate HTTP status codes
    - _Requirements: 18.8, 19.8_

  - [x] 20.2 Implement error logging
    - Log all errors with timestamp, request ID, user ID, endpoint, error type
    - Include stack traces for 500 errors
    - Configure log rotation and retention
    - _Requirements: 9.6_

  - [x] 20.3 Create user-friendly error messages
    - Provide clear, actionable error messages for end users
    - Avoid exposing system internals in error messages
    - Include guidance on resolution where appropriate
    - _Requirements: 7.6_

- [ ] 21. Checkpoint - Ensure all frontend and integration tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 22. Implement database optimization
  - [x] 22.1 Add database indexes for performance
    - Add index on audit_log(entity_type, entity_id)
    - Add index on buildings(verification_status)
    - Add index on streets(verification_status)
    - Add index on export_tasks(status, created_at)
    - Add index on users(username) if not exists
    - _Requirements: 10.7_

  - [x] 22.2 Optimize record listing queries
    - Use proper joins to fetch related data efficiently
    - Implement query result caching for statistics
    - Ensure pagination queries are optimized
    - _Requirements: 10.7_

  - [x] 22.3 Configure database connection pooling
    - Set appropriate pool size for concurrent requests
    - Configure connection timeout and retry logic
    - _Requirements: 9.2_

- [x] 23. Create database migration for export_tasks
  - [x] 23.1 Create Alembic migration script
    - Generate migration for export_tasks table
    - Include all indexes and constraints
    - Test migration up and down
    - _Requirements: 8.6_

- [x] 24. Implement background worker for export processing
  - [x] 24.1 Create background worker for async export generation
    - Set up Celery or similar task queue (or use FastAPI BackgroundTasks)
    - Implement worker to process pending export tasks
    - Update task status and file_path on completion
    - Handle errors and update error_message field
    - _Requirements: 8.6_

  - [x] 24.2 Implement export file cleanup
    - Create scheduled task to delete old export files
    - Keep exports for 7 days before cleanup
    - Update export_tasks records when files are deleted

- [x] 25. Integration and wiring
  - [x] 25.1 Register all route handlers in FastAPI application
    - Import and include admin route handlers
    - Import and include QA route handlers
    - Import and include auth route handlers
    - Configure static file serving for CSS and JavaScript
    - Configure Jinja2 template directory
    - _Requirements: 1.1, 2.1_

  - [x] 25.2 Configure authentication middleware
    - Add JWT authentication middleware to FastAPI app
    - Configure middleware to handle both HTML and API endpoints
    - Set up HTTP-only cookie configuration
    - _Requirements: 1.2, 2.2, 16.1_

  - [x] 25.3 Wire services to API endpoints
    - Inject UserService into admin endpoints
    - Inject QAService into QA endpoints
    - Inject ExportService into export endpoints
    - Configure database session dependency injection
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 19.1, 19.2, 19.3, 19.4, 19.5, 19.6_

  - [x] 25.4 Configure CORS and security headers
    - Set up CORS middleware if needed for API access
    - Add security headers (X-Frame-Options, X-Content-Type-Options, etc.)
    - Configure CSRF protection for forms
    - _Requirements: 20.3_

  - [x] 25.5 Set up environment configuration
    - Document required environment variables
    - Set default values for JWT expiration, rate limits, file upload limits
    - Configure logging levels and output
    - _Requirements: 3.4, 20.5, 20.8_

  - [ ]* 25.6 Write integration tests for complete workflows
    - Test complete user management workflow (create, update, reset password)
    - Test complete QA workflow (list, filter, view detail, approve/reject)
    - Test complete export workflow (request, check status, download)
    - Test authentication and authorization across all endpoints

- [x] 26. Final checkpoint - Ensure all tests pass and system is ready for deployment
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- All backend code uses Python with FastAPI and SQLAlchemy
- All frontend code uses Jinja2 templates with vanilla JavaScript
- Authentication uses JWT tokens stored in HTTP-only cookies
- All API endpoints follow RESTful conventions

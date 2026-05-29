# Task 6.4 Implementation: Shapefile Management Endpoints

## Overview
Implemented two new admin endpoints for shapefile version management as specified in Task 6.4 of the admin-qa-dashboards spec.

## Endpoints Implemented

### 1. GET `/api/v1/admin/shapefiles`
**Purpose**: List all shapefile versions with metadata

**Authorization**: Requires admin role

**Response Format**:
```json
[
  {
    "id": 1,
    "layer_name": "lga",
    "version_tag": "2024-Q1",
    "checksum_sha256": "abc123...",
    "uploaded_by": "uuid-string",
    "uploaded_at": "2024-01-15T10:30:00Z",
    "is_active": true
  }
]
```

**Features**:
- Returns all shapefile versions sorted by upload timestamp (most recent first)
- Includes version number, upload timestamp, active status, layer name, and uploader information
- Requires admin role authentication

### 2. PATCH `/api/v1/admin/shapefiles/{id}/activate`
**Purpose**: Mark a specific shapefile version as active

**Authorization**: Requires admin role

**Parameters**:
- `id` (path parameter): The shapefile version ID to activate

**Response Format**:
```json
{
  "status": "activated"
}
```

**Features**:
- Activates the specified shapefile version
- Automatically deactivates all other versions for the same layer
- Returns 404 if the shapefile ID is not found
- Creates an audit log entry for the activation
- Requires admin role authentication

## Implementation Details

### File Modified
- `feva-backend/app/api/v1/admin.py`

### Key Implementation Points

1. **List Shapefiles Endpoint**:
   - Queries all `ShapefileVersion` records from the database
   - Orders results by `uploaded_at` descending
   - Returns comprehensive metadata for each version
   - Uses `require_role("admin")` dependency for authorization

2. **Activate Shapefile Endpoint**:
   - Validates that the target shapefile version exists
   - Fetches all versions for the same layer
   - Sets `is_active=True` for the target version
   - Sets `is_active=False` for all other versions of the same layer
   - Preserves active status for versions of different layers
   - Creates audit log entry with operation details
   - Returns appropriate error responses (404 for invalid IDs)

### Authorization
Both endpoints use the existing `require_role("admin")` dependency to ensure only admin users can access them. Non-admin users receive a 403 Forbidden response.

### Audit Logging
The activate endpoint creates an audit log entry with:
- Operation: "activate_shapefile"
- Entity type: "shapefile_version"
- Entity ID: The shapefile version ID
- Details: Layer name and version tag

## Testing

### Test File Created
- `feva-backend/tests/test_shapefile_management_endpoints.py`

### Test Coverage
The test file includes 8 comprehensive tests:

1. **test_list_shapefiles_requires_admin_role**: Verifies that non-admin users cannot list shapefiles
2. **test_list_shapefiles_returns_empty_list**: Verifies empty list response when no shapefiles exist
3. **test_list_shapefiles_returns_all_versions**: Verifies all versions are returned with correct metadata
4. **test_activate_shapefile_requires_admin_role**: Verifies that non-admin users cannot activate shapefiles
5. **test_activate_shapefile_returns_404_for_invalid_id**: Verifies 404 response for non-existent IDs
6. **test_activate_shapefile_marks_version_as_active**: Verifies activation updates the correct version
7. **test_activate_shapefile_deactivates_other_versions_same_layer**: Verifies only one version per layer is active
8. **test_activate_shapefile_creates_audit_log**: Verifies audit log entries are created

### Endpoint Verification
Verified that both endpoints are properly registered in the FastAPI application:
```
GET /api/v1/admin/shapefiles
PATCH /api/v1/admin/shapefiles/{id}/activate
```

## Requirements Satisfied

This implementation satisfies the following requirements from the spec:

- **Requirement 7.4**: Display list of all shapefile versions
- **Requirement 7.5**: Allow marking a specific shapefile version as active
- **Requirement 18.4**: RESTful API endpoints for shapefile management
- **Requirement 18.7**: All admin API endpoints require authentication with admin role

## API Patterns Followed

The implementation follows existing patterns in the codebase:
- Uses FastAPI router and dependency injection
- Follows RESTful conventions (GET for listing, PATCH for updates)
- Returns appropriate HTTP status codes (200, 404, 403)
- Uses consistent error response format
- Implements role-based authorization
- Creates audit log entries for state-changing operations
- Uses async/await patterns with SQLAlchemy AsyncSession

## Integration

The endpoints integrate seamlessly with:
- Existing `ShapefileVersion` model
- Existing `AuditLog` model
- Existing `require_role()` authorization middleware
- Existing database session management
- Existing shapefile upload endpoint (POST `/api/v1/admin/shapefiles`)

## Status

✅ Implementation complete
✅ Endpoints registered and accessible
✅ Authorization implemented
✅ Audit logging implemented
✅ Test file created with comprehensive coverage
✅ Follows existing code patterns and conventions

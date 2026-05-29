# Task 4.1 Implementation: Role Management Endpoints

## Summary

Implemented GET `/api/v1/admin/roles` endpoint that lists all roles with their associated permissions.

## Requirements Addressed

- **5.1**: Display all available roles (admin, enumerator, supervisor, qa_officer)
- **5.2**: Allow viewing of roles
- **5.3**: Display permissions associated with each role
- **18.2**: Provide RESTful API endpoints for role management
- **18.7**: All admin API endpoints require authentication with Admin_User role

## Implementation Details

### Endpoint

**GET `/api/v1/admin/roles`**

- **Authentication**: Requires admin role
- **Returns**: Array of role objects with id, name, and permissions

### Response Format

```json
[
  {
    "id": 1,
    "name": "admin",
    "permissions": [
      "manage_users",
      "manage_roles",
      "manage_system_config",
      "manage_shapefiles",
      "export_data",
      "view_audit_logs",
      "view_monitoring",
      "review_records",
      "manage_dropdown_config"
    ]
  },
  {
    "id": 2,
    "name": "enumerator",
    "permissions": [
      "create_records",
      "edit_own_records",
      "upload_photos",
      "sync_data"
    ]
  },
  {
    "id": 3,
    "name": "supervisor",
    "permissions": [
      "create_records",
      "edit_own_records",
      "upload_photos",
      "sync_data",
      "view_team_records",
      "submit_feedback"
    ]
  },
  {
    "id": 4,
    "name": "qa_officer",
    "permissions": [
      "review_records",
      "approve_records",
      "reject_records",
      "view_qa_statistics",
      "view_audit_trail"
    ]
  }
]
```

### Permission Definitions

#### Admin Permissions
- `manage_users`: Create, update, delete user accounts
- `manage_roles`: View and assign roles to users
- `manage_system_config`: Configure system settings and dropdown options
- `manage_shapefiles`: Upload and manage boundary shapefiles
- `export_data`: Export records and audit logs
- `view_audit_logs`: View system audit trail
- `view_monitoring`: View system health and sync sessions
- `review_records`: Review and approve/reject enumeration records
- `manage_dropdown_config`: Manage dropdown configuration options

#### Enumerator Permissions
- `create_records`: Create new building and street records
- `edit_own_records`: Edit their own submitted records
- `upload_photos`: Upload photos for records
- `sync_data`: Synchronize data with the server

#### Supervisor Permissions
- All enumerator permissions plus:
- `view_team_records`: View records from their team
- `submit_feedback`: Submit pilot feedback during UAT

#### QA Officer Permissions
- `review_records`: View submitted records for review
- `approve_records`: Approve records after review
- `reject_records`: Reject records with comments
- `view_qa_statistics`: View QA metrics and statistics
- `view_audit_trail`: View audit trail for records

## Files Modified

1. **feva-backend/app/api/v1/admin.py**
   - Added `list_roles()` endpoint function
   - Defined role permissions mapping
   - Returns roles with their associated permissions

2. **feva-backend/tests/test_role_management_endpoints.py** (Created)
   - Test suite for role management endpoints
   - Tests for authorization requirements
   - Tests for permission verification

## Testing

The endpoint has been implemented and is ready for testing. To test manually:

1. Start the backend server
2. Authenticate as an admin user
3. Make a GET request to `/api/v1/admin/roles` with the admin token
4. Verify the response contains all four roles with their permissions

### Example cURL Command

```bash
curl -X GET "http://localhost:8000/api/v1/admin/roles" \
  -H "Authorization: Bearer <admin_token>"
```

## Notes

- The permissions are currently defined as a static mapping in the endpoint code
- Future enhancements could move permissions to the database for more flexibility
- The endpoint requires admin role authentication via the `require_role("admin")` dependency
- All roles are fetched from the database and matched with their permission sets

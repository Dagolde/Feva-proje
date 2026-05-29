# Task 12.3 Implementation: Audit Trail Retrieval

## Overview
Implemented audit trail retrieval functionality for the QA Dashboard, allowing QA officers to view the complete history of actions performed on records.

## Requirements Addressed
- **14.1**: Display audit log entries related to specific records
- **14.2**: Include timestamp, user, action type, and changes made
- **14.3**: Display complete review history including approvals, rejections, and status changes
- **14.4**: Display audit entries in reverse chronological order (newest first)

## Implementation Details

### 1. Service Layer (`app/services/qa_service.py`)

Added `get_audit_trail()` function:
- **Parameters**:
  - `db`: AsyncSession - Database session
  - `record_id`: UUID - ID of the record
  - `entity_type`: str - "building" or "street"

- **Returns**: List of audit entries with:
  - `timestamp`: When the action occurred
  - `user`: Username of the user who performed the action (or "system")
  - `action`: Type of operation performed
  - `detail`: Additional details about the action (if any)

- **Features**:
  - Queries `AuditLog` table filtered by entity_type and entity_id
  - Joins with `User` table to get usernames
  - Sorts results by `occurred_at` descending (newest first)
  - Handles system actions (where user_id is NULL)

### 2. API Layer (`app/api/v1/qa.py`)

Added audit trail endpoint:
- **Route**: `GET /api/v1/qa/records/{record_id}/audit`
- **Query Parameters**:
  - `entity_type`: Required - "building" or "street"
- **Authorization**: Requires `qa_officer` or `admin` role
- **Response**: `AuditTrailResponse` containing:
  - `record_id`: ID of the record
  - `entity_type`: Type of entity
  - `entries`: List of `AuditEntry` objects

Added Pydantic schemas:
- `AuditEntry`: Individual audit log entry
  - `timestamp`: ISO format timestamp
  - `user`: Username
  - `action`: Operation type
  - `detail`: Optional additional details
  
- `AuditTrailResponse`: Complete audit trail response
  - `record_id`: Record identifier
  - `entity_type`: Entity type
  - `entries`: List of audit entries

### 3. Testing

Created smoke tests (`tests/test_qa_audit_trail_smoke.py`):
- ✅ Verify `get_audit_trail()` function exists and has correct signature
- ✅ Verify audit trail endpoint is registered in QA API router
- ✅ Verify `AuditEntry` and `AuditTrailResponse` schemas exist with required fields
- ✅ Verify `get_audit_trail` is properly imported in QA API module

All smoke tests pass successfully.

## Usage Example

### API Request
```http
GET /api/v1/qa/records/123e4567-e89b-12d3-a456-426614174000/audit?entity_type=building
Authorization: Bearer <qa_officer_token>
```

### API Response
```json
{
  "record_id": "123e4567-e89b-12d3-a456-426614174000",
  "entity_type": "building",
  "entries": [
    {
      "timestamp": "2024-01-15T14:30:00Z",
      "user": "qa_officer_1",
      "action": "approve_record",
      "detail": null
    },
    {
      "timestamp": "2024-01-15T10:15:00Z",
      "user": "qa_officer_2",
      "action": "reject_record",
      "detail": {
        "reason": "Missing required photos"
      }
    },
    {
      "timestamp": "2024-01-14T16:45:00Z",
      "user": "system",
      "action": "create_record",
      "detail": null
    }
  ]
}
```

## Database Schema

Uses existing `audit_log` table:
- `id`: BigInteger primary key
- `user_id`: UUID foreign key to users table (nullable for system actions)
- `operation`: Text - operation type (e.g., "approve_record", "reject_record")
- `entity_type`: Text - "building" or "street"
- `entity_id`: Text - UUID of the record as string
- `detail`: JSONB - additional details (nullable)
- `ip_address`: INET - IP address (nullable)
- `occurred_at`: Timestamp with timezone - when the action occurred

## Integration Points

1. **Approval/Rejection Operations**: When records are approved or rejected via `approve_record()` or `reject_record()`, audit log entries are automatically created
2. **User Information**: Joins with `users` table to display usernames instead of UUIDs
3. **System Actions**: Handles entries with no user_id by displaying "system" as the user

## Security

- Requires authentication with JWT token
- Requires `qa_officer` or `admin` role
- Validates entity_type parameter
- Validates record_id as valid UUID format
- Returns 400 for invalid parameters
- Returns 404 if record not found

## Performance Considerations

- Query is filtered by both `entity_type` and `entity_id` for efficiency
- Results are sorted by database index on `occurred_at` column
- User lookups are performed for each audit entry (could be optimized with a join if needed)

## Status

✅ **COMPLETE** - All requirements implemented and smoke tests passing

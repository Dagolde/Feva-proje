# Task 4.2 Implementation: Last Admin Validation

## Overview
Implemented validation to prevent removing the last active admin user from the system, satisfying Requirement 5.5.

## Changes Made

### 1. User Service (`app/services/user_service.py`)

#### Added Helper Function
- `_count_active_admins(db)`: Counts active (non-locked) admin users

#### Modified `update_user()` Function
- Added validation before role changes
- Checks if user is currently an active admin
- Prevents role change if user is the last active admin
- Raises `ValueError` with message: "Cannot change role of the last active admin user"

#### Modified `deactivate_user()` Function
- Added validation before deactivation
- Checks if user is currently an active admin
- Prevents deactivation if user is the last active admin
- Raises `ValueError` with message: "Cannot deactivate the last active admin user"

### 2. API Endpoints (`app/api/v1/admin.py`)
- No changes required - endpoints already handle ValueError exceptions
- Returns 400 Bad Request with error message when validation fails

### 3. Tests (`tests/test_user_management_endpoints.py`)
Added four new test cases:
- `test_cannot_change_last_admin_role`: Verifies role change is blocked for last admin
- `test_cannot_deactivate_last_admin`: Verifies deactivation is blocked for last admin
- `test_can_change_role_when_multiple_admins_exist`: Verifies operations work with multiple admins
- `test_can_deactivate_when_multiple_admins_exist`: Verifies operations work with multiple admins

## Validation Logic

The validation works as follows:
1. When updating a user's role or deactivating a user
2. Check if the user currently has the admin role and is not locked
3. If yes, count all active admin users in the system
4. If count <= 1, reject the operation with a descriptive error
5. Otherwise, allow the operation to proceed

## Testing

Manual testing confirmed:
- ✅ Cannot change last admin's role
- ✅ Cannot deactivate last admin
- ✅ Can change role when multiple admins exist
- ✅ Can deactivate when multiple admins exist
- ✅ Error messages are clear and descriptive

## Requirements Satisfied
- Requirement 5.5: System SHALL prevent removal of the last Admin_User

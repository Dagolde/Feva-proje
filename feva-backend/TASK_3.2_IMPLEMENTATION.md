# Task 3.2 Implementation: User Management API Endpoints

## Overview
Implemented user management API endpoints at `/api/v1/admin/users` as specified in Task 3.2 of the admin-qa-dashboards spec.

## Changes Made

### 1. Updated `/feva-backend/app/api/v1/admin.py`

Refactored existing user management endpoints to use the `UserService` and added the missing reset-password endpoint:

#### Endpoints Implemented:

1. **GET `/api/v1/admin/users`** - List users with pagination
   - Query parameters: `page` (default: 1), `page_size` (default: 50)
   - Returns: `{total, page, page_size, items[]}`
   - Uses: `user_service.list_users()`

2. **POST `/api/v1/admin/users`** - Create new user
   - Request body: `{username, email, password, role_id, lga_assignment?}`
   - Validates password complexity before creation
   - Returns: `{id, username}`
   - Uses: `user_service.create_user()`

3. **PATCH `/api/v1/admin/users/{user_id}`** - Update user
   - Request body: `{role_id?, lga_assignment?, locked?}`
   - Returns: `{status: "ok"}`
   - Uses: `user_service.update_user()`

4. **DELETE `/api/v1/admin/users/{user_id}`** - Deactivate user
   - Soft delete (locks the account)
   - Returns: `{status: "deactivated"}`
   - Uses: `user_service.deactivate_user()`

5. **POST `/api/v1/admin/users/{user_id}/reset-password`** - Reset password (NEW)
   - Request body: `{new_password}`
   - Validates password complexity
   - Returns: `{status: "ok"}`
   - Uses: `user_service.reset_password()`

#### Pydantic Schemas:

- `UserCreate`: For creating new users
- `UserPatch`: For updating existing users
- `PasswordReset`: For password reset requests (NEW)

### 2. Integration with UserService

All endpoints now use the existing `UserService` functions from `/feva-backend/app/services/user_service.py`:
- `create_user()` - Creates user with audit logging
- `update_user()` - Updates user with change tracking
- `reset_password()` - Resets password and clears failed attempts
- `list_users()` - Lists users with pagination
- `deactivate_user()` - Soft deletes user account

### 3. Security Features

- All endpoints require admin role via `require_role("admin")` dependency
- Password complexity validation on user creation and password reset
- Proper error handling with appropriate HTTP status codes:
  - 200: Success
  - 201: Created
  - 400: Bad Request (validation errors)
  - 401: Unauthorized
  - 403: Forbidden (non-admin users)
  - 404: Not Found (user doesn't exist)

### 4. Audit Logging

All user management operations are automatically logged via the UserService:
- User creation
- User updates (role changes, LGA assignments, lock status)
- Password resets
- User deactivation

## Requirements Satisfied

- **Requirement 18.1**: RESTful API endpoints for user CRUD operations at `/api/v1/admin/users`
- **Requirement 18.7**: All admin API endpoints require authentication with Admin_User role

## Testing

Created comprehensive integration tests in `/feva-backend/tests/test_user_management_endpoints.py`:
- Test list users with pagination
- Test create user endpoint
- Test duplicate username rejection
- Test update user endpoint
- Test deactivate user endpoint
- Test reset password endpoint
- Test weak password rejection
- Test admin role requirement

## Notes

- The UserService was already implemented in Task 3.1
- The `require_role("admin")` dependency was already available in `app/core/deps.py`
- All endpoints follow RESTful conventions and return appropriate HTTP status codes
- Password complexity validation is enforced on both user creation and password reset
- Audit logging is handled automatically by the UserService layer

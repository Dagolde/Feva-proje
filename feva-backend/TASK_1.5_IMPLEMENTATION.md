# Task 1.5 Implementation: Authentication Redirect for Unauthenticated Users

## Overview
Implemented authentication redirect middleware that handles unauthenticated requests appropriately based on the endpoint type:
- **HTML routes** (`/admin/*`, `/qa/*`): Redirect to login page
- **API routes** (`/api/*`): Return 401 Unauthorized JSON response

## Requirements Addressed
- **Requirement 1.2**: WHEN an unauthenticated user attempts to access `/admin/`, THE System SHALL redirect to the login page
- **Requirement 2.2**: WHEN an unauthenticated user attempts to access `/qa/`, THE System SHALL redirect to the login page

## Implementation Details

### 1. Authentication Exception Handler
**File**: `feva-backend/app/middleware/auth_redirect.py`

Created an exception handler that intercepts 401 Unauthorized errors from FastAPI's authentication system:
- For HTML routes (`/admin/*`, `/qa/*`): Redirects to `/login?next={original_path}`
- For API routes: Returns JSON 401 response with appropriate headers

### 2. Login Page
**File**: `feva-backend/app/templates/login.html`

Created a clean, responsive login page with:
- Username and password fields
- Client-side form validation
- Error message display
- Automatic redirect after successful login based on user role
- Support for "next" parameter to redirect back to originally requested page

### 3. Login Route Handler
**File**: `feva-backend/app/api/login.py`

Simple route handler that renders the login page template.

### 4. Dashboard Routes
**Files**: 
- `feva-backend/app/api/admin_dashboard.py`
- `feva-backend/app/api/qa_dashboard.py`

Created placeholder dashboard pages for:
- Admin dashboard at `/admin/` (requires admin role)
- QA dashboard at `/qa/` (requires qa_officer or admin role)

Both pages display user information and include a logout button.

### 5. Enhanced Authentication Dependencies
**File**: `feva-backend/app/core/deps.py`

Updated `get_current_user` dependency to check for JWT tokens in:
1. Authorization header (Bearer token) - for API requests
2. HTTP-only cookies - for web dashboard requests

### 6. Enhanced Login Endpoint
**File**: `feva-backend/app/api/v1/auth.py`

Modified the login endpoint to:
- Set an HTTP-only cookie with the access token
- Return the token response as JSON (for API clients)
- Support both cookie-based (web) and header-based (API) authentication

### 7. Main Application Configuration
**File**: `feva-backend/app/main.py`

Registered:
- Exception handler for 401 errors
- Login route
- Admin dashboard route
- QA dashboard route

## Testing

Created comprehensive tests in `feva-backend/tests/test_auth_redirect.py`:

1. ✅ `test_unauthenticated_admin_route_redirects_to_login` - Verifies `/admin/` redirects to login
2. ✅ `test_unauthenticated_qa_route_redirects_to_login` - Verifies `/qa/` redirects to login
3. ✅ `test_unauthenticated_api_route_returns_401` - Verifies API routes return 401
4. ✅ `test_login_page_accessible_without_auth` - Verifies login page is accessible
5. ✅ `test_health_endpoint_accessible_without_auth` - Verifies health check works
6. ✅ `test_login_endpoint_accessible_without_auth` - Verifies login API is accessible

All tests pass successfully.

## How It Works

### For HTML Routes:
1. User navigates to `/admin/` or `/qa/` without authentication
2. FastAPI's `require_role` dependency checks for authentication
3. No valid token found → raises HTTPException with 401 status
4. Exception handler intercepts the 401 error
5. Detects it's an HTML route (starts with `/admin` or `/qa`)
6. Returns RedirectResponse to `/login?next=/admin/` (or `/qa/`)
7. User logs in successfully
8. Login page redirects back to original URL

### For API Routes:
1. Client makes request to `/api/v1/admin/users` without authentication
2. FastAPI's `require_role` dependency checks for authentication
3. No valid token found → raises HTTPException with 401 status
4. Exception handler intercepts the 401 error
5. Detects it's an API route (starts with `/api`)
6. Returns JSONResponse with 401 status and error details

## Security Features

1. **HTTP-only cookies**: Access tokens stored in HTTP-only cookies prevent XSS attacks
2. **SameSite protection**: Cookies use `samesite="lax"` to prevent CSRF attacks
3. **Token expiration**: Tokens expire after 8 hours (configurable)
4. **Role-based access**: Admin and QA dashboards enforce role requirements
5. **Secure redirects**: Login redirects preserve the originally requested URL

## Future Enhancements

For production deployment, consider:
1. Set `secure=True` for cookies when using HTTPS
2. Implement CSRF token protection for forms
3. Add rate limiting for login attempts
4. Implement session management and token refresh
5. Add logout functionality that clears cookies

## Files Created/Modified

### Created:
- `feva-backend/app/middleware/__init__.py`
- `feva-backend/app/middleware/auth_redirect.py`
- `feva-backend/app/api/login.py`
- `feva-backend/app/api/admin_dashboard.py`
- `feva-backend/app/api/qa_dashboard.py`
- `feva-backend/app/templates/login.html`
- `feva-backend/tests/test_auth_redirect.py`
- `feva-backend/TASK_1.5_IMPLEMENTATION.md`

### Modified:
- `feva-backend/app/main.py` - Registered exception handler and new routes
- `feva-backend/app/core/deps.py` - Enhanced to check cookies for tokens
- `feva-backend/app/api/v1/auth.py` - Added cookie setting to login endpoint
- `feva-backend/tests/conftest.py` - Added fixtures for authenticated testing

## Conclusion

Task 1.5 has been successfully implemented. The system now properly handles unauthenticated requests by:
- Redirecting HTML dashboard requests to the login page
- Returning 401 Unauthorized for API requests
- Supporting both cookie-based (web) and header-based (API) authentication
- Preserving the originally requested URL for post-login redirect

All tests pass and the implementation follows FastAPI best practices.

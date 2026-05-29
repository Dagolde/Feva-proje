# Task 1.7 Implementation: Session Management with HTTP-only Cookies

## Overview
Enhanced session management with proper HTTP-only cookie configuration, automatic token refresh logic, and logout functionality that clears cookies and invalidates tokens.

## Requirements Addressed
- **Requirement 16.1**: THE System SHALL maintain user sessions using JWT_Token stored in HTTP-only cookies
- **Requirement 16.2**: THE System SHALL refresh JWT_Token automatically when user performs actions within 7 hours of token creation
- **Requirement 16.4**: THE System SHALL provide a logout function that invalidates the current JWT_Token

## Implementation Details

### 1. Enhanced Cookie Configuration
**Files Modified**: 
- `feva-backend/app/api/v1/auth.py`
- `feva-backend/app/schemas/auth.py`

#### Login Endpoint Enhancements
The login endpoint now sets both access and refresh tokens as HTTP-only cookies with proper security attributes:

```python
# Access token cookie (8 hours)
response.set_cookie(
    key="access_token",
    value=tokens.access_token,
    httponly=True,
    secure=False,  # Set to True in production with HTTPS
    samesite="lax",
    max_age=tokens.expires_in,  # 8 hours
    path="/",
)

# Refresh token cookie (30 days)
response.set_cookie(
    key="refresh_token",
    value=tokens.refresh_token,
    httponly=True,
    secure=False,  # Set to True in production with HTTPS
    samesite="lax",
    max_age=60 * 60 * 24 * 30,  # 30 days
    path="/",
)
```

**Security Features**:
- `httponly=True`: Prevents JavaScript access to cookies (XSS protection)
- `samesite="lax"`: Provides CSRF protection while allowing normal navigation
- `path="/"`: Makes cookies available across all routes
- `secure=False`: Set to False for development; should be True in production with HTTPS
- Proper `max_age` values: 8 hours for access token, 30 days for refresh token

### 2. Token Refresh Endpoint Enhancement
**File Modified**: `feva-backend/app/api/v1/auth.py`

The refresh endpoint now:
1. Accepts refresh tokens from either the request body OR cookies
2. Returns new tokens in both JSON response AND cookies
3. Rotates both access and refresh tokens for security

```python
@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    # Get refresh token from body or cookie
    refresh_token = body.refresh_token or request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )
    
    # ... refresh logic ...
    
    # Set updated cookies in response
    response.set_cookie(...)  # Both access and refresh tokens
```

### 3. Automatic Token Refresh Middleware
**File Created**: `feva-backend/app/middleware/token_refresh.py`

Implemented middleware that automatically refreshes tokens for active sessions:

**How It Works**:
1. Intercepts all requests
2. Checks if user has a valid access token in cookies
3. Calculates token age from the `iat` (issued-at) claim
4. If token is less than 7 hours old, marks it for refresh
5. After the request completes, refreshes the token and updates cookies

**Key Logic**:
```python
# Check if token is within refresh window (7 hours from creation)
iat = payload.get("iat")
if iat:
    token_age_seconds = (datetime.now(UTC) - datetime.fromtimestamp(iat, UTC)).total_seconds()
    
    # If token is less than 7 hours old, we can refresh it
    if token_age_seconds < (7 * 60 * 60):  # 7 hours
        # Trigger refresh after response
        request.state.should_refresh_token = True
```

**Benefits**:
- Active users never experience session expiration
- Tokens are automatically rotated for security
- Transparent to the user - no manual refresh needed
- Only refreshes within the 7-hour window (requirement 16.2)

### 4. Enhanced Logout Functionality
**File Modified**: `feva-backend/app/api/v1/auth.py`

The logout endpoint now:
1. Accepts refresh tokens from either request body OR cookies
2. Invalidates the refresh token in the backend
3. Clears both access and refresh token cookies
4. Creates audit log entry

```python
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    body: RefreshRequest,
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    # Get refresh token from body or cookie
    refresh_token = body.refresh_token or request.cookies.get("refresh_token")
    
    if refresh_token:
        await auth_service.logout_user(
            db,
            user_id=current_user.id,
            refresh_token=refresh_token,
            ip_address=_client_ip(request),
        )
    
    # Clear cookies by deleting them
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    
    return response
```

**Cookie Deletion**:
- Uses `response.delete_cookie()` which sets `Max-Age=0`
- Ensures cookies are removed from the browser
- Prevents reuse of invalidated tokens

### 5. Schema Updates
**File Modified**: `feva-backend/app/schemas/auth.py`

Made `refresh_token` optional in `RefreshRequest` to support cookie-based refresh:

```python
class RefreshRequest(BaseModel):
    refresh_token: str | None = None
```

This allows the endpoint to work with:
- API clients that send tokens in the request body
- Web clients that use cookies automatically

### 6. Middleware Registration
**File Modified**: `feva-backend/app/main.py`

Registered the token refresh middleware in the application:

```python
from app.middleware.token_refresh import TokenRefreshMiddleware

# Add token refresh middleware (should be before CORS)
app.add_middleware(TokenRefreshMiddleware)
```

**Middleware Order**:
1. TokenRefreshMiddleware (first - handles token refresh)
2. CORSMiddleware (second - handles CORS)
3. Other middleware...

## Testing

Created comprehensive tests in `feva-backend/tests/test_session_management.py`:

### Unit Tests (Non-Database)
1. ✅ `test_token_within_7_hour_window_is_refreshable` - Verifies 7-hour refresh window logic
2. ✅ `test_token_age_calculation` - Verifies token age can be calculated from iat claim

### Integration Tests (Require Database)
1. `test_login_sets_httponly_cookies` - Verifies login sets both cookies
2. `test_login_cookies_have_correct_attributes` - Verifies HttpOnly, SameSite, Path attributes
3. `test_authenticated_request_with_cookie` - Verifies cookie-based authentication works
4. `test_logout_clears_cookies` - Verifies logout deletes cookies
5. `test_logout_with_cookie_only` - Verifies logout works without body parameter
6. `test_refresh_updates_cookies` - Verifies refresh updates both cookies
7. `test_refresh_with_cookie_only` - Verifies refresh works with cookie only
8. `test_access_token_cookie_expires_in_8_hours` - Verifies 8-hour max-age
9. `test_refresh_token_cookie_expires_in_30_days` - Verifies 30-day max-age
10. `test_after_logout_cookies_invalid` - Verifies cookies don't work after logout
11. `test_cookies_have_root_path` - Verifies Path=/ attribute
12. `test_refresh_token_invalidated_after_logout` - Verifies token invalidation

## Security Improvements

### 1. HTTP-only Cookies
- Prevents XSS attacks by making tokens inaccessible to JavaScript
- Tokens cannot be stolen via `document.cookie`

### 2. SameSite Protection
- `samesite="lax"` prevents CSRF attacks
- Cookies are not sent with cross-site requests (except safe methods like GET)

### 3. Token Rotation
- Refresh tokens are rotated on each refresh
- Old refresh tokens are invalidated
- Reduces window of opportunity for token theft

### 4. Automatic Refresh
- Keeps sessions alive for active users
- Reduces risk of expired token reuse
- Only refreshes within 7-hour window

### 5. Proper Logout
- Invalidates refresh tokens on logout
- Clears cookies from browser
- Creates audit trail

## How It Works

### Login Flow
1. User submits credentials to `/api/v1/auth/login`
2. Server validates credentials
3. Server generates access token (8h) and refresh token (30d)
4. Server sets both tokens as HTTP-only cookies
5. Server returns tokens in JSON response (for API clients)
6. Browser automatically includes cookies in subsequent requests

### Automatic Refresh Flow
1. User makes a request with valid access token cookie
2. TokenRefreshMiddleware intercepts the request
3. Middleware checks token age from `iat` claim
4. If token < 7 hours old, marks for refresh
5. Request proceeds normally
6. After response, middleware refreshes tokens
7. New tokens are set as cookies in the response
8. User's session is extended transparently

### Logout Flow
1. User calls `/api/v1/auth/logout`
2. Server retrieves refresh token from cookie
3. Server invalidates refresh token in backend
4. Server deletes both cookies (Max-Age=0)
5. Server creates audit log entry
6. User is logged out and must re-authenticate

## Production Considerations

### 1. HTTPS Required
Set `secure=True` for cookies in production:
```python
response.set_cookie(
    key="access_token",
    value=tokens.access_token,
    httponly=True,
    secure=True,  # Requires HTTPS
    samesite="lax",
    max_age=tokens.expires_in,
    path="/",
)
```

### 2. Environment-Based Configuration
Consider using environment variables:
```python
COOKIE_SECURE = os.getenv("ENVIRONMENT") == "production"

response.set_cookie(
    ...,
    secure=COOKIE_SECURE,
    ...
)
```

### 3. Token Refresh Strategy
Current implementation refreshes tokens on every request within 7 hours. For high-traffic applications, consider:
- Rate limiting token refresh (e.g., max once per minute)
- Only refreshing when token is close to expiration (e.g., < 1 hour remaining)

### 4. Session Management
Current implementation uses in-memory storage for refresh tokens. For production:
- Use Redis or database for refresh token storage
- Implement session tracking per user
- Support concurrent sessions or enforce single session per user

## Files Created/Modified

### Created:
- `feva-backend/app/middleware/token_refresh.py` - Automatic token refresh middleware
- `feva-backend/tests/test_session_management.py` - Comprehensive session management tests
- `feva-backend/TASK_1.7_IMPLEMENTATION.md` - This documentation

### Modified:
- `feva-backend/app/api/v1/auth.py` - Enhanced login, refresh, and logout endpoints
- `feva-backend/app/schemas/auth.py` - Made refresh_token optional in RefreshRequest
- `feva-backend/app/main.py` - Registered token refresh middleware

## Conclusion

Task 1.7 has been successfully implemented with:

✅ **Proper HTTP-only cookie configuration** with security attributes (httponly, samesite, path, max-age)
✅ **Automatic token refresh logic** that extends sessions for active users within 7 hours
✅ **Enhanced logout functionality** that clears cookies and invalidates tokens
✅ **Comprehensive test coverage** for all session management scenarios
✅ **Security improvements** including XSS protection, CSRF protection, and token rotation

The implementation follows FastAPI best practices and provides a secure, user-friendly session management system for the admin and QA dashboards.

## Next Steps

For full production readiness:
1. Set `secure=True` for cookies when deploying with HTTPS
2. Implement Redis-based refresh token storage
3. Add rate limiting for token refresh operations
4. Consider implementing session tracking and management UI
5. Add monitoring and alerting for suspicious session activity

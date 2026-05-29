"""Middleware for automatic token refresh."""
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import Request, Response
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import decode_token


class TokenRefreshMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically refresh tokens for active sessions.
    
    If a user has a valid access token that is within 7 hours of creation,
    and they make a request, we'll refresh their token to extend their session.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Get access token from cookie
        access_token = request.cookies.get("access_token")
        
        if access_token:
            try:
                payload = decode_token(access_token)
                
                # Check if token is within refresh window (7 hours from creation)
                iat = payload.get("iat")
                if iat:
                    token_age_seconds = (datetime.now(UTC) - datetime.fromtimestamp(iat, UTC)).total_seconds()
                    
                    # If token is less than 7 hours old, we can refresh it
                    # This means active users get their sessions extended
                    if token_age_seconds < (7 * 60 * 60):  # 7 hours
                        # Get refresh token from cookie
                        refresh_token = request.cookies.get("refresh_token")
                        
                        if refresh_token:
                            # We'll trigger a refresh by setting a flag on the request
                            # The actual refresh will happen after the response
                            request.state.should_refresh_token = True
                            request.state.refresh_token = refresh_token
            except JWTError:
                # Invalid token, let the normal auth flow handle it
                pass
        
        # Process the request
        response = await call_next(request)
        
        # After processing, check if we should refresh the token
        if hasattr(request.state, "should_refresh_token") and request.state.should_refresh_token:
            # Import here to avoid circular dependency
            from app.db.session import get_db
            from app.services import auth_service
            
            try:
                # Get a database session
                async for db in get_db():
                    # Refresh the token
                    tokens = await auth_service.refresh_access_token(
                        db, 
                        request.state.refresh_token
                    )
                    
                    # Update cookies in the response
                    response.set_cookie(
                        key="access_token",
                        value=tokens.access_token,
                        httponly=True,
                        secure=False,  # Set to True in production with HTTPS
                        samesite="lax",
                        max_age=tokens.expires_in,
                        path="/",
                    )
                    
                    response.set_cookie(
                        key="refresh_token",
                        value=tokens.refresh_token,
                        httponly=True,
                        secure=False,  # Set to True in production with HTTPS
                        samesite="lax",
                        max_age=60 * 60 * 24 * 30,  # 30 days
                        path="/",
                    )
                    
                    break  # Exit after first iteration
            except Exception:
                # If refresh fails, don't break the response
                # The user will need to re-authenticate when their token expires
                pass
        
        return response

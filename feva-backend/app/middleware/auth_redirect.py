"""Authentication redirect exception handler for HTML and API endpoints.

This module provides an exception handler that intercepts 401 Unauthorized errors:
- HTML routes (/admin/*, /qa/*): Redirect to login page if unauthenticated
- API routes (/api/*): Return 401 Unauthorized JSON response

Requirements: 1.2, 2.2
"""
from __future__ import annotations

from fastapi import Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.exceptions import HTTPException


async def auth_exception_handler(request: Request, exc: HTTPException):
    """Handle 401 Unauthorized exceptions.
    
    For HTML routes (/admin/*, /qa/*), redirect to login page.
    For API routes, return JSON 401 response.
    
    Requirements: 1.2, 2.2
    """
    # Only handle 401 Unauthorized
    if exc.status_code != status.HTTP_401_UNAUTHORIZED:
        # Re-raise other exceptions
        raise exc
    
    path = request.url.path
    
    # Check if this is an HTML route that should redirect
    if path.startswith("/admin") or path.startswith("/qa"):
        # Redirect to login page with next parameter
        return RedirectResponse(
            url=f"/login?next={path}",
            status_code=status.HTTP_302_FOUND
        )
    
    # For API routes, return JSON response
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.detail or "Not authenticated"},
        headers={"WWW-Authenticate": "Bearer"},
    )

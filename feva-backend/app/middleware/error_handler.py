"""Consistent error handling middleware and exception handlers.

Provides:
- Structured error response format: {code, message, details}
- Error logging with request context
- User-friendly messages that avoid leaking system internals

Requirements: 18.8, 19.8, 9.6, 7.6
"""
from __future__ import annotations

import logging
import traceback
import uuid
from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

logger = logging.getLogger("feva.api")


def _error_response(
    code: str,
    message: str,
    details: Any = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
) -> JSONResponse:
    content: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        content["details"] = details
    return JSONResponse(status_code=status_code, content=content)


# ---------------------------------------------------------------------------
# HTTP exception handler
# ---------------------------------------------------------------------------

_HTTP_USER_MESSAGES: dict[int, str] = {
    400: "The request was invalid. Please check your input and try again.",
    401: "Authentication required. Please log in.",
    403: "You do not have permission to perform this action.",
    404: "The requested resource was not found.",
    405: "This action is not allowed.",
    409: "A conflict occurred. The resource may already exist.",
    422: "The request data failed validation.",
    429: "Too many requests. Please wait before trying again.",
    500: "An unexpected error occurred. Please try again later.",
    503: "The service is temporarily unavailable. Please try again later.",
}


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException with structured response.

    For 401 on HTML routes, delegate to auth_redirect handler.
    """
    # Delegate 401 on HTML routes to auth redirect handler
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        path = request.url.path
        if path.startswith("/admin") or path.startswith("/qa"):
            from fastapi.responses import RedirectResponse
            return RedirectResponse(
                url=f"/login?next={path}",
                status_code=status.HTTP_302_FOUND,
            )

    request_id = str(uuid.uuid4())[:8]
    user_message = _HTTP_USER_MESSAGES.get(exc.status_code, str(exc.detail))

    if exc.status_code >= 500:
        logger.error(
            "HTTP %s on %s %s [req=%s]: %s",
            exc.status_code,
            request.method,
            request.url.path,
            request_id,
            exc.detail,
        )

    # Expose the original detail for 4xx (useful for API clients), but use
    # a generic message for 5xx to avoid leaking internals.
    detail = exc.detail if exc.status_code < 500 else None

    return _error_response(
        code=f"HTTP_{exc.status_code}",
        message=user_message,
        details=detail,
        status_code=exc.status_code,
    )


# ---------------------------------------------------------------------------
# Validation error handler
# ---------------------------------------------------------------------------


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic / FastAPI validation errors with structured response."""
    errors = [
        {
            "field": ".".join(str(loc) for loc in err["loc"]),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        errors,
    )
    return _error_response(
        code="VALIDATION_ERROR",
        message="The request data failed validation.",
        details=errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


# ---------------------------------------------------------------------------
# Generic unhandled exception handler
# ---------------------------------------------------------------------------


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions — log with stack trace, return 500."""
    request_id = str(uuid.uuid4())[:8]
    logger.error(
        "Unhandled exception on %s %s [req=%s]:\n%s",
        request.method,
        request.url.path,
        request_id,
        traceback.format_exc(),
    )
    return _error_response(
        code="INTERNAL_ERROR",
        message="An unexpected error occurred. Please try again later.",
        details={"request_id": request_id},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

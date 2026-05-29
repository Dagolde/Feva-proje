"""Tests for role-based authorization middleware.

Task 1.3: Create role-based authorization middleware
Tests that require_role() dependency correctly enforces role-based access control.
"""

import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock

from app.core.deps import require_role
from app.models.user import User
from app.models.role import Role


# ── Test Setup ────────────────────────────────────────────────────────────────


def _make_user(username: str = "testuser", role_name: str = "admin") -> User:
    """Create a mock User with specified role."""
    user = MagicMock(spec=User)
    user.id = "00000000-0000-0000-0000-000000000001"
    user.username = username
    user.email = f"{username}@example.com"
    
    role = MagicMock(spec=Role)
    role.id = 1
    role.name = role_name
    user.role = role
    
    return user


def _create_test_app_with_endpoint(allowed_roles: tuple[str, ...], mock_user: User = None) -> FastAPI:
    """Create a test FastAPI app with a protected endpoint."""
    app = FastAPI()
    
    # Override get_current_user dependency if mock_user is provided
    if mock_user:
        async def mock_get_current_user():
            return mock_user
        
        from app.core.deps import get_current_user
        app.dependency_overrides[get_current_user] = mock_get_current_user
    
    @app.get("/protected")
    async def protected_endpoint(
        current_user: User = Depends(require_role(*allowed_roles))
    ):
        return {"message": "success", "user": current_user.username}
    
    return app


# ── Test 1: Admin role can access admin-only endpoint ────────────────────────


@pytest.mark.asyncio
async def test_admin_role_can_access_admin_endpoint():
    """Admin user should be able to access admin-only endpoints."""
    admin_user = _make_user(username="admin", role_name="admin")
    app = _create_test_app_with_endpoint(("admin",), mock_user=admin_user)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/protected")
    
    assert response.status_code == 200
    assert response.json()["message"] == "success"
    assert response.json()["user"] == "admin"


# ── Test 2: Non-admin role cannot access admin-only endpoint ─────────────────


@pytest.mark.asyncio
async def test_non_admin_role_cannot_access_admin_endpoint():
    """Non-admin user should receive 403 Forbidden for admin-only endpoints."""
    qa_user = _make_user(username="qa_officer", role_name="qa_officer")
    app = _create_test_app_with_endpoint(("admin",), mock_user=qa_user)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/protected")
    
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]


# ── Test 3: Multiple allowed roles work correctly ────────────────────────────


@pytest.mark.asyncio
async def test_multiple_allowed_roles_work():
    """Endpoint with multiple allowed roles should accept any of them."""
    qa_user = _make_user(username="qa_officer", role_name="qa_officer")
    app = _create_test_app_with_endpoint(("admin", "qa_officer"), mock_user=qa_user)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/protected")
    
    assert response.status_code == 200
    assert response.json()["message"] == "success"


# ── Test 4: Enumerator cannot access admin or QA endpoints ───────────────────


@pytest.mark.asyncio
async def test_enumerator_cannot_access_admin_or_qa_endpoints():
    """Enumerator should receive 403 for admin/QA endpoints."""
    enumerator = _make_user(username="enumerator", role_name="enumerator")
    
    # Test admin-only endpoint
    app = _create_test_app_with_endpoint(("admin",), mock_user=enumerator)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/protected")
    
    assert response.status_code == 403
    
    # Test QA endpoint (admin or qa_officer)
    app = _create_test_app_with_endpoint(("admin", "qa_officer"), mock_user=enumerator)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/protected")
    
    assert response.status_code == 403


# ── Test 5: Supervisor cannot access admin-only endpoints ────────────────────


@pytest.mark.asyncio
async def test_supervisor_cannot_access_admin_only_endpoints():
    """Supervisor should receive 403 for admin-only endpoints."""
    supervisor = _make_user(username="supervisor", role_name="supervisor")
    app = _create_test_app_with_endpoint(("admin",), mock_user=supervisor)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/protected")
    
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]


# ── Test 6: User with no role cannot access protected endpoints ──────────────


@pytest.mark.asyncio
async def test_user_with_no_role_cannot_access_protected_endpoints():
    """User with no role should receive 403 for all protected endpoints."""
    user = MagicMock(spec=User)
    user.id = "00000000-0000-0000-0000-000000000001"
    user.username = "norole"
    user.email = "norole@example.com"
    user.role = None  # No role assigned
    
    app = _create_test_app_with_endpoint(("admin",), mock_user=user)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/protected")
    
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]



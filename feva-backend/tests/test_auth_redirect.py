"""Tests for authentication redirect middleware.

Requirements: 1.2, 2.2
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_unauthenticated_admin_route_redirects_to_login():
    """Test that unauthenticated requests to /admin/ redirect to login page.
    
    Requirements: 1.2
    """
    response = client.get("/admin/", follow_redirects=False)
    
    # Should redirect to login page
    assert response.status_code == 302
    assert response.headers["location"].startswith("/login")
    assert "next=/admin/" in response.headers["location"]


def test_unauthenticated_qa_route_redirects_to_login():
    """Test that unauthenticated requests to /qa/ redirect to login page.
    
    Requirements: 2.2
    """
    response = client.get("/qa/", follow_redirects=False)
    
    # Should redirect to login page
    assert response.status_code == 302
    assert response.headers["location"].startswith("/login")
    assert "next=/qa/" in response.headers["location"]


def test_unauthenticated_api_route_returns_401():
    """Test that unauthenticated requests to API routes return 401."""
    response = client.get("/api/v1/admin/users")
    
    # Should return 401 Unauthorized
    assert response.status_code == 401
    assert response.json()["details"] == "Could not validate credentials"


def test_login_page_accessible_without_auth():
    """Test that the login page is accessible without authentication."""
    response = client.get("/login")
    
    assert response.status_code == 200
    assert b"FEVA Login" in response.content


def test_health_endpoint_accessible_without_auth():
    """Test that the health endpoint is accessible without authentication."""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_endpoint_accessible_without_auth():
    """Test that the login API endpoint is accessible without authentication."""
    # This should fail with invalid credentials, not auth error
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "invalid", "password": "invalid"}
    )
    
    # Should return 401 for invalid credentials, not authentication error
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["details"]



@pytest.mark.asyncio
async def test_authenticated_admin_can_access_admin_dashboard(async_client, admin_user, admin_token):
    """Test that authenticated admin users can access the admin dashboard.
    
    Requirements: 1.3
    """
    # Set the access token cookie
    async_client.cookies.set("access_token", admin_token)
    
    response = await async_client.get("/admin/")
    
    assert response.status_code == 200
    assert b"Admin Dashboard" in response.content
    assert admin_user.username.encode() in response.content


@pytest.mark.asyncio
async def test_authenticated_qa_officer_can_access_qa_dashboard(async_client, qa_user, qa_token):
    """Test that authenticated QA officers can access the QA dashboard.
    
    Requirements: 2.3
    """
    # Set the access token cookie
    async_client.cookies.set("access_token", qa_token)
    
    response = await async_client.get("/qa/")
    
    assert response.status_code == 200
    assert b"QA Dashboard" in response.content
    assert qa_user.username.encode() in response.content


@pytest.mark.asyncio
async def test_qa_officer_cannot_access_admin_dashboard(async_client, qa_token):
    """Test that QA officers cannot access the admin dashboard.
    
    Requirements: 1.4
    """
    # Set the access token cookie
    async_client.cookies.set("access_token", qa_token)
    
    response = await async_client.get("/admin/", follow_redirects=False)
    
    # Should return 403 Forbidden
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_access_qa_dashboard(async_client, admin_token):
    """Test that admin users can access the QA dashboard.
    
    Requirements: 2.4
    """
    # Set the access token cookie
    async_client.cookies.set("access_token", admin_token)
    
    response = await async_client.get("/qa/")
    
    assert response.status_code == 200
    assert b"QA Dashboard" in response.content


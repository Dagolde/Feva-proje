"""Smoke test for QA statistics endpoint.

Task 12.2: Create statistics endpoint
Requirements: 19.5, 19.7
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_statistics_endpoint_exists(client: AsyncClient):
    """Test that statistics endpoint exists and requires authentication."""
    response = await client.get("/api/v1/qa/statistics")
    # Should return 401 (unauthorized) not 404 (not found)
    assert response.status_code == 401, "Endpoint should exist and require authentication"


@pytest.mark.asyncio
async def test_statistics_endpoint_with_qa_user(client: AsyncClient, qa_user):
    """Test that QA users can access the statistics endpoint."""
    from app.core.security import create_access_token
    
    token = create_access_token({"sub": str(qa_user.id), "role": "qa_officer"})
    
    response = await client.get(
        "/api/v1/qa/statistics",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "total_records" in data
    assert "pending_records" in data
    assert "approved_records" in data
    assert "rejected_records" in data
    assert "approval_rate_by_enumerator" in data
    assert "average_review_time_seconds" in data
    assert "daily_volumes" in data
    
    # Verify types
    assert isinstance(data["total_records"], int)
    assert isinstance(data["pending_records"], int)
    assert isinstance(data["approved_records"], int)
    assert isinstance(data["rejected_records"], int)
    assert isinstance(data["approval_rate_by_enumerator"], dict)
    assert data["average_review_time_seconds"] is None or isinstance(data["average_review_time_seconds"], (int, float))
    assert isinstance(data["daily_volumes"], list)


@pytest.mark.asyncio
async def test_statistics_endpoint_with_admin_user(client: AsyncClient, admin_user):
    """Test that admin users can access the statistics endpoint."""
    from app.core.security import create_access_token
    
    token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
    
    response = await client.get(
        "/api/v1/qa/statistics",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total_records" in data

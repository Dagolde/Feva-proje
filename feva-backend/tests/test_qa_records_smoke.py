"""Smoke test for QA records endpoint.

Simple test to verify the endpoint is accessible and returns the correct structure.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_qa_records_endpoint_exists(async_client: AsyncClient, admin_token: str):
    """Test that the QA records endpoint exists and returns correct structure."""
    response = await async_client.get(
        "/api/v1/qa/records",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    # Should return 200 OK
    assert response.status_code == 200
    
    # Should have the correct response structure
    data = response.json()
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "items" in data
    assert isinstance(data["items"], list)
    
    # Default pagination values
    assert data["page"] == 1
    assert data["page_size"] == 50

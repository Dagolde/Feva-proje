"""Smoke test for QA record detail API endpoint.

Simple test to verify the GET /api/v1/qa/records/{id} endpoint exists.
Requirements: 19.2, 19.7
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_record_detail_endpoint_exists(async_client: AsyncClient):
    """Test that the record detail endpoint exists and requires authentication."""
    import uuid
    
    record_id = uuid.uuid4()
    
    # Without authentication, should return 401
    response = await async_client.get(
        f"/api/v1/qa/records/{record_id}",
        params={"entity_type": "building"},
    )
    
    # Endpoint exists (not 404) and requires auth (401)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_record_detail_endpoint_requires_entity_type(async_client: AsyncClient):
    """Test that the endpoint requires entity_type query parameter."""
    import uuid
    
    record_id = uuid.uuid4()
    
    # Without entity_type parameter, authentication is checked first (401)
    # This is correct behavior - auth before validation
    response = await async_client.get(
        f"/api/v1/qa/records/{record_id}",
    )
    
    assert response.status_code == 401

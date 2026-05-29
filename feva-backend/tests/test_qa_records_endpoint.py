"""Tests for QA records listing endpoint.

Tests the GET /api/v1/qa/records endpoint for listing and filtering records.
Requirements: 10.7, 19.1, 19.7
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_records_endpoint_requires_qa_or_admin(async_client: AsyncClient):
    """Test that records endpoint requires qa_officer or admin role."""
    # Test without authentication
    response = await async_client.get("/api/v1/qa/records")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_records_endpoint_accessible_by_qa_officer(async_client: AsyncClient, qa_token: str):
    """Test that QA officer can access records endpoint."""
    response = await async_client.get(
        "/api/v1/qa/records",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "items" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_records_endpoint_accessible_by_admin(async_client: AsyncClient, admin_token: str):
    """Test that admin can access records endpoint."""
    response = await async_client.get(
        "/api/v1/qa/records",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "items" in data


@pytest.mark.asyncio
async def test_records_pagination(async_client: AsyncClient, qa_token: str):
    """Test that records endpoint supports pagination."""
    response = await async_client.get(
        "/api/v1/qa/records?page=1&page_size=10",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["items"]) <= 10


@pytest.mark.asyncio
async def test_records_status_filter(async_client: AsyncClient, qa_token: str):
    """Test that records endpoint supports status filtering."""
    response = await async_client.get(
        "/api/v1/qa/records?status=pending",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    data = response.json()
    # All returned items should have pending status
    for item in data["items"]:
        assert item["status"] == "pending"


@pytest.mark.asyncio
async def test_records_lga_filter(async_client: AsyncClient, qa_token: str):
    """Test that records endpoint supports LGA filtering."""
    response = await async_client.get(
        "/api/v1/qa/records?lga=TestLGA",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    data = response.json()
    # All returned items should be from TestLGA
    for item in data["items"]:
        assert item["lga"] == "TestLGA"


@pytest.mark.asyncio
async def test_records_entity_type_filter(async_client: AsyncClient, qa_token: str):
    """Test that records endpoint supports entity_type filtering."""
    # Test building filter
    response = await async_client.get(
        "/api/v1/qa/records?entity_type=building",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    data = response.json()
    for item in data["items"]:
        assert item["entity_type"] == "building"
    
    # Test street filter
    response = await async_client.get(
        "/api/v1/qa/records?entity_type=street",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    data = response.json()
    for item in data["items"]:
        assert item["entity_type"] == "street"


@pytest.mark.asyncio
async def test_records_response_structure(async_client: AsyncClient, qa_token: str):
    """Test that record items have the correct structure."""
    response = await async_client.get(
        "/api/v1/qa/records",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    data = response.json()
    if data["items"]:
        item = data["items"][0]
        # Check required fields
        assert "id" in item
        assert "entity_type" in item
        assert "record_id" in item
        assert "lga" in item
        assert "enumerator_username" in item
        assert "enumerator_id" in item
        assert "submitted_at" in item
        assert "status" in item
        
        # Check entity_type is valid
        assert item["entity_type"] in ["building", "street"]


@pytest.mark.asyncio
async def test_records_multiple_filters(async_client: AsyncClient, qa_token: str):
    """Test that records endpoint supports multiple filters simultaneously."""
    response = await async_client.get(
        "/api/v1/qa/records?status=pending&entity_type=building&page_size=5",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["page_size"] == 5
    
    # All items should match the filters
    for item in data["items"]:
        assert item["status"] == "pending"
        assert item["entity_type"] == "building"


@pytest.mark.asyncio
async def test_records_date_range_filter(async_client: AsyncClient, qa_token: str):
    """Test that records endpoint supports date range filtering."""
    response = await async_client.get(
        "/api/v1/qa/records?start_date=2024-01-01T00:00:00&end_date=2024-12-31T23:59:59",
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert response.status_code == 200
    
    data = response.json()
    # Should return successfully with date filters
    assert "items" in data

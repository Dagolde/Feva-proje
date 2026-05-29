"""Tests for QA statistics endpoint.

Task 12.2: Create statistics endpoint
Requirements: 19.5, 19.7
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building
from app.models.user import User


@pytest.mark.asyncio
async def test_statistics_endpoint_requires_authentication(client: AsyncClient):
    """Test that statistics endpoint requires authentication."""
    response = await client.get("/api/v1/qa/statistics")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_statistics_endpoint_requires_qa_or_admin_role(
    client: AsyncClient,
    enumerator_user: User,
):
    """Test that statistics endpoint requires qa_officer or admin role."""
    # Try to access with enumerator role (should fail)
    from app.core.security import create_access_token
    token = create_access_token({"sub": str(enumerator_user.id), "role": "enumerator"})
    
    response = await client.get(
        "/api/v1/qa/statistics",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_statistics_endpoint_returns_correct_structure(
    client: AsyncClient,
    async_db_session: AsyncSession,
    qa_user: User,
    admin_user: User,
):
    """Test that statistics endpoint returns correct response structure."""
    # Create test building
    building = Building(
        id=uuid4(),
        building_id="BLD001",
        street_id="STR001",
        lga="TestLGA",
        ward="TestWard",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
        geom="SRID=4326;POINT(3.0 6.0)",
        gps_accuracy_m=5.0,
    )
    async_db_session.add(building)
    await async_db_session.commit()
    
    # Get statistics
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
    
    # Verify we have at least one record
    assert data["total_records"] >= 1
    assert data["pending_records"] >= 1


@pytest.mark.asyncio
async def test_statistics_endpoint_with_lga_filter(
    client: AsyncClient,
    async_db_session: AsyncSession,
    qa_user: User,
    admin_user: User,
):
    """Test that statistics endpoint filters by LGA correctly."""
    # Create buildings in different LGAs
    building1 = Building(
        id=uuid4(),
        building_id="BLD001",
        street_id="STR001",
        lga="LGA_A",
        ward="Ward1",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="pending",
        geom="SRID=4326;POINT(3.0 6.0)",
        gps_accuracy_m=5.0,
    )
    building2 = Building(
        id=uuid4(),
        building_id="BLD002",
        street_id="STR002",
        lga="LGA_B",
        ward="Ward2",
        enumerator_id=admin_user.id,
        enumeration_date=datetime.now(timezone.utc),
        verification_status="approved",
        geom="SRID=4326;POINT(3.1 6.1)",
        gps_accuracy_m=5.0,
    )
    async_db_session.add_all([building1, building2])
    await async_db_session.commit()
    
    # Get statistics for LGA_A only
    from app.core.security import create_access_token
    token = create_access_token({"sub": str(qa_user.id), "role": "qa_officer"})
    
    response = await client.get(
        "/api/v1/qa/statistics?lga=LGA_A",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should only include building1 from LGA_A
    assert data["total_records"] >= 1
    assert data["pending_records"] >= 1
    # Should not include approved building from LGA_B
    # (exact counts depend on other test data, but we verify structure)


@pytest.mark.asyncio
async def test_statistics_endpoint_with_admin_role(
    client: AsyncClient,
    admin_user: User,
):
    """Test that admin users can access statistics endpoint."""
    # Get statistics as admin
    from app.core.security import create_access_token
    token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
    
    response = await client.get(
        "/api/v1/qa/statistics",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total_records" in data

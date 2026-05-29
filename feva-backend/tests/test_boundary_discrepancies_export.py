"""Tests for GET /api/v1/export/boundary-discrepancies endpoint and certified export bundling.

Requirements: 21.5, 21.6
"""
from __future__ import annotations

import csv
import io
import zipfile
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.boundary_discrepancy import BoundaryDiscrepancy
from app.models.user import User
from app.services.export_service import (
    _bundle_into_zip,
    _generate_boundary_discrepancies_csv,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
async def sample_discrepancies(async_db_session: AsyncSession):
    """Insert two boundary_discrepancy rows for testing."""
    rows = [
        BoundaryDiscrepancy(
            postcode_polygon_id="PC-001",
            admin_polygon_id="LGA-LAGOS",
            admin_type="lga",
            overlap_area_m2=12345.6789,
            detected_at=datetime(2025, 1, 10, 12, 0, 0, tzinfo=timezone.utc),
        ),
        BoundaryDiscrepancy(
            postcode_polygon_id="PC-002",
            admin_polygon_id="WARD-IKEJA",
            admin_type="ward",
            overlap_area_m2=500.0,
            detected_at=datetime(2025, 1, 11, 8, 0, 0, tzinfo=timezone.utc),
        ),
    ]
    for row in rows:
        async_db_session.add(row)
    await async_db_session.commit()
    for row in rows:
        await async_db_session.refresh(row)
    yield rows
    # Cleanup
    for row in rows:
        await async_db_session.delete(row)
    await async_db_session.commit()


# ── Endpoint: JSON format ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_boundary_discrepancies_json_default(
    client: AsyncClient,
    admin_token: str,
    sample_discrepancies,
):
    """GET /api/v1/export/boundary-discrepancies returns JSON list by default."""
    response = await client.get(
        "/api/v1/export/boundary-discrepancies",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    ids = {row["postcode_polygon_id"] for row in data}
    assert "PC-001" in ids
    assert "PC-002" in ids

    # Verify required fields are present
    for row in data:
        assert "postcode_polygon_id" in row
        assert "admin_polygon_id" in row
        assert "admin_type" in row
        assert "overlap_area_m2" in row
        assert "detected_at" in row


@pytest.mark.asyncio
async def test_boundary_discrepancies_explicit_json(
    client: AsyncClient,
    admin_token: str,
    sample_discrepancies,
):
    """GET /api/v1/export/boundary-discrepancies?format=json returns JSON list."""
    response = await client.get(
        "/api/v1/export/boundary-discrepancies?format=json",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ── Endpoint: CSV format ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_boundary_discrepancies_csv_format(
    client: AsyncClient,
    admin_token: str,
    sample_discrepancies,
):
    """GET /api/v1/export/boundary-discrepancies?format=csv returns CSV attachment."""
    response = await client.get(
        "/api/v1/export/boundary-discrepancies?format=csv",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "attachment" in response.headers.get("content-disposition", "")
    assert "boundary_discrepancies.csv" in response.headers.get("content-disposition", "")

    # Parse CSV and verify columns
    reader = csv.DictReader(io.StringIO(response.text))
    rows = list(reader)
    assert len(rows) >= 2

    expected_columns = {
        "postcode_polygon_id",
        "admin_polygon_id",
        "admin_type",
        "overlap_area_m2",
        "detected_at",
    }
    assert expected_columns == set(reader.fieldnames)

    ids = {row["postcode_polygon_id"] for row in rows}
    assert "PC-001" in ids
    assert "PC-002" in ids


@pytest.mark.asyncio
async def test_boundary_discrepancies_csv_values(
    client: AsyncClient,
    admin_token: str,
    sample_discrepancies,
):
    """CSV rows contain correct values for each discrepancy."""
    response = await client.get(
        "/api/v1/export/boundary-discrepancies?format=csv",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    reader = csv.DictReader(io.StringIO(response.text))
    rows = {row["postcode_polygon_id"]: row for row in reader}

    assert "PC-001" in rows
    assert rows["PC-001"]["admin_polygon_id"] == "LGA-LAGOS"
    assert rows["PC-001"]["admin_type"] == "lga"
    assert float(rows["PC-001"]["overlap_area_m2"]) == pytest.approx(12345.6789, rel=1e-4)

    assert "PC-002" in rows
    assert rows["PC-002"]["admin_type"] == "ward"


# ── Endpoint: Auth / RBAC ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_boundary_discrepancies_requires_admin(
    client: AsyncClient,
    enumerator_token: str,
):
    """Non-admin users receive 403."""
    response = await client.get(
        "/api/v1/export/boundary-discrepancies",
        headers={"Authorization": f"Bearer {enumerator_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_boundary_discrepancies_requires_auth(
    client: AsyncClient,
):
    """Unauthenticated requests receive 401."""
    response = await client.get("/api/v1/export/boundary-discrepancies")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_boundary_discrepancies_invalid_format(
    client: AsyncClient,
    admin_token: str,
):
    """Invalid format param returns 422."""
    response = await client.get(
        "/api/v1/export/boundary-discrepancies?format=xml",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422


# ── Service helpers ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_generate_boundary_discrepancies_csv_helper(
    async_db_session: AsyncSession,
    sample_discrepancies,
):
    """_generate_boundary_discrepancies_csv returns valid CSV bytes with correct columns."""
    csv_bytes = await _generate_boundary_discrepancies_csv(async_db_session)
    assert isinstance(csv_bytes, bytes)

    reader = csv.DictReader(io.StringIO(csv_bytes.decode("utf-8")))
    rows = list(reader)
    assert len(rows) >= 2

    expected_columns = {
        "postcode_polygon_id",
        "admin_polygon_id",
        "admin_type",
        "overlap_area_m2",
        "detected_at",
    }
    assert expected_columns == set(reader.fieldnames)


def test_bundle_into_zip():
    """_bundle_into_zip creates a valid ZIP containing all provided files."""
    files = {
        "data.geojson": b'{"type":"FeatureCollection","features":[]}',
        "boundary_discrepancies.csv": b"postcode_polygon_id,admin_polygon_id\nPC-001,LGA-A\n",
    }
    zip_bytes = _bundle_into_zip(files)

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = set(zf.namelist())
        assert "data.geojson" in names
        assert "boundary_discrepancies.csv" in names
        assert zf.read("boundary_discrepancies.csv") == files["boundary_discrepancies.csv"]


@pytest.mark.asyncio
async def test_generate_boundary_discrepancies_csv_empty(
    async_db_session: AsyncSession,
):
    """_generate_boundary_discrepancies_csv returns header-only CSV when no rows exist."""
    # Use a fresh session with no discrepancy rows (or rely on empty state)
    csv_bytes = await _generate_boundary_discrepancies_csv(async_db_session)
    reader = csv.DictReader(io.StringIO(csv_bytes.decode("utf-8")))
    # fieldnames should still be present even with zero data rows
    assert reader.fieldnames is not None
    assert "postcode_polygon_id" in reader.fieldnames

"""Export API endpoints.

Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 21.5, 21.6
"""
from __future__ import annotations

import asyncio
import csv
import io

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.boundary_discrepancy import BoundaryDiscrepancy
from app.models.user import User
from app.services.export_service import (
    run_geojson_export,
    run_shapefile_export,
    generate_coverage_report_csv,
    generate_dq_metrics_snapshot_csv,
)

# In-memory job tracking for backward compatibility
_jobs: dict[str, dict] = {}

def create_export_job(format: str, user_id) -> str:
    """Create an export job (backward compatibility)."""
    import uuid
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "pending", "format": format, "user_id": str(user_id)}
    return job_id

def get_job_status(job_id: str) -> dict | None:
    """Get job status (backward compatibility)."""
    return _jobs.get(job_id)

router = APIRouter()


@router.post("/geojson")
async def start_geojson_export(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("supervisor", "admin")),
):
    """Create an async GeoJSON export job. Returns job_id for polling."""
    job_id = create_export_job("geojson", current_user.id)
    background_tasks.add_task(run_geojson_export, db, job_id, current_user)
    return {"job_id": job_id, "status": "pending"}


@router.post("/shapefile")
async def start_shapefile_export(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("supervisor", "admin")),
):
    """Create an async Shapefile export job. Returns job_id for polling."""
    job_id = create_export_job("shapefile", current_user.id)
    background_tasks.add_task(run_shapefile_export, db, job_id, current_user)
    return {"job_id": job_id, "status": "pending"}


@router.get("/jobs/{job_id}")
async def get_export_job(
    job_id: str,
    current_user: User = Depends(require_role("supervisor", "admin")),
):
    """Poll export job status. Returns download_url when complete."""
    job = get_job_status(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Export job not found")
    return job


@router.get("/monthly/{year}/{month}")
async def get_monthly_export(
    year: int,
    month: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("supervisor", "admin")),
):
    """Serve or generate the monthly GeoJSON export package."""
    job_id = create_export_job("geojson_monthly", current_user.id)
    background_tasks.add_task(
        run_geojson_export, db, job_id, current_user, year, month
    )
    return {"job_id": job_id, "year": year, "month": month, "status": "pending"}


@router.get("/boundary-discrepancies")
async def get_boundary_discrepancies(
    format: str = Query(default="json", pattern="^(csv|json)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Return all current boundary_discrepancies rows.

    Supports ?format=csv|json (default: json).
    Requires Admin role.

    Requirements: 21.5
    """
    result = await db.execute(
        select(BoundaryDiscrepancy).order_by(BoundaryDiscrepancy.detected_at.desc())
    )
    rows = result.scalars().all()

    if format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "postcode_polygon_id",
                "admin_polygon_id",
                "admin_type",
                "overlap_area_m2",
                "detected_at",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "postcode_polygon_id": row.postcode_polygon_id,
                    "admin_polygon_id": row.admin_polygon_id,
                    "admin_type": row.admin_type,
                    "overlap_area_m2": float(row.overlap_area_m2),
                    "detected_at": row.detected_at.isoformat() if row.detected_at else "",
                }
            )
        csv_bytes = output.getvalue().encode("utf-8")
        return StreamingResponse(
            iter([csv_bytes]),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=boundary_discrepancies.csv"
            },
        )

    # JSON format
    return [
        {
            "postcode_polygon_id": row.postcode_polygon_id,
            "admin_polygon_id": row.admin_polygon_id,
            "admin_type": row.admin_type,
            "overlap_area_m2": float(row.overlap_area_m2),
            "detected_at": row.detected_at.isoformat() if row.detected_at else None,
        }
        for row in rows
    ]


@router.get("/monthly/{year}/{month}/coverage-report")
async def get_monthly_coverage_report(
    year: int,
    month: int,
    format: str = Query(default="json", pattern="^(csv|json)$"),
    lga: str | None = Query(default=None, description="Filter by LGA"),
    verification_status: str | None = Query(default=None, description="Filter by verification status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("supervisor", "admin")),
):
    """Return coverage report (street/building counts per LGA and enumerator) for a given month.

    Supports ?format=csv|json (default: json).
    Optional filters: ?lga=, ?verification_status=

    Requirements: 22.4, 22.5
    """
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="month must be between 1 and 12")

    csv_bytes = await generate_coverage_report_csv(
        db, year, month, lga=lga, verification_status=verification_status
    )

    if format == "csv":
        return StreamingResponse(
            iter([csv_bytes]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=coverage_report_{year}_{month:02d}.csv"
            },
        )

    # Parse CSV back to JSON for the json response
    import csv as _csv
    reader = _csv.DictReader(io.StringIO(csv_bytes.decode("utf-8")))
    rows = list(reader)
    return {
        "year": year,
        "month": month,
        "filters": {"lga": lga, "verification_status": verification_status},
        "rows": rows,
    }


@router.get("/monthly/{year}/{month}/dq-metrics")
async def get_monthly_dq_metrics(
    year: int,
    month: int,
    format: str = Query(default="json", pattern="^(csv|json)$"),
    lga: str | None = Query(default=None, description="Filter by LGA"),
    verification_status: str | None = Query(default=None, description="Filter by verification status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("supervisor", "admin")),
):
    """Return DQ metrics snapshot for a given month.

    Metrics: median GPS accuracy, boundary containment %, mandatory field completion %,
    duplicate flag %, verification approval %.

    Supports ?format=csv|json (default: json).
    Optional filters: ?lga=, ?verification_status=

    Requirements: 22.4, 22.5
    """
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="month must be between 1 and 12")

    csv_bytes = await generate_dq_metrics_snapshot_csv(
        db, year, month, lga=lga, verification_status=verification_status
    )

    if format == "csv":
        return StreamingResponse(
            iter([csv_bytes]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=dq_metrics_{year}_{month:02d}.csv"
            },
        )

    # Parse CSV back to JSON
    import csv as _csv
    reader = _csv.DictReader(io.StringIO(csv_bytes.decode("utf-8")))
    metrics = {row["metric"]: float(row["value"]) for row in reader}
    return {
        "year": year,
        "month": month,
        "filters": {"lga": lga, "verification_status": verification_status},
        "metrics": metrics,
    }

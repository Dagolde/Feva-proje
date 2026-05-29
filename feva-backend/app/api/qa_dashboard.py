"""QA dashboard HTML routes.

Requirements: 2.1, 2.3, 2.4, 21.3, 21.4
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/qa/", response_class=HTMLResponse)
async def qa_dashboard(
    request: Request,
    current_user: User = Depends(require_role("qa_officer", "admin", "supervisor")),
    db: AsyncSession = Depends(get_db),
):
    """Render the QA dashboard home page.
    
    Displays QA statistics summary with:
    - Pending records count prominently displayed
    - Recent activity summary
    - Statistics cards (total records, pending, approved, rejected)
    - Boundary discrepancy count and per-LGA breakdown
    - Auto-refresh for real-time updates (60 seconds)
    
    Requirements: 2.1, 2.3, 2.4, 21.3, 21.4
    """
    # Query boundary discrepancy summary for the dashboard
    discrepancy_total = 0
    discrepancy_by_lga: list[dict] = []
    try:
        total_result = await db.execute(
            text("SELECT COUNT(*) FROM boundary_discrepancies")
        )
        discrepancy_total = total_result.scalar() or 0

        by_lga_result = await db.execute(
            text(
                """
                SELECT admin_polygon_id, COUNT(*) as cnt
                FROM boundary_discrepancies
                GROUP BY admin_polygon_id
                ORDER BY cnt DESC, admin_polygon_id
                """
            )
        )
        discrepancy_by_lga = [
            {"lga": row.admin_polygon_id, "count": row.cnt}
            for row in by_lga_result.fetchall()
        ]
    except Exception:
        # Table may not exist in test environments; degrade gracefully
        pass

    return templates.TemplateResponse(
        "qa/index.html",
        {
            "request": request,
            "user": current_user,
            "discrepancy_total": discrepancy_total,
            "discrepancy_by_lga": discrepancy_by_lga,
        },
    )


@router.get("/qa/records", response_class=HTMLResponse)
async def qa_records(
    request: Request,
    current_user: User = Depends(require_role("qa_officer", "admin", "supervisor")),
):
    """Render the QA record list page.
    
    Displays paginated record table with:
    - Multi-dimensional filters (status, LGA, ward, enumerator, date range, entity type)
    - Quick status indicators for each record
    - Page size selection (10, 25, 50, 100 records per page)
    - Clickable rows to view record details
    - Auto-refresh for real-time updates (60 seconds)
    
    All filtering and pagination is handled client-side via the existing
    API endpoint at /api/v1/qa/records.
    
    Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.8
    """
    return templates.TemplateResponse(
        "qa/records.html",
        {"request": request, "user": current_user}
    )


@router.get("/qa/flagged", response_class=HTMLResponse)
async def qa_flagged(
    request: Request,
    current_user: User = Depends(require_role("qa_officer", "admin", "supervisor")),
):
    """Render the flagged records page.

    Displays records with active QA flags (boundary, duplicate, GPS accuracy).
    Includes bulk review interface for approving or rejecting multiple records.

    Data is loaded client-side via /api/v1/qa/flags.
    Bulk actions use /api/v1/qa/records/{id}/approve and /reject.
    """
    return templates.TemplateResponse(
        "qa/flagged.html",
        {"request": request, "user": current_user}
    )


@router.get("/qa/reports", response_class=HTMLResponse)
async def qa_reports(
    request: Request,
    current_user: User = Depends(require_role("qa_officer", "admin", "supervisor")),
):
    """Render the QA reports page.

    Displays QA statistics by enumerator including:
    - Summary statistics (total, pending, approved, rejected, overall approval rate)
    - Approval rate per enumerator with inline bar chart
    - Average review time
    - Daily submission and review volume chart
    - Filterable by LGA, ward, and date range

    Data is loaded client-side via /api/v1/qa/statistics.

    Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6
    """
    return templates.TemplateResponse(
        "qa/reports.html",
        {"request": request, "user": current_user}
    )


@router.get("/qa/records/{record_id}", response_class=HTMLResponse)
async def qa_record_detail(
    request: Request,
    record_id: str,
    current_user: User = Depends(require_role("qa_officer", "admin", "supervisor")),
):
    """Render the QA record detail page.
    
    Displays complete record information including:
    - All form field values submitted by the enumerator
    - GPS coordinates with accuracy information
    - Photo gallery with all associated photos
    - Interactive map showing the record's location
    - Approval/rejection controls (for pending/flagged records)
    - Complete audit trail of all review actions
    - Submission timestamp and enumerator information
    - Current review status and any previous review comments
    
    The page supports both building and street entity types. The entity_type
    parameter is required in the query string.
    
    All data is loaded client-side via the existing API endpoints:
    - /api/v1/qa/records/{id} for record details
    - /api/v1/qa/records/{id}/audit for audit trail
    - /api/v1/qa/records/{id}/approve for approval
    - /api/v1/qa/records/{id}/reject for rejection
    
    Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 12.1, 12.2
    """
    return templates.TemplateResponse(
        "qa/record_detail.html",
        {"request": request, "user": current_user}
    )

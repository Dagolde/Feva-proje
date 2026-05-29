"""QA Dashboard — server-rendered Jinja2 UI.

Requirements: 13.1, 13.2, 13.3, 13.4, 13.5
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.qa import (
    get_flagged_records,
    get_qa_metrics,
)
from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard/", response_class=HTMLResponse)
async def qa_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    # TEMP: Auth disabled for local dev - RE-ENABLE BEFORE PRODUCTION
    # current_user: User = Depends(require_role("supervisor", "admin")),
):
    """Render the QA dashboard page."""
    # Mock current_user for local dev
    from app.models.user import User
    current_user = User(id="87777cc0-a9b4-40f6-8ebc-66b648490037e", username="admin", role_id=1)
    
    metrics = await get_qa_metrics(db=db, current_user=current_user)
    flags = await get_flagged_records(db=db, current_user=current_user)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "metrics": metrics,
            "flags": flags,
        },
    )

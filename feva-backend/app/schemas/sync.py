"""Pydantic schemas for the sync upload endpoint."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class RecordPayload(BaseModel):
    """A single street or building record submitted from the device."""
    entity_type: str = Field(..., description="'street' or 'building'")
    local_id: int = Field(..., description="Device SQLite row id")
    data: dict[str, Any] = Field(..., description="Full record fields as JSON")


class RecordResult(BaseModel):
    """Per-record result returned to the device."""
    local_id: int
    entity_type: str
    status: str  # 'accepted' | 'rejected'
    server_id: str | None = None
    errors: list[str] = Field(default_factory=list)


class SyncUploadResponse(BaseModel):
    session_id: str
    results: list[RecordResult]
    accepted: int
    rejected: int

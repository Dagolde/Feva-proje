"""Smoke tests for QA audit trail retrieval.

Requirements: 14.1, 14.2, 14.3, 14.4
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.services.qa_service import get_audit_trail


@pytest.mark.asyncio
async def test_get_audit_trail_function_exists():
    """Test that get_audit_trail function exists and is callable."""
    assert callable(get_audit_trail)
    
    # Check function signature
    import inspect
    sig = inspect.signature(get_audit_trail)
    params = list(sig.parameters.keys())
    
    # Verify expected parameters
    assert "db" in params
    assert "record_id" in params
    assert "entity_type" in params


def test_audit_trail_endpoint_exists():
    """Test that the audit trail endpoint is registered in the QA API."""
    from app.api.v1.qa import router
    
    # Check that the endpoint exists
    routes = [route.path for route in router.routes]
    assert "/records/{record_id}/audit" in routes


def test_audit_entry_schema_exists():
    """Test that AuditEntry and AuditTrailResponse schemas exist."""
    from app.api.v1.qa import AuditEntry, AuditTrailResponse
    
    # Verify schemas are defined
    assert AuditEntry is not None
    assert AuditTrailResponse is not None
    
    # Check AuditEntry fields
    audit_entry_fields = AuditEntry.model_fields
    assert "timestamp" in audit_entry_fields
    assert "user" in audit_entry_fields
    assert "action" in audit_entry_fields
    assert "detail" in audit_entry_fields
    
    # Check AuditTrailResponse fields
    audit_trail_fields = AuditTrailResponse.model_fields
    assert "record_id" in audit_trail_fields
    assert "entity_type" in audit_trail_fields
    assert "entries" in audit_trail_fields


def test_get_audit_trail_imported_in_qa_api():
    """Test that get_audit_trail is imported in the QA API module."""
    from app.api.v1 import qa
    
    # Verify the function is imported
    assert hasattr(qa, "get_audit_trail")
    assert callable(qa.get_audit_trail)

"""Smoke test for QA record detail retrieval.

Simple test to verify the get_record_detail function exists and has correct signature.
Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7
"""
import inspect
from uuid import UUID

from app.services.qa_service import get_record_detail, RecordDetail


def test_get_record_detail_function_exists():
    """Test that get_record_detail function exists."""
    assert callable(get_record_detail)


def test_get_record_detail_signature():
    """Test that get_record_detail has the correct signature."""
    sig = inspect.signature(get_record_detail)
    params = list(sig.parameters.keys())
    
    # Should have 3 parameters: db, record_id, entity_type
    assert len(params) == 3
    assert "db" in params
    assert "record_id" in params
    assert "entity_type" in params


def test_record_detail_dataclass_exists():
    """Test that RecordDetail dataclass exists with required fields."""
    # Check that RecordDetail is a dataclass
    assert hasattr(RecordDetail, '__dataclass_fields__')
    
    # Check required fields
    fields = RecordDetail.__dataclass_fields__
    assert "id" in fields
    assert "entity_type" in fields
    assert "data" in fields
    assert "photos" in fields
    assert "geometry" in fields
    assert "status" in fields
    assert "enumerator" in fields
    assert "submitted_at" in fields
    assert "reviewed_by" in fields
    assert "reviewed_at" in fields
    assert "rejection_reason" in fields


def test_get_record_detail_is_async():
    """Test that get_record_detail is an async function."""
    assert inspect.iscoroutinefunction(get_record_detail)

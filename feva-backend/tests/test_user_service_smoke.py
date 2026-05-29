"""Smoke tests for UserService to verify implementation."""
import inspect

from app.services import user_service


def test_user_service_functions_exist():
    """Verify all required UserService functions exist."""
    assert hasattr(user_service, "create_user")
    assert hasattr(user_service, "update_user")
    assert hasattr(user_service, "reset_password")
    assert hasattr(user_service, "list_users")
    assert hasattr(user_service, "deactivate_user")


def test_create_user_signature():
    """Verify create_user has correct signature."""
    sig = inspect.signature(user_service.create_user)
    params = list(sig.parameters.keys())
    
    assert "db" in params
    assert "username" in params
    assert "email" in params
    assert "password" in params
    assert "role_id" in params
    assert "lga_assignment" in params
    assert "created_by" in params


def test_update_user_signature():
    """Verify update_user has correct signature."""
    sig = inspect.signature(user_service.update_user)
    params = list(sig.parameters.keys())
    
    assert "db" in params
    assert "user_id" in params
    assert "role_id" in params
    assert "lga_assignment" in params
    assert "locked" in params
    assert "updated_by" in params


def test_reset_password_signature():
    """Verify reset_password has correct signature."""
    sig = inspect.signature(user_service.reset_password)
    params = list(sig.parameters.keys())
    
    assert "db" in params
    assert "user_id" in params
    assert "new_password" in params
    assert "reset_by" in params


def test_list_users_signature():
    """Verify list_users has correct signature."""
    sig = inspect.signature(user_service.list_users)
    params = list(sig.parameters.keys())
    
    assert "db" in params
    assert "page" in params
    assert "page_size" in params


def test_deactivate_user_signature():
    """Verify deactivate_user has correct signature."""
    sig = inspect.signature(user_service.deactivate_user)
    params = list(sig.parameters.keys())
    
    assert "db" in params
    assert "user_id" in params
    assert "deactivated_by" in params

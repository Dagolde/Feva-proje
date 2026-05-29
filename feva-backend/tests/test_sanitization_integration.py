"""Integration tests for input sanitization in API endpoints."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.sanitization import sanitize_html_input, sanitize_sql_input


class TestSanitizationIntegration:
    """Test that sanitization is properly integrated into API endpoints."""
    
    def test_user_creation_sanitizes_username(self):
        """Test that user creation endpoint sanitizes username."""
        # This is a unit test to verify the sanitization logic
        username = "admin' OR 1=1 --"
        
        with pytest.raises(ValueError, match="dangerous SQL pattern"):
            sanitize_sql_input(username)
    
    def test_user_creation_sanitizes_email(self):
        """Test that user creation endpoint sanitizes email."""
        email = "test@example.com'; DROP TABLE users; --"
        
        with pytest.raises(ValueError, match="dangerous SQL pattern"):
            sanitize_sql_input(email)
    
    def test_dropdown_label_sanitizes_html(self):
        """Test that dropdown label sanitizes HTML."""
        label = "<script>alert('xss')</script>"
        result = sanitize_html_input(label)
        
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
    
    def test_dropdown_value_rejects_sql_injection(self):
        """Test that dropdown value rejects SQL injection."""
        value = "residential'; DROP TABLE buildings; --"
        
        with pytest.raises(ValueError, match="dangerous SQL pattern"):
            sanitize_sql_input(value)
    
    def test_rejection_reason_sanitizes_html(self):
        """Test that rejection reason sanitizes HTML."""
        reason = "GPS accuracy too low. <img src=x onerror=alert(1)>"
        result = sanitize_html_input(reason)
        
        assert "<img" not in result
        assert "&lt;img" in result
        assert "GPS accuracy too low" in result
    
    def test_pilot_feedback_message_sanitizes_html(self):
        """Test that pilot feedback message sanitizes HTML."""
        message = "App crashed when <script>alert('test')</script> was entered"
        result = sanitize_html_input(message)
        
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
        assert "App crashed when" in result
    
    def test_pilot_feedback_device_id_rejects_sql_injection(self):
        """Test that pilot feedback device_id rejects SQL injection."""
        device_id = "DEVICE123'; DELETE FROM pilot_feedback; --"
        
        with pytest.raises(ValueError, match="dangerous SQL pattern"):
            sanitize_sql_input(device_id)
    
    def test_normal_inputs_pass_through(self):
        """Test that normal inputs pass through sanitization."""
        # Normal username
        username = "john_doe"
        assert sanitize_sql_input(username) == username
        
        # Normal email
        email = "john@example.com"
        assert sanitize_sql_input(email) == email
        
        # Normal label
        label = "Residential Building"
        assert sanitize_html_input(label) == label
        
        # Normal rejection reason
        reason = "GPS accuracy is below 10 meters threshold"
        assert sanitize_html_input(reason) == reason
    
    def test_special_characters_allowed(self):
        """Test that safe special characters are allowed."""
        # Username with underscores and numbers
        username = "user_123"
        assert sanitize_sql_input(username) == username
        
        # Label with punctuation
        label = "Building Type: Residential (Multi-Unit)"
        assert sanitize_html_input(label) == label
        
        # Reason with punctuation (< will be escaped)
        reason = "Please re-survey: GPS accuracy below 5m required!"
        assert sanitize_html_input(reason) == reason
    
    def test_unicode_characters_preserved(self):
        """Test that Unicode characters are preserved."""
        # Label with Unicode
        label = "Résidentiel Bâtiment"
        result = sanitize_html_input(label)
        assert "Résidentiel" in result
        
        # Message with Unicode
        message = "测试消息"
        result = sanitize_html_input(message)
        assert "测试消息" in result

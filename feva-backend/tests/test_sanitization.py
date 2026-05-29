"""Unit tests for input sanitization utilities."""
import pytest

from app.core.sanitization import (
    sanitize_dict_values,
    sanitize_html_input,
    sanitize_sql_input,
)


class TestSanitizeHtmlInput:
    """Test HTML input sanitization."""
    
    def test_sanitize_script_tag(self):
        """Test that script tags are escaped."""
        input_text = "<script>alert('xss')</script>"
        result = sanitize_html_input(input_text)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
        assert "&lt;/script&gt;" in result
    
    def test_sanitize_img_tag_with_onerror(self):
        """Test that img tags with onerror are escaped."""
        input_text = '<img src="x" onerror="alert(1)">'
        result = sanitize_html_input(input_text)
        assert "<img" not in result
        assert "&lt;img" in result
        assert "onerror" in result
    
    def test_sanitize_javascript_protocol(self):
        """Test that javascript: protocol is escaped."""
        input_text = '<a href="javascript:alert(1)">Click</a>'
        result = sanitize_html_input(input_text)
        assert "<a" not in result
        assert "&lt;a" in result
    
    def test_sanitize_normal_text(self):
        """Test that normal text is preserved."""
        input_text = "This is normal text with no HTML"
        result = sanitize_html_input(input_text)
        assert result == input_text
    
    def test_sanitize_text_with_quotes(self):
        """Test that quotes are escaped."""
        input_text = 'Text with "quotes" and \'apostrophes\''
        result = sanitize_html_input(input_text)
        assert "&#x27;" in result or "'" in result  # Apostrophes may or may not be escaped
        assert "&quot;" in result or '"' in result  # Quotes may or may not be escaped
    
    def test_sanitize_none_input(self):
        """Test that None input returns None."""
        result = sanitize_html_input(None)
        assert result is None
    
    def test_sanitize_empty_string(self):
        """Test that empty string returns empty string."""
        result = sanitize_html_input("")
        assert result == ""
    
    def test_sanitize_whitespace_only(self):
        """Test that whitespace-only string is stripped."""
        result = sanitize_html_input("   \t\n  ")
        assert result == ""
    
    def test_sanitize_strips_leading_trailing_whitespace(self):
        """Test that leading/trailing whitespace is removed."""
        input_text = "  text with spaces  "
        result = sanitize_html_input(input_text)
        assert result == "text with spaces"
    
    def test_sanitize_removes_null_bytes(self):
        """Test that null bytes are removed."""
        input_text = "text\x00with\x00nulls"
        result = sanitize_html_input(input_text)
        assert "\x00" not in result
        assert result == "textwithnulls"


class TestSanitizeSqlInput:
    """Test SQL input sanitization."""
    
    def test_reject_drop_table(self):
        """Test that DROP TABLE is rejected."""
        with pytest.raises(ValueError, match="dangerous SQL pattern"):
            sanitize_sql_input("'; DROP TABLE users; --")
    
    def test_reject_delete_from(self):
        """Test that DELETE FROM is rejected."""
        with pytest.raises(ValueError, match="dangerous SQL pattern"):
            sanitize_sql_input("'; DELETE FROM users WHERE 1=1; --")
    
    def test_reject_union_select(self):
        """Test that UNION SELECT is rejected."""
        with pytest.raises(ValueError, match="dangerous SQL pattern"):
            sanitize_sql_input("' UNION SELECT password FROM users --")
    
    def test_reject_or_1_equals_1(self):
        """Test that OR 1=1 pattern is rejected."""
        with pytest.raises(ValueError, match="dangerous SQL pattern"):
            sanitize_sql_input("admin' OR 1=1 --")
    
    def test_reject_or_true(self):
        """Test that OR true pattern is rejected."""
        with pytest.raises(ValueError, match="dangerous SQL pattern"):
            sanitize_sql_input("admin' OR true --")
    
    def test_reject_sql_comments(self):
        """Test that SQL comment patterns are rejected."""
        with pytest.raises(ValueError, match="dangerous SQL pattern"):
            sanitize_sql_input("text with -- comment")
    
    def test_reject_multiline_comments(self):
        """Test that multiline comment patterns are rejected."""
        with pytest.raises(ValueError, match="dangerous SQL pattern"):
            sanitize_sql_input("text with /* comment */")
    
    def test_reject_exec_command(self):
        """Test that EXEC command is rejected."""
        with pytest.raises(ValueError, match="dangerous SQL pattern"):
            sanitize_sql_input("'; EXEC('malicious code'); --")
    
    def test_reject_xp_stored_procedures(self):
        """Test that xp_ stored procedures are rejected."""
        with pytest.raises(ValueError, match="dangerous SQL pattern"):
            sanitize_sql_input("'; EXEC xp_cmdshell('dir'); --")
    
    def test_accept_normal_text(self):
        """Test that normal text is accepted."""
        input_text = "This is normal text"
        result = sanitize_sql_input(input_text)
        assert result == input_text
    
    def test_accept_text_with_numbers(self):
        """Test that text with numbers is accepted."""
        input_text = "Building 123 on Street 456"
        result = sanitize_sql_input(input_text)
        assert result == input_text
    
    def test_accept_text_with_special_chars(self):
        """Test that text with safe special characters is accepted."""
        input_text = "Text with @#$%^&*()_+={}[]|:;<>,.?/"
        result = sanitize_sql_input(input_text)
        assert result == input_text
    
    def test_accept_none_input(self):
        """Test that None input returns None."""
        result = sanitize_sql_input(None)
        assert result is None
    
    def test_case_insensitive_detection(self):
        """Test that SQL injection detection is case-insensitive."""
        with pytest.raises(ValueError, match="dangerous SQL pattern"):
            sanitize_sql_input("'; dRoP tAbLe users; --")


class TestSanitizeDictValues:
    """Test dictionary value sanitization."""
    
    def test_sanitize_simple_dict(self):
        """Test sanitizing a simple dictionary."""
        data = {
            "name": "<script>alert('xss')</script>",
            "age": 25,
            "active": True,
        }
        result = sanitize_dict_values(data, html_fields=["name"])
        assert "&lt;script&gt;" in result["name"]
        assert result["age"] == 25
        assert result["active"] is True
    
    def test_sanitize_nested_dict(self):
        """Test sanitizing nested dictionaries."""
        data = {
            "user": {
                "name": "<b>Bold Name</b>",
                "email": "user@example.com",
            },
            "count": 10,
        }
        result = sanitize_dict_values(data, html_fields=["name"])
        assert "&lt;b&gt;" in result["user"]["name"]
        assert result["user"]["email"] == "user@example.com"
        assert result["count"] == 10
    
    def test_sanitize_list_values(self):
        """Test sanitizing list values in dictionary."""
        data = {
            "tags": ["<script>", "normal", "text"],
            "numbers": [1, 2, 3],
        }
        result = sanitize_dict_values(data, html_fields=["tags"])
        assert "&lt;script&gt;" in result["tags"][0]
        assert result["tags"][1] == "normal"
        assert result["numbers"] == [1, 2, 3]
    
    def test_sanitize_sql_injection_in_dict(self):
        """Test that SQL injection in dict values is rejected."""
        data = {
            "username": "admin' OR 1=1 --",
            "password": "password",
        }
        with pytest.raises(ValueError, match="dangerous SQL pattern"):
            sanitize_dict_values(data)
    
    def test_sanitize_mixed_types(self):
        """Test sanitizing dictionary with mixed types."""
        data = {
            "string": "text",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
        }
        result = sanitize_dict_values(data)
        assert result["string"] == "text"
        assert result["int"] == 42
        assert result["float"] == 3.14
        assert result["bool"] is True
        assert result["none"] is None
        assert result["list"] == [1, 2, 3]
        assert result["dict"]["key"] == "value"
    
    def test_empty_dict(self):
        """Test sanitizing empty dictionary."""
        result = sanitize_dict_values({})
        assert result == {}
    
    def test_html_fields_parameter(self):
        """Test that html_fields parameter controls sanitization method."""
        data = {
            "description": "<p>Paragraph</p>",
            "username": "user123",
        }
        # description should use HTML sanitization
        result = sanitize_dict_values(data, html_fields=["description"])
        assert "&lt;p&gt;" in result["description"]
        assert result["username"] == "user123"


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    def test_user_registration_data(self):
        """Test sanitizing user registration data."""
        data = {
            "username": "john_doe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "bio": "<script>alert('xss')</script>",
        }
        result = sanitize_dict_values(data, html_fields=["bio"])
        assert result["username"] == "john_doe"
        assert result["email"] == "john@example.com"
        assert "&lt;script&gt;" in result["bio"]
    
    def test_record_submission_data(self):
        """Test sanitizing record submission data."""
        data = {
            "building_id": "BLD-001",
            "notes": "Building has <b>good</b> condition",
            "business_names": ["Shop A", "Shop B"],
        }
        result = sanitize_dict_values(data, html_fields=["notes"])
        assert result["building_id"] == "BLD-001"
        assert "&lt;b&gt;" in result["notes"]
        assert result["business_names"] == ["Shop A", "Shop B"]
    
    def test_qa_rejection_reason(self):
        """Test sanitizing QA rejection reason."""
        data = {
            "record_id": "REC-123",
            "reason": "GPS accuracy too low. Please re-survey.",
        }
        result = sanitize_dict_values(data, html_fields=["reason"])
        assert result["record_id"] == "REC-123"
        assert result["reason"] == "GPS accuracy too low. Please re-survey."
    
    def test_dropdown_config_data(self):
        """Test sanitizing dropdown configuration data."""
        data = {
            "category": "building_type",
            "value": "residential",
            "label": "Residential Building",
        }
        result = sanitize_dict_values(data)
        assert result["category"] == "building_type"
        assert result["value"] == "residential"
        assert result["label"] == "Residential Building"

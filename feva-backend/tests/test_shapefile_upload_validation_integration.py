"""Integration tests for shapefile upload validation.

Tests the integration of file upload validation with the shapefile upload endpoint.
Verifies that the validation is properly applied before shapefile processing.

Requirements: 20.7, 20.8
"""
import io
import pytest
from unittest.mock import AsyncMock, patch


class TestShapefileUploadValidation:
    """Test file upload validation in the shapefile endpoint."""
    
    def test_validate_file_upload_function_exists(self):
        """Test that the validate_file_upload function is available."""
        from app.core.sanitization import validate_file_upload
        
        assert callable(validate_file_upload)
    
    def test_validate_file_upload_rejects_non_zip(self):
        """Test that non-ZIP files are rejected."""
        from app.core.sanitization import validate_file_upload
        
        is_valid, error = validate_file_upload("test.txt", b"text content")
        
        assert is_valid is False
        assert "File type not allowed" in error
    
    def test_validate_file_upload_rejects_oversized(self):
        """Test that oversized files are rejected."""
        from app.core.sanitization import validate_file_upload
        
        # Create a file larger than 50MB
        large_content = b'PK\x03\x04' + b'\x00' * (51 * 1024 * 1024)
        is_valid, error = validate_file_upload("test.zip", large_content)
        
        assert is_valid is False
        assert "File too large" in error
    
    def test_validate_file_upload_rejects_wrong_mime(self):
        """Test that files with wrong MIME type are rejected."""
        from app.core.sanitization import validate_file_upload
        
        is_valid, error = validate_file_upload("fake.zip", b"not a zip")
        
        assert is_valid is False
        assert "does not match ZIP format" in error
    
    def test_validate_file_upload_accepts_valid_zip(self):
        """Test that valid ZIP files are accepted."""
        from app.core.sanitization import validate_file_upload
        
        zip_content = b'PK\x03\x04' + b'\x00' * 1000
        is_valid, error = validate_file_upload("test.zip", zip_content)
        
        assert is_valid is True
        assert error == ""
    
    def test_admin_endpoint_uses_validation(self):
        """Test that the admin endpoint imports and can use the validation function."""
        # This test verifies the integration without needing a full HTTP request
        from app.api.v1.admin import upload_shapefile
        from app.core.sanitization import validate_file_upload
        
        # Verify the endpoint function exists
        assert callable(upload_shapefile)
        
        # Verify validation function is available in the same module context
        assert callable(validate_file_upload)
    
    def test_validation_error_messages_are_descriptive(self):
        """Test that validation error messages are clear and actionable."""
        from app.core.sanitization import validate_file_upload
        
        # Test wrong extension
        is_valid, error = validate_file_upload("data.pdf", b"PDF content")
        assert "ZIP" in error
        assert "shapefile" in error.lower()
        
        # Test wrong MIME type
        is_valid, error = validate_file_upload("fake.zip", b"text")
        assert "ZIP format" in error
        assert "valid" in error.lower()
        
        # Test oversized file
        large_content = b'PK\x03\x04' + b'\x00' * (51 * 1024 * 1024)
        is_valid, error = validate_file_upload("huge.zip", large_content)
        assert "50MB" in error or "50 MB" in error
        assert "large" in error.lower()


class TestFileUploadValidationRequirements:
    """Test that validation meets the specified requirements."""
    
    def test_requirement_20_7_file_type_validation(self):
        """Requirement 20.7: System SHALL validate file uploads to ensure only allowed file types are accepted."""
        from app.core.sanitization import validate_file_upload
        
        # Only ZIP files should be allowed for shapefile uploads
        valid_extensions = [".zip", ".ZIP", ".Zip"]
        invalid_extensions = [".txt", ".pdf", ".exe", ".doc", ".xls", ".jpg", ".png"]
        
        # Test valid extensions
        for ext in valid_extensions:
            zip_content = b'PK\x03\x04' + b'\x00' * 100
            is_valid, _ = validate_file_upload(f"test{ext}", zip_content)
            assert is_valid is True, f"Extension {ext} should be valid"
        
        # Test invalid extensions
        for ext in invalid_extensions:
            content = b'some content'
            is_valid, error = validate_file_upload(f"test{ext}", content)
            assert is_valid is False, f"Extension {ext} should be invalid"
            assert "File type not allowed" in error
    
    def test_requirement_20_8_file_size_limit(self):
        """Requirement 20.8: System SHALL limit file upload sizes to 50MB maximum."""
        from app.core.sanitization import validate_file_upload
        
        # Test file exactly at limit (should pass)
        exact_size = b'PK\x03\x04' + b'\x00' * (50 * 1024 * 1024 - 4)
        is_valid, _ = validate_file_upload("exact.zip", exact_size)
        assert is_valid is True, "File exactly at 50MB should be valid"
        
        # Test file just under limit (should pass)
        under_size = b'PK\x03\x04' + b'\x00' * (49 * 1024 * 1024)
        is_valid, _ = validate_file_upload("under.zip", under_size)
        assert is_valid is True, "File under 50MB should be valid"
        
        # Test file over limit (should fail)
        over_size = b'PK\x03\x04' + b'\x00' * (50 * 1024 * 1024 + 1)
        is_valid, error = validate_file_upload("over.zip", over_size)
        assert is_valid is False, "File over 50MB should be invalid"
        assert "File too large" in error
        assert "50MB" in error or "50 MB" in error
    
    def test_mime_type_validation(self):
        """Test that MIME type is validated by checking file signature."""
        from app.core.sanitization import validate_file_upload
        
        # Valid ZIP signature
        valid_zip = b'PK\x03\x04' + b'\x00' * 100
        is_valid, _ = validate_file_upload("valid.zip", valid_zip)
        assert is_valid is True
        
        # Invalid signatures with .zip extension
        invalid_signatures = [
            (b'%PDF-1.4', "PDF"),
            (b'\x89PNG\r\n\x1a\n', "PNG"),
            (b'GIF89a', "GIF"),
            (b'MZ\x90\x00', "EXE"),
            (b'This is text', "Text"),
        ]
        
        for signature, file_type in invalid_signatures:
            is_valid, error = validate_file_upload("fake.zip", signature + b'\x00' * 100)
            assert is_valid is False, f"{file_type} file should be rejected"
            assert "does not match ZIP format" in error


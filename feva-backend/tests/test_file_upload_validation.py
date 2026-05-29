"""Unit tests for file upload validation.

Tests the validate_file_upload function to ensure proper validation of:
- File extensions (only ZIP allowed)
- File size limits (50MB maximum)
- MIME type validation (ZIP file signature)

Requirements: 20.7, 20.8
"""
import pytest

from app.core.sanitization import validate_file_upload


class TestFileUploadValidation:
    """Test suite for file upload validation."""
    
    def test_valid_zip_file(self):
        """Test that a valid ZIP file passes validation."""
        # ZIP files start with "PK" signature (0x504B)
        zip_content = b'PK\x03\x04' + b'\x00' * 100
        
        is_valid, error_message = validate_file_upload("test.zip", zip_content)
        
        assert is_valid is True
        assert error_message == ""
    
    def test_valid_zip_file_uppercase_extension(self):
        """Test that ZIP files with uppercase extension are accepted."""
        zip_content = b'PK\x03\x04' + b'\x00' * 100
        
        is_valid, error_message = validate_file_upload("TEST.ZIP", zip_content)
        
        assert is_valid is True
        assert error_message == ""
    
    def test_invalid_extension_txt(self):
        """Test that non-ZIP file extensions are rejected."""
        content = b'Some text content'
        
        is_valid, error_message = validate_file_upload("data.txt", content)
        
        assert is_valid is False
        assert "File type not allowed" in error_message
        assert "ZIP" in error_message
    
    def test_invalid_extension_pdf(self):
        """Test that PDF files are rejected."""
        content = b'%PDF-1.4'
        
        is_valid, error_message = validate_file_upload("document.pdf", content)
        
        assert is_valid is False
        assert "File type not allowed" in error_message
    
    def test_invalid_extension_exe(self):
        """Test that executable files are rejected."""
        content = b'MZ\x90\x00'
        
        is_valid, error_message = validate_file_upload("malware.exe", content)
        
        assert is_valid is False
        assert "File type not allowed" in error_message
    
    def test_file_too_large(self):
        """Test that files exceeding 50MB are rejected."""
        # Create a file larger than 50MB
        large_content = b'PK\x03\x04' + b'\x00' * (51 * 1024 * 1024)
        
        is_valid, error_message = validate_file_upload("large.zip", large_content)
        
        assert is_valid is False
        assert "File too large" in error_message
        assert "50MB" in error_message
    
    def test_file_exactly_50mb(self):
        """Test that a file exactly 50MB is accepted."""
        # Create a file exactly 50MB
        exact_size_content = b'PK\x03\x04' + b'\x00' * (50 * 1024 * 1024 - 4)
        
        is_valid, error_message = validate_file_upload("exact.zip", exact_size_content)
        
        assert is_valid is True
        assert error_message == ""
    
    def test_file_just_under_50mb(self):
        """Test that a file just under 50MB is accepted."""
        # Create a file just under 50MB
        under_size_content = b'PK\x03\x04' + b'\x00' * (49 * 1024 * 1024)
        
        is_valid, error_message = validate_file_upload("under.zip", under_size_content)
        
        assert is_valid is True
        assert error_message == ""
    
    def test_empty_file(self):
        """Test that empty files are rejected."""
        empty_content = b''
        
        is_valid, error_message = validate_file_upload("empty.zip", empty_content)
        
        assert is_valid is False
        assert "empty or corrupted" in error_message.lower()
    
    def test_file_with_one_byte(self):
        """Test that files with only one byte are rejected."""
        tiny_content = b'P'
        
        is_valid, error_message = validate_file_upload("tiny.zip", tiny_content)
        
        assert is_valid is False
        assert "empty or corrupted" in error_message.lower()
    
    def test_wrong_mime_type_text_file(self):
        """Test that files with wrong MIME type are rejected."""
        # Text file content with .zip extension
        text_content = b'This is a text file, not a ZIP'
        
        is_valid, error_message = validate_file_upload("fake.zip", text_content)
        
        assert is_valid is False
        assert "does not match ZIP format" in error_message
    
    def test_wrong_mime_type_pdf(self):
        """Test that PDF files with .zip extension are rejected."""
        # PDF file signature with .zip extension
        pdf_content = b'%PDF-1.4\n'
        
        is_valid, error_message = validate_file_upload("fake.zip", pdf_content)
        
        assert is_valid is False
        assert "does not match ZIP format" in error_message
    
    def test_wrong_mime_type_image(self):
        """Test that image files with .zip extension are rejected."""
        # PNG file signature with .zip extension
        png_content = b'\x89PNG\r\n\x1a\n'
        
        is_valid, error_message = validate_file_upload("fake.zip", png_content)
        
        assert is_valid is False
        assert "does not match ZIP format" in error_message
    
    def test_filename_without_extension(self):
        """Test that files without extension are rejected."""
        zip_content = b'PK\x03\x04' + b'\x00' * 100
        
        is_valid, error_message = validate_file_upload("noextension", zip_content)
        
        assert is_valid is False
        assert "File type not allowed" in error_message
    
    def test_filename_with_multiple_extensions(self):
        """Test that files with multiple extensions are handled correctly."""
        zip_content = b'PK\x03\x04' + b'\x00' * 100
        
        # Should accept because the final extension is .zip
        is_valid, error_message = validate_file_upload("data.tar.zip", zip_content)
        
        assert is_valid is True
        assert error_message == ""
    
    def test_filename_with_path_traversal_attempt(self):
        """Test that filenames with path traversal are handled safely."""
        zip_content = b'PK\x03\x04' + b'\x00' * 100
        
        # Should still validate based on extension
        is_valid, error_message = validate_file_upload("../../etc/passwd.zip", zip_content)
        
        assert is_valid is True
        assert error_message == ""
    
    def test_real_zip_signature_variants(self):
        """Test various valid ZIP file signatures."""
        # Standard ZIP signature
        zip_sig1 = b'PK\x03\x04'
        is_valid, _ = validate_file_upload("test1.zip", zip_sig1 + b'\x00' * 100)
        assert is_valid is True
        
        # Empty ZIP archive signature
        zip_sig2 = b'PK\x05\x06'
        is_valid, _ = validate_file_upload("test2.zip", zip_sig2 + b'\x00' * 100)
        assert is_valid is True
        
        # Spanned ZIP signature
        zip_sig3 = b'PK\x07\x08'
        is_valid, _ = validate_file_upload("test3.zip", zip_sig3 + b'\x00' * 100)
        assert is_valid is True
    
    def test_case_insensitive_extension_check(self):
        """Test that extension checking is case-insensitive."""
        zip_content = b'PK\x03\x04' + b'\x00' * 100
        
        # Test various case combinations
        for filename in ["test.ZIP", "test.Zip", "test.zIp", "test.ZiP"]:
            is_valid, error_message = validate_file_upload(filename, zip_content)
            assert is_valid is True, f"Failed for filename: {filename}"
            assert error_message == ""


class TestFileUploadValidationEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_minimum_valid_zip(self):
        """Test the minimum valid ZIP file (just the signature)."""
        # Minimum ZIP is just the signature
        min_zip = b'PK\x03\x04'
        
        is_valid, error_message = validate_file_upload("min.zip", min_zip)
        
        assert is_valid is True
        assert error_message == ""
    
    def test_file_size_boundary_conditions(self):
        """Test file sizes around the 50MB boundary."""
        # Test sizes: 49MB, 50MB-1byte, 50MB, 50MB+1byte, 51MB
        test_cases = [
            (49 * 1024 * 1024, True, "49MB should pass"),
            (50 * 1024 * 1024 - 1, True, "50MB-1byte should pass"),
            (50 * 1024 * 1024, True, "50MB should pass"),
            (50 * 1024 * 1024 + 1, False, "50MB+1byte should fail"),
            (51 * 1024 * 1024, False, "51MB should fail"),
        ]
        
        for size, should_pass, description in test_cases:
            # Account for the 4-byte signature
            content = b'PK\x03\x04' + b'\x00' * (size - 4)
            is_valid, error_message = validate_file_upload("test.zip", content)
            
            if should_pass:
                assert is_valid is True, f"{description}: {error_message}"
            else:
                assert is_valid is False, f"{description}: should have failed"
                assert "File too large" in error_message
    
    def test_unicode_filename(self):
        """Test that Unicode filenames are handled correctly."""
        zip_content = b'PK\x03\x04' + b'\x00' * 100
        
        # Test with Unicode characters
        is_valid, error_message = validate_file_upload("测试文件.zip", zip_content)
        
        assert is_valid is True
        assert error_message == ""
    
    def test_special_characters_in_filename(self):
        """Test filenames with special characters."""
        zip_content = b'PK\x03\x04' + b'\x00' * 100
        
        # Test with special characters
        special_names = [
            "file name with spaces.zip",
            "file-with-dashes.zip",
            "file_with_underscores.zip",
            "file.with.dots.zip",
        ]
        
        for filename in special_names:
            is_valid, error_message = validate_file_upload(filename, zip_content)
            assert is_valid is True, f"Failed for filename: {filename}"
            assert error_message == ""

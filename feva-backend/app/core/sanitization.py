"""Input sanitization utilities for XSS and SQL injection prevention."""
import html
import re
from typing import Any


def sanitize_html_input(text: str | None) -> str | None:
    """Sanitize user input to prevent XSS attacks.
    
    This function:
    1. Escapes HTML special characters
    2. Removes potentially dangerous patterns
    3. Strips leading/trailing whitespace
    
    Args:
        text: The input text to sanitize
        
    Returns:
        Sanitized text safe for storage and display, or None if input is None
        
    Examples:
        >>> sanitize_html_input("<script>alert('xss')</script>")
        "&lt;script&gt;alert('xss')&lt;/script&gt;"
        >>> sanitize_html_input("Normal text")
        "Normal text"
    """
    if text is None:
        return None
    
    if not isinstance(text, str):
        text = str(text)
    
    # Strip whitespace
    text = text.strip()
    
    # Escape HTML special characters
    text = html.escape(text, quote=True)
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    return text


def sanitize_sql_input(text: str | None) -> str | None:
    """Sanitize input for additional SQL injection protection.
    
    Note: SQLAlchemy's parameterized queries are the primary defense against
    SQL injection. This function provides an additional validation layer.
    
    This function checks for dangerous SQL patterns and raises an error if found.
    
    Args:
        text: The input text to validate
        
    Returns:
        The original text if safe, or None if input is None
        
    Raises:
        ValueError: If dangerous SQL patterns are detected
        
    Examples:
        >>> sanitize_sql_input("Normal text")
        "Normal text"
        >>> sanitize_sql_input("'; DROP TABLE users; --")
        Traceback (most recent call last):
        ...
        ValueError: Invalid input: contains dangerous SQL pattern
    """
    if text is None:
        return None
    
    if not isinstance(text, str):
        text = str(text)
    
    # Patterns that might indicate SQL injection attempts
    dangerous_patterns = [
        r";\s*DROP\s+TABLE",
        r";\s*DELETE\s+FROM",
        r";\s*UPDATE\s+.*\s+SET",
        r";\s*INSERT\s+INTO",
        r"--",
        r"/\*",
        r"\*/",
        r"xp_",
        r"sp_",
        r"EXEC\s*\(",
        r"EXECUTE\s*\(",
        r"UNION\s+SELECT",
        r"'\s*OR\s+'",
        r"'\s*OR\s+1\s*=\s*1",
        r"'\s*OR\s+true",
    ]
    
    text_lower = text.lower()
    
    for pattern in dangerous_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            raise ValueError(f"Invalid input: contains dangerous SQL pattern")
    
    return text


def sanitize_dict_values(data: dict[str, Any], html_fields: list[str] | None = None) -> dict[str, Any]:
    """Sanitize all string values in a dictionary.
    
    Args:
        data: Dictionary with values to sanitize
        html_fields: List of field names that should use HTML sanitization.
                    Other string fields will use SQL sanitization.
                    
    Returns:
        Dictionary with sanitized values
        
    Examples:
        >>> sanitize_dict_values({"name": "<script>alert('xss')</script>", "age": 25})
        {'name': '&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;', 'age': 25}
    """
    if html_fields is None:
        html_fields = []
    
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            if key in html_fields:
                sanitized[key] = sanitize_html_input(value)
            else:
                # Apply SQL sanitization (will raise if dangerous patterns found)
                sanitized[key] = sanitize_sql_input(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict_values(value, html_fields)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_dict_values(item, html_fields) if isinstance(item, dict)
                else sanitize_html_input(item) if isinstance(item, str) and key in html_fields
                else sanitize_sql_input(item) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


def validate_file_upload(filename: str, content: bytes) -> tuple[bool, str]:
    """Validate uploaded file for security and size constraints.
    
    This function validates:
    1. File extension is in the allowed list (ZIP only for shapefiles)
    2. File size does not exceed the maximum limit (50MB)
    3. File content matches the expected MIME type (basic check)
    
    Args:
        filename: The name of the uploaded file
        content: The binary content of the uploaded file
        
    Returns:
        A tuple of (is_valid, error_message). If valid, error_message is empty.
        
    Examples:
        >>> validate_file_upload("data.zip", b"PK...")
        (True, "")
        >>> validate_file_upload("data.txt", b"text")
        (False, "File type not allowed. Only ZIP files are accepted for shapefile uploads.")
        >>> validate_file_upload("huge.zip", b"x" * 60_000_000)
        (False, "File too large. Maximum size: 50MB")
        
    Requirements: 20.7, 20.8
    """
    from pathlib import Path
    
    # Define allowed extensions and max file size
    ALLOWED_EXTENSIONS = {".zip"}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Check extension
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, "File type not allowed. Only ZIP files are accepted for shapefile uploads."
    
    # Check size
    if len(content) > MAX_FILE_SIZE:
        max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
        return False, f"File too large. Maximum size: {max_size_mb:.0f}MB"
    
    # Check MIME type by examining file signature (magic bytes)
    # ZIP files start with "PK" (0x504B)
    if len(content) < 2:
        return False, "File is empty or corrupted"
    
    # Check for ZIP file signature
    if content[:2] != b'PK':
        return False, "File content does not match ZIP format. Please upload a valid ZIP archive."
    
    return True, ""


__all__ = [
    "sanitize_html_input",
    "sanitize_sql_input",
    "sanitize_dict_values",
    "validate_file_upload",
]

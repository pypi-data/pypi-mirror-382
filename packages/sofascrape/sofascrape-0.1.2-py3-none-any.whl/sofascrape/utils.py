"""
Utility functions for the SofaScore scraper library
"""
import re
import json
from typing import Any, Dict, Optional


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename safe for the filesystem
    """
    # Remove any characters that are not alphanumeric or common safe characters
    sanitized = re.sub(r'[^\w\-_.()]', '_', filename)
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')
    # Limit length to prevent issues with filesystems
    return sanitized[:255] if len(sanitized) > 255 else sanitized


def safe_json_loads(json_str: str, default: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Safely parse a JSON string, returning a default value if parsing fails
    
    Args:
        json_str: The JSON string to parse
        default: Default value to return if parsing fails
        
    Returns:
        Parsed JSON data or the default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def format_data_for_output(data: Dict[str, Any], format_type: str = "json"):
    """
    Format data according to the specified format type
    
    Args:
        data: The data to format
        format_type: The format type ("json", "csv", etc.)
        
    Returns:
        Formatted data
    """
    if format_type.lower() == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    else:
        # For now, just return the raw data for other formats
        return data
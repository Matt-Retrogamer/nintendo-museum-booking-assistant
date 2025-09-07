"""Validation utilities for MCP server."""

import re
from datetime import datetime
from typing import List, Tuple
from urllib.parse import urlparse


def validate_date_format(date_str: str) -> Tuple[bool, str]:
    """
    Validate that a date string matches YYYY-MM-DD format.
    
    Args:
        date_str: The date string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(date_str, str):
        return False, "Date must be a string"
    
    # Check basic format with regex
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return False, f"Date '{date_str}' must be in YYYY-MM-DD format"
    
    # Try to parse as actual date
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, ""
    except ValueError:
        return False, f"Date '{date_str}' is not a valid date"


def validate_dates_list(dates: List[str]) -> Tuple[bool, str, List[str]]:
    """
    Validate a list of dates, deduplicate and sort them.
    
    Args:
        dates: List of date strings to validate
        
    Returns:
        Tuple of (is_valid, error_message, processed_dates)
        processed_dates will be deduplicated and sorted if validation passes
    """
    if not isinstance(dates, list):
        return False, "Dates must be provided as a list", []
    
    if not dates:
        return True, "", []
    
    # Validate each date
    valid_dates = []
    invalid_dates = []
    
    for date_str in dates:
        is_valid, error = validate_date_format(date_str)
        if is_valid:
            valid_dates.append(date_str)
        else:
            invalid_dates.append(f"{date_str}: {error}")
    
    if invalid_dates:
        return False, f"Invalid dates found: {'; '.join(invalid_dates)}", []
    
    # Deduplicate and sort
    unique_sorted_dates = sorted(list(set(valid_dates)))
    
    return True, "", unique_sorted_dates


def validate_ifttt_webhook_url(url: str) -> Tuple[bool, str]:
    """
    Validate IFTTT webhook URL format.
    
    Args:
        url: The webhook URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(url, str):
        return False, "URL must be a string"
    
    if not url.strip():
        return False, "URL cannot be empty"
    
    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Invalid URL format: {e}"
    
    # Check basic URL structure
    if not parsed.scheme or not parsed.netloc:
        return False, "URL must include scheme (https://) and domain"
    
    # Check if it's an IFTTT webhook URL
    if 'maker.ifttt.com' not in parsed.netloc:
        return False, "URL must be an IFTTT webhook URL (maker.ifttt.com)"
    
    # Check path structure
    if not parsed.path.startswith('/trigger/'):
        return False, "URL must be an IFTTT trigger webhook"
    
    if '/with/key/' not in parsed.path:
        return False, "URL must contain a webhook key (/with/key/YOUR_KEY)"
    
    return True, ""


def extract_ifttt_key(url: str) -> str:
    """
    Extract the IFTTT key from a webhook URL.
    
    Args:
        url: The IFTTT webhook URL
        
    Returns:
        The extracted key, or empty string if not found
    """
    try:
        parsed = urlparse(url)
        path_parts = parsed.path.split('/')
        key_index = path_parts.index('key') + 1
        if key_index < len(path_parts):
            return path_parts[key_index]
    except (ValueError, IndexError):
        pass
    return ""


def is_date_in_past(date_str: str) -> bool:
    """
    Check if a date is in the past.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        True if date is in the past, False otherwise
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        return date_obj < datetime.now().date()
    except ValueError:
        return False

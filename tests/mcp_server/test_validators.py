"""Tests for MCP server validators."""

import pytest
from mcp_server.validators import (
    validate_date_format,
    validate_dates_list,
    validate_ifttt_webhook_url,
    extract_ifttt_key,
    is_date_in_past
)


class TestValidateDateFormat:
    """Test date format validation."""
    
    def test_valid_dates(self):
        """Test valid date formats."""
        valid_dates = [
            "2025-01-01",
            "2025-12-31",
            "2024-02-29",  # leap year
            "2000-01-01"
        ]
        
        for date in valid_dates:
            is_valid, error = validate_date_format(date)
            assert is_valid, f"Date {date} should be valid, got error: {error}"
            assert error == ""
    
    def test_invalid_format(self):
        """Test invalid date formats."""
        invalid_formats = [
            "25-01-01",      # wrong year format
            "2025-1-01",     # wrong month format
            "2025-01-1",     # wrong day format
            "2025/01/01",    # wrong separator
            "01-01-2025",    # wrong order
            "2025-01",       # incomplete
            "not-a-date",    # not a date
            "",              # empty string
        ]
        
        for date in invalid_formats:
            is_valid, error = validate_date_format(date)
            assert not is_valid, f"Date {date} should be invalid"
            assert error != ""
    
    def test_invalid_dates(self):
        """Test dates with invalid values."""
        invalid_dates = [
            "2025-02-29",    # not a leap year
            "2025-13-01",    # invalid month
            "2025-01-32",    # invalid day
            "2025-00-01",    # invalid month
            "2025-01-00",    # invalid day
        ]
        
        for date in invalid_dates:
            is_valid, error = validate_date_format(date)
            assert not is_valid, f"Date {date} should be invalid"
            assert error != ""
    
    def test_non_string_input(self):
        """Test non-string inputs."""
        invalid_inputs = [123, None, [], {}]
        
        for inp in invalid_inputs:
            is_valid, error = validate_date_format(inp)
            assert not is_valid
            assert "must be a string" in error


class TestValidateDatesList:
    """Test dates list validation."""
    
    def test_valid_dates_list(self):
        """Test valid dates list."""
        dates = ["2025-01-01", "2025-01-02", "2025-01-03"]
        is_valid, error, processed = validate_dates_list(dates)
        
        assert is_valid
        assert error == ""
        assert processed == ["2025-01-01", "2025-01-02", "2025-01-03"]
    
    def test_empty_list(self):
        """Test empty list."""
        is_valid, error, processed = validate_dates_list([])
        
        assert is_valid
        assert error == ""
        assert processed == []
    
    def test_deduplication(self):
        """Test that duplicate dates are removed."""
        dates = ["2025-01-01", "2025-01-02", "2025-01-01", "2025-01-03"]
        is_valid, error, processed = validate_dates_list(dates)
        
        assert is_valid
        assert error == ""
        assert processed == ["2025-01-01", "2025-01-02", "2025-01-03"]
    
    def test_sorting(self):
        """Test that dates are sorted."""
        dates = ["2025-01-03", "2025-01-01", "2025-01-02"]
        is_valid, error, processed = validate_dates_list(dates)
        
        assert is_valid
        assert error == ""
        assert processed == ["2025-01-01", "2025-01-02", "2025-01-03"]
    
    def test_mixed_valid_invalid(self):
        """Test list with mix of valid and invalid dates."""
        dates = ["2025-01-01", "invalid-date", "2025-01-02"]
        is_valid, error, processed = validate_dates_list(dates)
        
        assert not is_valid
        assert "Invalid dates found" in error
        assert "invalid-date" in error
        assert processed == []
    
    def test_non_list_input(self):
        """Test non-list inputs."""
        invalid_inputs = ["2025-01-01", 123, None, {}]
        
        for inp in invalid_inputs:
            is_valid, error, processed = validate_dates_list(inp)
            assert not is_valid
            assert "must be provided as a list" in error
            assert processed == []


class TestValidateIftttWebhookUrl:
    """Test IFTTT webhook URL validation."""
    
    def test_valid_ifttt_url(self):
        """Test valid IFTTT webhook URLs."""
        valid_urls = [
            "https://maker.ifttt.com/trigger/event_name/with/key/abc123",
            "https://maker.ifttt.com/trigger/nintendo_museum_available/with/key/my_secret_key_123",
            "http://maker.ifttt.com/trigger/test/with/key/key123"  # http should work too
        ]
        
        for url in valid_urls:
            is_valid, error = validate_ifttt_webhook_url(url)
            assert is_valid, f"URL {url} should be valid, got error: {error}"
            assert error == ""
    
    def test_invalid_urls(self):
        """Test invalid URLs."""
        invalid_urls = [
            "",
            "not-a-url",
            "https://example.com",
            "https://maker.ifttt.com",  # missing path
            "https://maker.ifttt.com/trigger/event",  # incomplete path
            "https://wrong-domain.com/trigger/event/with/key/abc123",
            "maker.ifttt.com/trigger/event/with/key/abc123",  # missing scheme
        ]
        
        for url in invalid_urls:
            is_valid, error = validate_ifttt_webhook_url(url)
            assert not is_valid, f"URL {url} should be invalid"
            assert error != ""
    
    def test_non_string_input(self):
        """Test non-string inputs."""
        invalid_inputs = [123, None, [], {}]
        
        for inp in invalid_inputs:
            is_valid, error = validate_ifttt_webhook_url(inp)
            assert not is_valid
            assert "must be a string" in error


class TestExtractIftttKey:
    """Test IFTTT key extraction."""
    
    def test_extract_key(self):
        """Test key extraction from valid URLs."""
        test_cases = [
            ("https://maker.ifttt.com/trigger/event/with/key/abc123", "abc123"),
            ("https://maker.ifttt.com/trigger/nintendo_museum_available/with/key/my_secret_key", "my_secret_key"),
            ("http://maker.ifttt.com/trigger/test/with/key/123-456-789", "123-456-789"),
        ]
        
        for url, expected_key in test_cases:
            extracted_key = extract_ifttt_key(url)
            assert extracted_key == expected_key
    
    def test_extract_key_invalid_url(self):
        """Test key extraction from invalid URLs."""
        invalid_urls = [
            "https://example.com",
            "https://maker.ifttt.com/wrong/path",
            "not-a-url",
            "",
        ]
        
        for url in invalid_urls:
            extracted_key = extract_ifttt_key(url)
            assert extracted_key == ""


class TestIsDateInPast:
    """Test past date checking."""
    
    def test_past_date(self):
        """Test that past dates are detected."""
        assert is_date_in_past("2020-01-01")
        assert is_date_in_past("2024-01-01")
    
    def test_future_date(self):
        """Test that future dates are detected."""
        assert not is_date_in_past("2030-01-01")
        assert not is_date_in_past("2026-12-31")
    
    def test_invalid_date(self):
        """Test that invalid dates return False."""
        assert not is_date_in_past("invalid-date")
        assert not is_date_in_past("2025-13-01")
        assert not is_date_in_past("")

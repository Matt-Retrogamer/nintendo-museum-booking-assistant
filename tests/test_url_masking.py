"""Tests for URL masking functionality."""

from src.config import mask_sensitive_url


class TestUrlMasking:
    """Test URL masking for sensitive information."""

    def test_ifttt_webhook_url_masking(self):
        """Test that IFTTT webhook URLs have their keys masked."""
        original_url = (
            "https://maker.ifttt.com/trigger/event_name/with/key/supersecretkey123"
        )
        expected_url = "https://maker.ifttt.com/trigger/event_name/with/key/****"

        masked_url = mask_sensitive_url(original_url)

        assert masked_url == expected_url
        assert "supersecretkey123" not in masked_url

    def test_api_key_in_query_params_masking(self):
        """Test that API keys in query parameters are masked."""
        test_cases = [
            (
                "https://api.example.com/webhook?key=secret123",
                "https://api.example.com/webhook?key=****",
            ),
            (
                "https://example.com/api?token=abc123&other=value",
                "https://example.com/api?token=****&other=value",
            ),
            (
                "https://api.com/endpoint?api_key=xyz789&param=test",
                "https://api.com/endpoint?api_key=****&param=test",
            ),
            (
                "https://service.com/hook?secret=hidden&public=visible",
                "https://service.com/hook?secret=****&public=visible",
            ),
        ]

        for original_url, expected_url in test_cases:
            masked_url = mask_sensitive_url(original_url)
            assert masked_url == expected_url

    def test_normal_urls_unchanged(self):
        """Test that normal URLs without sensitive data are unchanged."""
        normal_urls = [
            "https://example.com/path",
            "https://nintendo.com/calendar",
            "https://github.com/user/repo",
            "https://api.example.com/public?param=value",
        ]

        for url in normal_urls:
            masked_url = mask_sensitive_url(url)
            assert masked_url == url

    def test_multiple_sensitive_params(self):
        """Test masking when multiple sensitive parameters exist."""
        original_url = "https://api.com/hook?key=secret1&token=secret2&public=value"
        masked_url = mask_sensitive_url(original_url)

        assert "secret1" not in masked_url
        assert "secret2" not in masked_url
        assert "public=value" in masked_url
        assert masked_url == "https://api.com/hook?key=****&token=****&public=value"

    def test_empty_and_edge_cases(self):
        """Test edge cases for URL masking."""
        edge_cases = [
            ("", ""),
            ("not-a-url", "not-a-url"),
            ("https://", "https://"),
            (
                "https://maker.ifttt.com/trigger/event/with/key/",
                "https://maker.ifttt.com/trigger/event/with/key/",
            ),
        ]

        for original_url, expected_url in edge_cases:
            masked_url = mask_sensitive_url(original_url)
            assert masked_url == expected_url

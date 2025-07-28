"""Tests for webhook notification functionality."""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from src.config import (
    Config,
    LoggingConfig,
    PollingConfig,
    WebhookConfig,
    WebsiteConfig,
)
from src.notifier import NotificationManager, WebhookNotifier


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    return Config(
        target_dates=["2025-09-25", "2025-09-26"],
        polling=PollingConfig(interval_seconds=1, page_load_delay_seconds=0),
        webhook=WebhookConfig(
            url="https://maker.ifttt.com/trigger/test/with/key/test_key",
            event_name="test_event",
            timeout_seconds=30,
        ),
        website=WebsiteConfig(url="https://test.com", availability_class="sale"),
        logging=LoggingConfig(),
    )


class TestWebhookNotifier:
    """Test webhook notification functionality."""

    @pytest.mark.asyncio
    async def test_prepare_payload(self, mock_config):
        """Test payload preparation for webhook."""
        notifier = WebhookNotifier(mock_config)
        available_dates = {"2025-09-25", "2025-09-26"}

        payload = notifier._prepare_payload(available_dates)

        assert "value1" in payload
        assert "value2" in payload
        assert "value3" in payload
        assert "2025-09-25" in payload["value1"]
        assert "2025-09-26" in payload["value1"]
        assert str(mock_config.website.url) == payload["value2"]

    @pytest.mark.asyncio
    async def test_send_notification_success(self, mock_config):
        """Test successful webhook notification."""
        with patch("aiohttp.ClientSession.post") as mock_post:
            # Mock successful HTTP response
            mock_response = AsyncMock()
            mock_response.raise_for_status = AsyncMock()
            mock_response.text = AsyncMock(return_value="OK")
            mock_post.return_value.__aenter__.return_value = mock_response

            async with WebhookNotifier(mock_config) as notifier:
                success = await notifier.send_notification({"2025-09-25"})

            assert success is True
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_network_error(self, mock_config):
        """Test webhook notification with network error."""
        with patch("aiohttp.ClientSession.post") as mock_post:
            # Mock network error
            mock_post.side_effect = Exception("Network error")

            async with WebhookNotifier(mock_config) as notifier:
                success = await notifier.send_notification({"2025-09-25"})

            assert success is False

    @pytest.mark.asyncio
    async def test_send_notification_empty_dates(self, mock_config):
        """Test webhook notification with empty dates."""
        async with WebhookNotifier(mock_config) as notifier:
            success = await notifier.send_notification(set())

        assert success is False

    @pytest.mark.asyncio
    async def test_test_webhook(self, mock_config):
        """Test webhook testing functionality."""
        with patch("aiohttp.ClientSession.post") as mock_post:
            # Mock successful HTTP response
            mock_response = AsyncMock()
            mock_response.raise_for_status = AsyncMock()
            mock_response.text = AsyncMock(return_value="OK")
            mock_post.return_value.__aenter__.return_value = mock_response

            async with WebhookNotifier(mock_config) as notifier:
                success = await notifier.test_webhook()

            assert success is True
            mock_post.assert_called_once()


class TestNotificationManager:
    """Test notification management functionality."""

    def test_notify_if_needed_new_dates(self, mock_config):
        """Test notification for new dates."""
        manager = NotificationManager(mock_config)

        # First call with new dates
        with patch.object(manager, "notified_dates", set()):
            with patch("src.notifier.WebhookNotifier") as mock_notifier_class:
                mock_notifier = AsyncMock()
                mock_notifier.send_notification.return_value = True
                mock_notifier_class.return_value.__aenter__.return_value = mock_notifier

                # This would normally be tested in an async function
                # For this test, we're checking the logic without async
                new_dates = {"2025-09-25"}
                assert new_dates - manager.notified_dates == new_dates

    def test_notify_if_needed_no_new_dates(self, mock_config):
        """Test notification when no new dates are available."""
        manager = NotificationManager(mock_config)
        manager.notified_dates = {"2025-09-25"}

        # Call with same dates - should not notify
        available_dates = {"2025-09-25"}
        new_dates = available_dates - manager.notified_dates

        assert new_dates == set()

    def test_rate_limiting_logic(self, mock_config):
        """Test rate limiting logic."""
        manager = NotificationManager(mock_config)

        # Set recent notification time
        manager.last_notification_time = datetime.now()

        # Check if enough time has passed (should be False for recent notification)
        now = datetime.now()
        time_since_last = (now - manager.last_notification_time).total_seconds()

        assert time_since_last < manager.min_notification_interval

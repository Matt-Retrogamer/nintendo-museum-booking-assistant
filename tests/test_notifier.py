"""Tests for webhook notification functionality."""

from datetime import datetime, timedelta
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

    @pytest.mark.asyncio
    async def test_notify_if_needed_new_dates(self, mock_config):
        """Test notification for newly available dates."""
        manager = NotificationManager(mock_config)

        with patch("src.notifier.WebhookNotifier") as mock_notifier_class:
            mock_notifier = AsyncMock()
            mock_notifier.send_notification.return_value = True
            mock_notifier_class.return_value.__aenter__.return_value = mock_notifier

            # First call with available dates
            available_dates = {"2025-09-25"}
            result = await manager.notify_if_needed(available_dates)

            assert result is True
            mock_notifier.send_notification.assert_called_once_with({"2025-09-25"})

    @pytest.mark.asyncio
    async def test_notify_if_needed_no_change(self, mock_config):
        """Test notification when availability doesn't change."""
        manager = NotificationManager(mock_config)
        
        with patch("src.notifier.WebhookNotifier") as mock_notifier_class:
            mock_notifier = AsyncMock()
            mock_notifier.send_notification.return_value = True
            mock_notifier_class.return_value.__aenter__.return_value = mock_notifier

            # First call - should notify
            available_dates = {"2025-09-25"}
            result1 = await manager.notify_if_needed(available_dates)
            assert result1 is True

            # Second call with same dates - should not notify
            result2 = await manager.notify_if_needed(available_dates)
            assert result2 is False

            # Should only be called once
            assert mock_notifier.send_notification.call_count == 1

    @pytest.mark.asyncio
    async def test_notify_if_needed_reappearing_dates(self, mock_config):
        """Test notification for dates that disappear and reappear."""
        manager = NotificationManager(mock_config)
        
        with patch("src.notifier.WebhookNotifier") as mock_notifier_class:
            mock_notifier = AsyncMock()
            mock_notifier.send_notification.return_value = True
            mock_notifier_class.return_value.__aenter__.return_value = mock_notifier

            # First: Date becomes available
            result1 = await manager.notify_if_needed({"2025-09-25"})
            assert result1 is True
            
            # Second: Date disappears
            result2 = await manager.notify_if_needed(set())
            assert result2 is False
            
            # Third: Date reappears (should notify again, but rate limited)
            result3 = await manager.notify_if_needed({"2025-09-25"})
            assert result3 is False  # Rate limited
            
            # Should be called only once due to rate limiting
            assert mock_notifier.send_notification.call_count == 1

    @pytest.mark.asyncio 
    async def test_notify_if_needed_reappearing_dates_after_grace_period(self, mock_config):
        """Test notification for dates that reappear after grace period."""
        manager = NotificationManager(mock_config)
        manager.min_notification_interval = 0  # No rate limiting for this test
        
        with patch("src.notifier.WebhookNotifier") as mock_notifier_class:
            mock_notifier = AsyncMock()
            mock_notifier.send_notification.return_value = True
            mock_notifier_class.return_value.__aenter__.return_value = mock_notifier

            # First: Date becomes available
            result1 = await manager.notify_if_needed({"2025-09-25"})
            assert result1 is True
            
            # Second: Date disappears
            result2 = await manager.notify_if_needed(set())
            assert result2 is False
            
            # Third: Date reappears (should notify again)
            result3 = await manager.notify_if_needed({"2025-09-25"})
            assert result3 is True
            
            # Should be called twice
            assert mock_notifier.send_notification.call_count == 2

    def test_rate_limiting_logic(self, mock_config):
        """Test rate limiting logic."""
        manager = NotificationManager(mock_config)

        # Set recent notification time
        manager.last_notification_time = datetime.now()

        # Check if enough time has passed (should be False for recent notification)
        now = datetime.now()
        time_since_last = (now - manager.last_notification_time).total_seconds()

        assert time_since_last < manager.min_notification_interval

    async def test_send_heartbeat_enabled(self, mock_config):
        """Test heartbeat sending when enabled."""
        # Configure heartbeat interval
        mock_config.webhook.heartbeat_interval_hours = 24
        
        manager = NotificationManager(mock_config)
        
        with patch('src.notifier.WebhookNotifier') as mock_notifier_class:
            mock_notifier = AsyncMock()
            mock_notifier.send_heartbeat.return_value = True
            mock_notifier_class.return_value.__aenter__.return_value = mock_notifier
            
            # First call should send heartbeat (no previous heartbeat)
            result = await manager.send_heartbeat_if_needed()
            assert result is True
            mock_notifier.send_heartbeat.assert_called_once()
            
            # Immediate second call should not send heartbeat (too soon)
            mock_notifier.reset_mock()
            result2 = await manager.send_heartbeat_if_needed()
            assert result2 is False
            mock_notifier.send_heartbeat.assert_not_called()

    async def test_send_heartbeat_disabled(self, mock_config):
        """Test heartbeat not sending when disabled."""
        # Disable heartbeat
        mock_config.webhook.heartbeat_interval_hours = 0
        
        manager = NotificationManager(mock_config)
        
        # Should not send heartbeat when disabled
        result = await manager.send_heartbeat_if_needed()
        assert result is False

    async def test_send_heartbeat_after_interval(self, mock_config):
        """Test heartbeat sending after interval has passed."""
        mock_config.webhook.heartbeat_interval_hours = 1  # 1 hour for easier testing
        
        manager = NotificationManager(mock_config)
        
        # Set last heartbeat time to 2 hours ago
        manager.last_heartbeat_time = datetime.now() - timedelta(hours=2)
        
        with patch('src.notifier.WebhookNotifier') as mock_notifier_class:
            mock_notifier = AsyncMock()
            mock_notifier.send_heartbeat.return_value = True
            mock_notifier_class.return_value.__aenter__.return_value = mock_notifier
            
            # Should send heartbeat since interval has passed
            result = await manager.send_heartbeat_if_needed()
            assert result is True
            mock_notifier.send_heartbeat.assert_called_once()

    async def test_send_heartbeat_failure(self, mock_config):
        """Test heartbeat failure handling."""
        mock_config.webhook.heartbeat_interval_hours = 24
        
        manager = NotificationManager(mock_config)
        
        with patch('src.notifier.WebhookNotifier') as mock_notifier_class:
            mock_notifier = AsyncMock()
            mock_notifier.send_heartbeat.return_value = False  # Simulate failure
            mock_notifier_class.return_value.__aenter__.return_value = mock_notifier
            
            # Should return False on failure
            result = await manager.send_heartbeat_if_needed()
            assert result is False
            
            # Should not update last heartbeat time on failure
            assert manager.last_heartbeat_time is None

    async def test_webhook_notifier_send_heartbeat(self, mock_config):
        """Test WebhookNotifier send_heartbeat method."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_post.return_value.__aenter__.return_value = mock_response
            
            async with WebhookNotifier(mock_config) as notifier:
                result = await notifier.send_heartbeat()
                assert result is True
                
                # Verify the correct payload was sent
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                
                # Check that the JSON payload contains heartbeat data
                json_data = call_args[1]['json']
                assert json_data['value1'] == "HEARTBEAT - Nintendo Museum Booking Assistant"
                assert json_data['value2'] == "Service is running normally"
                assert 'value3' in json_data  # Timestamp should be present

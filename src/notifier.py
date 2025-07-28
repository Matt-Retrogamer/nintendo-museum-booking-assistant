"""Webhook notification functionality for IFTTT integration."""

import logging
from datetime import datetime
from typing import Any

import aiohttp

from .config import Config, mask_sensitive_url

logger = logging.getLogger(__name__)


class WebhookNotifier:
    """Handles webhook notifications to IFTTT when availability is found."""

    def __init__(self, config: Config):
        """Initialize the notifier with configuration."""
        self.config = config
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "WebhookNotifier":
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.webhook.timeout_seconds)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    def _prepare_payload(self, available_dates: set[str]) -> dict[str, Any]:
        """
        Prepare the webhook payload for IFTTT.

        Args:
            available_dates: Set of available dates

        Returns:
            Dictionary containing the webhook payload
        """
        # Format dates for display
        formatted_dates = sorted(list(available_dates))
        dates_text = ", ".join(formatted_dates)

        # Create IFTTT-compatible payload
        # IFTTT webhooks support up to 3 values: value1, value2, value3
        payload = {
            "value1": dates_text,  # Available dates
            "value2": str(self.config.website.url),  # Link to booking site
            "value3": datetime.now().isoformat(),  # Timestamp
        }

        return payload

    async def send_notification(self, available_dates: set[str]) -> bool:
        """
        Send webhook notification about available dates.

        Args:
            available_dates: Set of available dates

        Returns:
            True if notification was sent successfully, False otherwise
        """
        if not self.session:
            raise RuntimeError("Notifier must be used as an async context manager")

        if not available_dates:
            logger.warning("No available dates to notify about")
            return False

        try:
            payload = self._prepare_payload(available_dates)
            webhook_url = self.config.webhook.url

            logger.info(f"Sending webhook notification for dates: {available_dates}")
            logger.debug(f"Webhook URL: {mask_sensitive_url(webhook_url)}")
            logger.debug(f"Payload: {payload}")

            async with self.session.post(webhook_url, json=payload) as response:
                response.raise_for_status()
                response_text = await response.text()

                logger.info(
                    f"Webhook notification sent successfully. Response: {response_text}"
                )
                return True

        except aiohttp.ClientError as e:
            logger.error(f"Network error while sending webhook: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending webhook: {e}")
            return False

    async def test_webhook(self) -> bool:
        """
        Test the webhook configuration by sending a test notification.

        Returns:
            True if test was successful, False otherwise
        """
        test_dates = {"2025-01-01"}  # Test date

        logger.info("Testing webhook configuration...")

        # Modify payload to indicate this is a test
        payload = self._prepare_payload(test_dates)
        payload["value1"] = "TEST - Nintendo Museum Booking Assistant"
        payload["value2"] = "This is a test notification"

        try:
            async with self.session.post(
                self.config.webhook.url, json=payload
            ) as response:
                response.raise_for_status()
                response_text = await response.text()

                logger.info(f"Webhook test successful. Response: {response_text}")
                return True

        except Exception as e:
            logger.error(f"Webhook test failed: {e}")
            return False


class NotificationManager:
    """Manages notification sending with rate limiting and deduplication."""

    def __init__(self, config: Config):
        """Initialize the notification manager."""
        self.config = config
        self.notified_dates: set[str] = set()
        self.last_notification_time: datetime | None = None
        self.min_notification_interval = 300  # 5 minutes between notifications

    async def notify_if_needed(self, available_dates: set[str]) -> bool:
        """
        Send notification only if new dates are available and enough time has passed.

        Args:
            available_dates: Set of available dates

        Returns:
            True if notification was sent, False otherwise
        """
        # Check if these are new dates
        new_dates = available_dates - self.notified_dates

        if not new_dates:
            logger.debug("No new dates to notify about")
            return False

        # Check if enough time has passed since last notification
        now = datetime.now()
        if (
            self.last_notification_time
            and (now - self.last_notification_time).total_seconds()
            < self.min_notification_interval
        ):
            logger.debug("Skipping notification due to rate limiting")
            return False

        # Send notification
        async with WebhookNotifier(self.config) as notifier:
            success = await notifier.send_notification(new_dates)

            if success:
                self.notified_dates.update(new_dates)
                self.last_notification_time = now
                logger.info(f"Notification sent for new dates: {new_dates}")

            return success

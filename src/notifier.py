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

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
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
            if not self.session:
                raise RuntimeError("Notifier must be used as an async context manager")

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

    async def send_heartbeat(self) -> bool:
        """
        Send a heartbeat notification to confirm the service is still running.

        Returns:
            True if heartbeat was sent successfully, False otherwise
        """
        if not self.session:
            raise RuntimeError("Notifier must be used as an async context manager")

        logger.info("Sending heartbeat notification...")

        # Create heartbeat-specific payload
        payload = {
            "value1": "HEARTBEAT - Nintendo Museum Booking Assistant",
            "value2": "Service is running normally",
            "value3": datetime.now().isoformat(),
        }

        try:
            async with self.session.post(
                self.config.webhook.url, json=payload
            ) as response:
                response.raise_for_status()
                response_text = await response.text()

                logger.info(
                    f"Heartbeat notification sent successfully. Response: {response_text}"
                )
                return True

        except Exception as e:
            logger.error(f"Heartbeat notification failed: {e}")
            return False


class NotificationManager:
    """Manages notification state and prevents duplicate/spam notifications."""

    def __init__(self, config: Config):
        self.config = config
        self.previous_available_dates: set[str] = set()
        self.last_notification_time: datetime | None = None
        self.last_heartbeat_time: datetime | None = None
        self.min_notification_interval = 300  # 5 minutes between notifications

    async def notify_if_needed(self, available_dates: set[str]) -> bool:
        """
        Send notification for newly available dates or dates that became available again.

        This method will notify when:
        1. A date becomes available for the first time
        2. A date becomes available again after being unavailable (with rate limiting)

        Args:
            available_dates: Set of currently available dates

        Returns:
            True if notification was sent, False otherwise
        """
        # Determine which dates are newly available (weren't available in previous check)
        newly_available_dates = available_dates - self.previous_available_dates

        if not newly_available_dates:
            logger.debug("No newly available dates to notify about")
            # Update state for next comparison
            self.previous_available_dates = available_dates.copy()
            return False

        # Check if enough time has passed since last notification (grace period)
        now = datetime.now()
        if (
            self.last_notification_time
            and (now - self.last_notification_time).total_seconds()
            < self.min_notification_interval
        ):
            logger.debug(
                f"Skipping notification due to rate limiting ({self.min_notification_interval}s grace period)"
            )
            # Update state for next comparison even if we don't notify
            self.previous_available_dates = available_dates.copy()
            return False

        # Send notification for newly available dates
        async with WebhookNotifier(self.config) as notifier:
            success = await notifier.send_notification(newly_available_dates)

            if success:
                self.last_notification_time = now
                logger.info(
                    f"Notification sent for newly available dates: {newly_available_dates}"
                )
            else:
                logger.warning(
                    f"Failed to send notification for dates: {newly_available_dates}"
                )

            # Update state regardless of notification success
            self.previous_available_dates = available_dates.copy()
            return success

    async def send_heartbeat_if_needed(self) -> bool:
        """
        Send heartbeat notification if enough time has passed since last heartbeat.

        Returns:
            True if heartbeat was sent, False otherwise
        """
        if not self.config.webhook.heartbeat_interval_hours:
            # Heartbeat disabled
            return False

        now = datetime.now()
        heartbeat_interval_seconds = self.config.webhook.heartbeat_interval_hours * 3600

        # Check if it's time for a heartbeat
        if (
            self.last_heartbeat_time is None
            or (now - self.last_heartbeat_time).total_seconds()
            >= heartbeat_interval_seconds
        ):
            async with WebhookNotifier(self.config) as notifier:
                success = await notifier.send_heartbeat()

                if success:
                    self.last_heartbeat_time = now
                    logger.info("Heartbeat notification sent")
                else:
                    logger.warning("Failed to send heartbeat notification")

                return success

        return False

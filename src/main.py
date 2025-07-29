"""Main application entry point for Nintendo Museum Booking Assistant."""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Any

from .config import load_config, mask_sensitive_url
from .notifier import NotificationManager
from .poller import AvailabilityPoller

logger = logging.getLogger(__name__)


class BookingAssistant:
    """Main application class for the Nintendo Museum Booking Assistant."""

    def __init__(self, config_path: Path = Path("config.yaml")):
        """Initialize the booking assistant."""
        self.config = load_config(config_path)
        self.setup_logging()

        self.poller: AvailabilityPoller | None = None
        self.notification_manager = NotificationManager(self.config)
        self._shutdown_event = asyncio.Event()

    def setup_logging(self) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.logging.level),
            format=self.config.logging.format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("nintendo_museum_assistant.log", encoding="utf-8"),
            ],
        )

        # Reduce noise from external libraries
        logging.getLogger("aiohttp").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)

    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum: int, frame: Any) -> None:
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self._shutdown_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def handle_availability_found(self, available_dates: set[str]) -> None:
        """
        Handle when availability is found for target dates.

        Args:
            available_dates: Set of dates with availability
        """
        # Log current availability status
        if available_dates:
            logger.info(f"Availability detected for dates: {available_dates}")
        else:
            logger.debug("No availability found for any target dates")

        # Send notification if needed (will handle state tracking internally)
        notification_sent = await self.notification_manager.notify_if_needed(
            available_dates
        )

        if notification_sent:
            logger.info("Webhook notification sent successfully")
        else:
            logger.debug(
                "Notification not sent (rate limited, no new availability, or error)"
            )

        # Check if heartbeat notification is needed
        heartbeat_sent = await self.notification_manager.send_heartbeat_if_needed()
        if heartbeat_sent:
            logger.info("Heartbeat notification sent successfully")

    async def run(self) -> None:
        """Run the main application loop."""
        logger.info("Starting Nintendo Museum Booking Assistant")
        logger.info(f"Monitoring dates: {self.config.target_dates}")
        logger.info(f"Webhook URL: {mask_sensitive_url(self.config.webhook.url)}")

        self.setup_signal_handlers()

        try:
            # Test webhook configuration first
            logger.info("Testing webhook configuration...")
            from .notifier import WebhookNotifier

            async with WebhookNotifier(self.config) as webhook:
                webhook_test_ok = await webhook.test_webhook()

            if not webhook_test_ok:
                logger.warning(
                    "Webhook test failed - notifications may not work properly"
                )
            else:
                logger.info("Webhook test successful")

            # Start polling
            async with AvailabilityPoller(self.config) as poller:
                self.poller = poller

                # Create polling task
                polling_task = asyncio.create_task(
                    poller.start_polling(self.handle_availability_found)
                )

                # Wait for shutdown signal
                shutdown_task = asyncio.create_task(self._shutdown_event.wait())

                # Wait for either polling to complete or shutdown signal
                done, pending = await asyncio.wait(
                    [polling_task, shutdown_task], return_when=asyncio.FIRST_COMPLETED
                )

                # Cancel remaining tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                # Stop polling gracefully
                if self.poller:
                    self.poller.stop_polling()

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise
        finally:
            logger.info("Nintendo Museum Booking Assistant stopped")

    async def check_once(self) -> set[str]:
        """
        Perform a single availability check (useful for testing).

        Returns:
            Set of available dates
        """
        logger.info("Performing single availability check...")

        async with AvailabilityPoller(self.config) as poller:
            available_dates = await poller.check_availability(self.config.target_dates)

        if available_dates:
            logger.info(f"Found availability: {available_dates}")
        else:
            logger.info("No availability found")

        return available_dates


async def main() -> None:
    """Main entry point."""
    try:
        # Check if config file exists
        config_path = Path("config.yaml")
        if not config_path.exists():
            print(f"Error: Configuration file not found: {config_path}")
            print(
                "Please create a config.yaml file based on the example configuration."
            )
            sys.exit(1)

        assistant = BookingAssistant(config_path)

        # Check command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == "--check-once":
            await assistant.check_once()
        else:
            await assistant.run()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

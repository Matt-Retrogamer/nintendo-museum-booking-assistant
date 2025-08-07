"""Tests for the main application functionality."""

import signal
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import yaml

from src.config import Config
from src.main import BookingAssistant


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    config_data = {
        "target_dates": ["2025-09-25", "2025-09-26"],
        "polling": {"interval_seconds": 1, "page_load_delay_seconds": 0},
        "webhook": {
            "url": "https://maker.ifttt.com/trigger/test/with/key/test_key",
            "event_name": "test_event",
            "timeout_seconds": 30,
        },
        "website": {"url": "https://test.com", "availability_class": "sale"},
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        config_path = Path(f.name)

    yield config_path

    # Cleanup
    config_path.unlink()


class TestBookingAssistant:
    """Test the main BookingAssistant class."""

    def test_initialization(self, temp_config_file):
        """Test BookingAssistant initialization."""
        assistant = BookingAssistant(temp_config_file)

        assert isinstance(assistant.config, Config)
        assert assistant.config.target_dates == ["2025-09-25", "2025-09-26"]
        assert assistant.notification_manager is not None

    def test_setup_logging(self, temp_config_file):
        """Test logging setup."""
        with patch("logging.basicConfig") as mock_basic_config:
            BookingAssistant(temp_config_file)

            mock_basic_config.assert_called_once()
            call_args = mock_basic_config.call_args[1]
            assert "level" in call_args
            assert "format" in call_args
            assert "handlers" in call_args

    @pytest.mark.asyncio
    async def test_handle_availability_found(self, temp_config_file):
        """Test handling of found availability."""
        assistant = BookingAssistant(temp_config_file)

        with patch.object(
            assistant.notification_manager, "notify_if_needed"
        ) as mock_notify:
            mock_notify.return_value = True

            available_dates = {"2025-09-25"}
            await assistant.handle_availability_found(available_dates)

            mock_notify.assert_called_once_with(available_dates)

    @pytest.mark.asyncio
    async def test_check_once(self, temp_config_file):
        """Test single availability check."""
        assistant = BookingAssistant(temp_config_file)

        with patch("src.main.AvailabilityPoller") as mock_poller_class:
            mock_poller = AsyncMock()
            mock_poller.check_availability.return_value = {"2025-09-25"}
            mock_poller_class.return_value.__aenter__.return_value = mock_poller

            result = await assistant.check_once()

            assert result == {"2025-09-25"}
            mock_poller.check_availability.assert_called_once_with(
                assistant.config.target_dates
            )

    def test_signal_handlers_setup(self, temp_config_file):
        """Test signal handlers setup."""
        assistant = BookingAssistant(temp_config_file)

        with patch("signal.signal") as mock_signal:
            assistant.setup_signal_handlers()

            # Should set up handlers for SIGINT and SIGTERM
            assert mock_signal.call_count == 2

    @pytest.mark.asyncio
    async def test_run_with_shutdown_signal(self, temp_config_file):
        """Test running the assistant with shutdown signal."""
        assistant = BookingAssistant(temp_config_file)

        # Mock all the components
        with (
            patch("src.main.AvailabilityPoller") as mock_poller_class,
            patch("src.main.NotificationManager") as mock_notifier_class,
            patch.object(assistant, "setup_signal_handlers"),
            patch("asyncio.sleep"),
        ):
            # Mock poller
            mock_poller = AsyncMock()
            mock_poller.start_polling = AsyncMock()
            mock_poller.stop_polling = MagicMock()
            mock_poller_class.return_value.__aenter__.return_value = mock_poller

            # Mock notifier for webhook test
            mock_notifier = AsyncMock()
            mock_webhook = AsyncMock()
            mock_webhook.test_webhook.return_value = True
            mock_notifier.__aenter__.return_value = mock_webhook
            mock_notifier_class.return_value = mock_notifier

            # Mock the webhook notifier import
            with patch("src.notifier.WebhookNotifier", return_value=mock_notifier):
                # Simulate immediate shutdown
                assistant._shutdown_event.set()

                # Run should complete without errors
                await assistant.run()

                mock_poller.stop_polling.assert_called_once()
                # Webhook test should NOT be called with INFO level
                mock_webhook.test_webhook.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_webhook_test_in_debug_mode(self, temp_config_file):
        """Test that webhook test runs only in debug mode."""
        # Modify config to use DEBUG logging
        with open(temp_config_file) as f:
            config_data = yaml.safe_load(f)
        config_data["logging"]["level"] = "DEBUG"
        with open(temp_config_file, "w") as f:
            yaml.dump(config_data, f)

        assistant = BookingAssistant(temp_config_file)

        # Mock all the components
        with (
            patch("src.main.AvailabilityPoller") as mock_poller_class,
            patch("src.main.NotificationManager") as mock_notifier_class,
            patch.object(assistant, "setup_signal_handlers"),
            patch("asyncio.sleep"),
        ):
            # Mock poller
            mock_poller = AsyncMock()
            mock_poller.start_polling = AsyncMock()
            mock_poller.stop_polling = MagicMock()
            mock_poller_class.return_value.__aenter__.return_value = mock_poller

            # Mock notifier for webhook test
            mock_notifier = AsyncMock()
            mock_webhook = AsyncMock()
            mock_webhook.test_webhook.return_value = True
            mock_notifier.__aenter__.return_value = mock_webhook
            mock_notifier_class.return_value = mock_notifier

            # Mock the webhook notifier import
            with patch("src.notifier.WebhookNotifier", return_value=mock_notifier):
                # Simulate immediate shutdown
                assistant._shutdown_event.set()

                # Run should complete without errors
                await assistant.run()

                mock_poller.stop_polling.assert_called_once()
                # Webhook test SHOULD be called with DEBUG level
                mock_webhook.test_webhook.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_availability_found_with_dates(self, temp_config_file):
        """Test handle_availability_found with available dates."""
        assistant = BookingAssistant(temp_config_file)

        # Mock notification manager
        assistant.notification_manager = AsyncMock()
        assistant.notification_manager.notify_if_needed.return_value = True
        assistant.notification_manager.send_heartbeat_if_needed.return_value = False

        available_dates = {"2025-09-25", "2025-09-26"}
        await assistant.handle_availability_found(available_dates)

        assistant.notification_manager.notify_if_needed.assert_called_once_with(
            available_dates
        )
        assistant.notification_manager.send_heartbeat_if_needed.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_availability_found_no_dates(self, temp_config_file):
        """Test handle_availability_found with no available dates."""
        assistant = BookingAssistant(temp_config_file)

        # Mock notification manager
        assistant.notification_manager = AsyncMock()
        assistant.notification_manager.notify_if_needed.return_value = False
        assistant.notification_manager.send_heartbeat_if_needed.return_value = True

        available_dates = set()
        await assistant.handle_availability_found(available_dates)

        assistant.notification_manager.notify_if_needed.assert_called_once_with(
            available_dates
        )
        assistant.notification_manager.send_heartbeat_if_needed.assert_called_once()

    def test_signal_handler_execution(self, temp_config_file):
        """Test that signal handlers actually work when called."""
        assistant = BookingAssistant(temp_config_file)

        # Manually call the signal handler function
        with patch("signal.signal") as mock_signal:
            assistant.setup_signal_handlers()

            # Get the signal handler function that was registered
            signal_handler_func = mock_signal.call_args_list[0][0][1]

            # Call the signal handler
            signal_handler_func(signal.SIGINT, None)

            # Verify shutdown event was set
            assert assistant._shutdown_event.is_set()

    @pytest.mark.asyncio
    async def test_main_no_config_file(self):
        """Test main function with missing config file."""
        with (
            patch("sys.exit") as mock_exit,
            patch("pathlib.Path.exists", return_value=False),
        ):
            from src.main import main

            await main()
            # sys.exit is called once for missing config and once for the exception handler
            assert mock_exit.call_count >= 1
            mock_exit.assert_any_call(1)

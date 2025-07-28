"""Tests for the availability polling functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.config import Config
from src.poller import AvailabilityPoller


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return Config(
        target_dates=["2025-09-25", "2025-09-26"],
        polling={
            "interval_seconds": 1,
            "page_load_delay_seconds": 0,
        },
        webhook={
            "url": "https://maker.ifttt.com/trigger/test/with/key/test_key",
            "event_name": "test_event",
            "timeout_seconds": 30,
        },
        website={
            "url": "https://example.com/calendar",
            "availability_class": "sale",
        },
        logging={
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    )


class TestAvailabilityPoller:
    """Test the availability polling functionality."""

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_config):
        """Test that the poller works as an async context manager."""
        with patch("src.poller.async_playwright") as mock_playwright:
            mock_playwright_instance = AsyncMock()
            mock_browser = AsyncMock()
            mock_playwright_instance.chromium.launch.return_value = mock_browser
            mock_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_instance
            )

            async with AvailabilityPoller(mock_config) as poller:
                assert poller.browser is not None
                assert poller.playwright is not None

    @pytest.mark.asyncio
    async def test_check_availability_success(self, mock_config):
        """Test successful availability check with available dates."""
        with patch("src.poller.async_playwright") as mock_playwright:
            # Setup mocks
            mock_playwright_instance = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            # Mock Playwright setup
            mock_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_instance
            )
            mock_playwright_instance.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page

            # Mock page interactions
            mock_page.goto = AsyncMock()
            mock_page.wait_for_selector = AsyncMock()
            mock_page.query_selector_all.return_value = [
                MagicMock(),
                MagicMock(),
            ]  # Mock date cells

            # Mock finding date cells
            mock_page.query_selector.side_effect = lambda selector: (
                MagicMock() if "2025-09-25" in selector else None
            )

            # Mock JavaScript evaluation - return True for availability
            mock_page.evaluate.return_value = True

            async with AvailabilityPoller(mock_config) as poller:
                available_dates = await poller.check_availability(
                    ["2025-09-25", "2025-09-26"]
                )

            assert "2025-09-25" in available_dates
            mock_page.goto.assert_called_once()
            mock_page.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_availability_no_dates(self, mock_config):
        """Test availability check when no dates are available."""
        with patch("src.poller.async_playwright") as mock_playwright:
            # Setup mocks
            mock_playwright_instance = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            # Mock Playwright setup
            mock_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_instance
            )
            mock_playwright_instance.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page

            # Mock page interactions
            mock_page.goto = AsyncMock()
            mock_page.wait_for_selector = AsyncMock()
            mock_page.query_selector_all.return_value = []  # No date cells found
            mock_page.query_selector.return_value = None  # No date cells found

            async with AvailabilityPoller(mock_config) as poller:
                available_dates = await poller.check_availability(["2025-09-25"])

            assert available_dates == set()

    @pytest.mark.asyncio
    async def test_check_availability_error_handling(self, mock_config):
        """Test error handling during availability check."""
        with patch("src.poller.async_playwright") as mock_playwright:
            # Setup mocks
            mock_playwright_instance = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            # Mock Playwright setup
            mock_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_instance
            )
            mock_playwright_instance.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page

            # Mock page error
            mock_page.goto.side_effect = Exception("Page load error")

            async with AvailabilityPoller(mock_config) as poller:
                available_dates = await poller.check_availability(["2025-09-25"])

            assert available_dates == set()

    @pytest.mark.asyncio
    async def test_check_dates_on_page_with_availability(self, mock_config):
        """Test _check_dates_on_page method with available dates."""
        poller = AvailabilityPoller(mock_config)

        # Mock page object
        mock_page = AsyncMock()
        mock_cell = MagicMock()
        mock_cell.get_attribute.return_value = "2025-09-25"

        mock_page.query_selector_all.return_value = [mock_cell]
        mock_page.query_selector.return_value = mock_cell
        mock_page.evaluate.return_value = True  # Available

        available_dates = await poller._check_dates_on_page(mock_page, ["2025-09-25"])

        assert "2025-09-25" in available_dates

    @pytest.mark.asyncio
    async def test_check_dates_on_page_no_availability(self, mock_config):
        """Test _check_dates_on_page method with no available dates."""
        poller = AvailabilityPoller(mock_config)

        # Mock page object
        mock_page = AsyncMock()
        mock_page.query_selector_all.return_value = []
        mock_page.query_selector.return_value = None

        available_dates = await poller._check_dates_on_page(mock_page, ["2025-09-25"])

        assert available_dates == set()

    @pytest.mark.asyncio
    async def test_start_polling_with_availability(self, mock_config):
        """Test start_polling method when availability is found."""
        with patch("src.poller.async_playwright") as mock_playwright:
            # Setup mocks
            mock_playwright_instance = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_instance
            )
            mock_playwright_instance.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page

            # Mock successful availability check
            mock_page.goto = AsyncMock()
            mock_page.wait_for_selector = AsyncMock()
            mock_page.query_selector_all.return_value = [MagicMock()]
            mock_page.query_selector.return_value = MagicMock()
            mock_page.evaluate.return_value = True

            callback_called = False
            available_dates_result = None

            async def mock_callback(dates):
                nonlocal callback_called, available_dates_result
                callback_called = True
                available_dates_result = dates
                # Stop polling after first callback
                poller.stop_polling()

            async with AvailabilityPoller(mock_config) as poller:
                # Patch asyncio.sleep to speed up test
                with patch("asyncio.sleep", new_callable=AsyncMock):
                    await poller.start_polling(mock_callback)

            assert callback_called

    def test_stop_polling(self, mock_config):
        """Test stop_polling method."""
        poller = AvailabilityPoller(mock_config)
        assert poller._running is False

        poller._running = True
        poller.stop_polling()
        assert poller._running is False

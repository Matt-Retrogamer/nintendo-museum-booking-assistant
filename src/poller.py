"""Website polling functionality for Nintendo Museum ticket availability."""

import asyncio
import logging

from playwright.async_api import async_playwright

from .config import Config

logger = logging.getLogger(__name__)


class AvailabilityPoller:
    """Polls the Nintendo Museum website for ticket availability using Playwright."""

    def __init__(self, config: Config):
        """Initialize the poller with configuration."""
        self.config = config
        self.playwright = None
        self.browser = None
        self._running = False

    async def __aenter__(self) -> "AvailabilityPoller":
        """Async context manager entry."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        try:
            if self.browser:
                await self.browser.close()
        except Exception as e:
            logger.debug(f"Error closing browser: {e}")
        try:
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.debug(f"Error stopping playwright: {e}")

    async def check_availability(self, target_dates: list[str]) -> set[str]:
        """
        Check availability for the specified dates using Playwright.

        Args:
            target_dates: List of dates in YYYY-MM-DD format

        Returns:
            Set of available dates
        """
        if not self.browser:
            raise RuntimeError("Poller must be used as an async context manager")

        try:
            page = await self.browser.new_page()

            # Set user agent to avoid bot detection
            await page.set_extra_http_headers(
                {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            )

            logger.debug(f"Navigating to calendar page: {self.config.website.url}")
            await page.goto(str(self.config.website.url))

            # Wait for the page to load and JavaScript to execute
            # This mimics the original TRIGGER_DELAY of 2000ms
            await asyncio.sleep(self.config.polling.page_load_delay_seconds)

            # Additional wait for dynamic content to load
            try:
                # Wait for at least one calendar cell to appear (with a timeout)
                await page.wait_for_selector("td[data-date]", timeout=10000)
                logger.debug("Calendar cells detected on page")
            except Exception as e:
                logger.debug(f"No calendar cells found within timeout: {e}")
                # Continue anyway in case the structure is different

            available_dates = await self._check_dates_on_page(page, target_dates)

            await page.close()
            return available_dates

        except Exception as e:
            logger.error(f"Error while checking availability: {e}")
            return set()

    async def _check_dates_on_page(self, page, target_dates: list[str]) -> set[str]:
        """
        Check for availability of target dates on the loaded page.

        Args:
            page: Playwright page object
            target_dates: List of target dates to check

        Returns:
            Set of available dates
        """
        available_dates = set()

        # Get all date cells to debug what's available
        try:
            date_cells = await page.query_selector_all("td[data-date]")
            logger.debug(f"Found {len(date_cells)} date cells on page")

            if date_cells:
                # Sample some dates to see what's available
                sample_dates = []
                for _i, cell in enumerate(date_cells[:5]):  # Check first 5 cells
                    date_attr = await cell.get_attribute("data-date")
                    if date_attr:
                        sample_dates.append(date_attr)
                logger.debug(f"Sample dates found on page: {sample_dates}")
        except Exception as e:
            logger.debug(f"Error getting date cells: {e}")

        for date in target_dates:
            try:
                # Look for the specific date cell (matching original JS logic)
                date_cell = await page.query_selector(f'td[data-date="{date}"]')

                if date_cell:
                    logger.debug(f"Found date cell for {date}")

                    # Check for availability using the nested structure from original JS:
                    # td?.children?.[0]?.children?.[1]?.children?.[0]?.children?.[0]?.children?.[0]?.children?.[0]?.className
                    is_available = await page.evaluate(f'''
                        () => {{
                            const td = document.querySelector('td[data-date="{date}"]');
                            if (!td) return false;

                            // Navigate the nested structure as in the original JavaScript
                            const element = td?.children?.[0]?.children?.[1]?.children?.[0]?.children?.[0]?.children?.[0]?.children?.[0];
                            return element?.className === "{self.config.website.availability_class}";
                        }}
                    ''')

                    if is_available:
                        logger.info(f"Availability found for date: {date}")
                        available_dates.add(date)
                    else:
                        logger.debug(
                            f"No availability for date: {date} (found cell but no '{self.config.website.availability_class}' class)"
                        )

                        # Debug: Get the actual class name for troubleshooting
                        actual_class = await page.evaluate(f'''
                            () => {{
                                const td = document.querySelector('td[data-date="{date}"]');
                                const element = td?.children?.[0]?.children?.[1]?.children?.[0]?.children?.[0]?.children?.[0]?.children?.[0];
                                return element?.className || 'no-class-found';
                            }}
                        ''')
                        logger.debug(f"Actual class for {date}: {actual_class}")
                else:
                    logger.debug(f"Date cell not found for: {date}")

            except Exception as e:
                logger.error(f"Error checking date {date}: {e}")

        return available_dates

    async def start_polling(self, on_availability_found) -> None:
        """
        Start continuous polling for availability.

        Args:
            on_availability_found: Callback function to call when availability is found
        """
        self._running = True
        logger.info("Starting availability polling...")
        logger.info(f"Target dates: {self.config.target_dates}")
        logger.info(f"Polling interval: {self.config.polling.interval_seconds} seconds")

        while self._running:
            try:
                available_dates = await self.check_availability(
                    self.config.target_dates
                )

                if available_dates:
                    logger.info(f"Found availability for dates: {available_dates}")
                    await on_availability_found(available_dates)
                else:
                    logger.debug("No availability found")

                # Wait before next poll
                await asyncio.sleep(self.config.polling.interval_seconds)

            except asyncio.CancelledError:
                logger.info("Polling cancelled")
                break
            except Exception as e:
                logger.error(f"Error during polling: {e}")
                # Continue polling despite errors
                await asyncio.sleep(self.config.polling.interval_seconds)

        logger.info("Polling stopped")

    def stop_polling(self) -> None:
        """Stop the polling loop."""
        self._running = False
        logger.info("Stopping polling...")

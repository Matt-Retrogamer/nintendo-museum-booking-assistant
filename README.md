# Nintendo Museum Booking Assistant

A Python-based tool that monitors the Nintendo Museum ticket booking website for availability and sends webhook notifications when tickets become available for specified dates.

This project ports the core functionality from the original [Nintendo Museum Reservation Notifier](https://github.com/zhxie/nintendo-museum-reservation-notifier) into a modern, async Python application with IFTTT webhook integration and headless browser automation.

## Features

- 🎯 **Targeted Monitoring**: Monitor specific dates for ticket availability
- 🔄 **Asynchronous Polling**: Efficient, non-blocking website monitoring using Playwright  
- 🌐 **JavaScript Support**: Uses headless browser automation to handle dynamic content
- 📱 **IFTTT Integration**: Send notifications via webhook to trigger IFTTT automations
- 🔔 **Smart Notifications**: Get alerted when dates become available, disappear, and reappear (with grace period)
- ⚙️ **Configurable**: Customizable polling intervals and target dates
- 🛡️ **Robust Error Handling**: Graceful handling of network errors and rate limiting
- 🔒 **Security**: Sensitive information (webhook URLs, API keys) are masked in log output
- 📋 **Debug Mode**: Enhanced logging and troubleshooting capabilities
- 🧪 **Webhook Testing**: Built-in webhook testing functionality
- 📋 **Comprehensive Logging**: Detailed logging for monitoring and debugging
- 🧪 **Well Tested**: Comprehensive test suite with high coverage

## How It Works

The assistant uses Playwright to launch a headless browser that loads the Nintendo Museum calendar page, executes JavaScript, and monitors for ticket availability on your specified dates. When availability is found (indicated by a "sale" CSS class), it triggers an IFTTT webhook that can:

- Send push notifications to your phone
- Send emails or SMS messages  
- Trigger other automations (smart home, calendar events, etc.)

### Smart Notification System

The notification system intelligently tracks availability changes:

**Scenario 1: First Time Available**
- Date becomes available → ✅ **Alert sent**

**Scenario 2: No Change**
- Date remains available → ❌ No duplicate alert

**Scenario 3: Reappearing Availability**
- Date disappears → No action
- Date reappears → ✅ **New alert sent** (after 5-minute grace period)

This ensures you don't miss slots that pop in and out of availability due to high demand, while preventing notification spam through a built-in grace period.

## Requirements

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) for dependency management
- [Task](https://taskfile.dev) for running common tasks (optional but recommended)
- Playwright browser binaries (automatically installed with `task install`)

## Prerequisites Installation

Before installing the project, you'll need to install the required tools: **uv** and **Task**.

### Installing uv (Astral's Python Package Manager)

**macOS:**
```bash
# Using Homebrew (recommended)
brew install uv

# Or using curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Ubuntu/Debian:**
```bash
# Using snap (recommended)
sudo snap install astral-uv --classic

# Or using curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv

# Or using pipx
pipx install uv
```

### Installing Task (Task Runner)

**macOS:**
```bash
# Using Homebrew (recommended)
brew install go-task

# Or using curl
curl -sL https://taskfile.dev/install.sh | sh
```

**Ubuntu/Debian:**
```bash
# Using snap (recommended)
sudo snap install task --classic

# Or using curl
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d

# Or download from GitHub releases
sudo wget https://github.com/go-task/task/releases/latest/download/task_linux_amd64.tar.gz -O - | sudo tar -xz -C /usr/local/bin task
```

### Verification

After installation, verify both tools are working:

```bash
# Check uv installation
uv --version

# Check Task installation  
task --version
```

**Expected output example:**
```
$ uv --version
uv 0.4.10

$ task --version
Task version: v3.38.0
```

## Installation

**Prerequisites:** Make sure you have installed [uv and Task](#prerequisites-installation) before proceeding.

1. Clone the repository:
```bash
git clone <repository-url>
cd nintendo-museum-booking-assistant
```

2. Install all dependencies (Python packages + browser binaries):
```bash
task install
```

This will automatically:
- Install Python dependencies with `uv sync --dev`
- Download Playwright Chromium browser binary
- Install system dependencies for headless browser operation

**Alternative manual installation** (if you prefer not to use Task):
```bash
uv sync --dev
uv run playwright install chromium
uv run playwright install-deps chromium
```

## Quick Start

**Prerequisites:** Ensure you have [uv and Task installed](#prerequisites-installation) first.

1. **Install and setup:**
```bash
git clone <repository-url>
cd nintendo-museum-booking-assistant
task install
```

2. **Create configuration:**
```bash
cp config.yaml.example config.yaml
# Edit config.yaml with your target dates and IFTTT webhook URL
```

3. **Test webhook:**
```bash
task test-webhook
```

4. **Start monitoring:**
```bash
task run
```

For debugging issues, use:
```bash
task run-debug
```

## Current Status ✅

**Fully Functional** - Successfully monitors Nintendo Museum calendar with:
- ✅ **JavaScript Support**: Playwright headless browser handles dynamic content
- ✅ **Calendar Detection**: Successfully finds 168+ date cells on the page
- ✅ **Target Date Recognition**: Correctly identifies and monitors your specified dates
- ✅ **Availability Detection**: Monitors for "sale" vs "soldOut" CSS classes
- ✅ **IFTTT Integration**: Webhook notifications working and tested
- ✅ **Debug Capabilities**: Comprehensive logging and troubleshooting tools
- ✅ **Production Ready**: Robust error handling and graceful shutdown

**Example Debug Output:**
```
2025-07-28 10:11:16,627 - Found 168 date cells on page
2025-07-28 10:11:16,639 - Found date cell for 2025-09-25
2025-07-28 10:11:16,640 - Actual class for 2025-09-25: soldOut
```

When tickets become available, the class will change from "soldOut" to "sale" and trigger notifications.

## Configuration

Create a `config.yaml` file in the project root (see `config.yaml` example):

```yaml
# Dates to monitor for available reservations
# Format: YYYY-MM-DD
target_dates:
  - "2025-09-25"
  - "2025-09-26" 
  - "2025-09-27"

# Polling configuration
polling:
  interval_seconds: 10  # How often to check for availability
  page_load_delay_seconds: 2  # Wait time after page loads before checking

# Webhook configuration for IFTTT
webhook:
  url: "https://maker.ifttt.com/trigger/nintendo_museum_available/with/key/YOUR_IFTTT_KEY"
  event_name: "nintendo_museum_available"
  timeout_seconds: 30

# Website configuration
website:
  url: "https://museum-tickets.nintendo.com/en/calendar"
  availability_class: "sale"  # CSS class indicating availability

# Logging configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### IFTTT Webhook Setup

1. Create an IFTTT account at [ifttt.com](https://ifttt.com)
2. Create a new applet:
   - **Trigger**: Webhooks → Receive a web request
   - **Event Name**: `nintendo_museum_available` (or your chosen event name)
   - **Action**: Choose your preferred notification method (notifications, email, SMS, etc.)

3. Get your webhook URL from the [IFTTT Webhooks service page](https://ifttt.com/maker_webhooks)
   - Go to "Settings" to see your key
   - Your webhook URL format: `https://maker.ifttt.com/trigger/{event_name}/with/key/{your_key}`

4. Update the `webhook.url` in your `config.yaml`

## Notification Behavior

### How Notifications Work

The system uses intelligent state tracking to determine when to send notifications:

**✅ You WILL receive notifications when:**
- A date becomes available for the first time
- A date becomes available again after being unavailable (respecting grace period)
- New dates become available while other dates remain available

**❌ You will NOT receive notifications when:**
- A date remains continuously available (no duplicate alerts)
- A date reappears within the 5-minute grace period (prevents spam)
- A date becomes unavailable (only availability triggers alerts)

### Grace Period

The system includes a **5-minute grace period** between notifications to prevent spam while still catching slots that come and go quickly. This means:

- If a date appears → disappears → reappears within 5 minutes: **No duplicate alert**
- If a date appears → disappears → reappears after 5+ minutes: **New alert sent**

### Example Scenarios

**Scenario A: High-demand slot that flickers**
```
10:00 AM - Date 2025-09-26 available → ✅ Alert sent
10:01 AM - Date 2025-09-26 unavailable → No action
10:02 AM - Date 2025-09-26 available → ❌ No alert (grace period)
10:07 AM - Date 2025-09-26 unavailable → No action  
10:08 AM - Date 2025-09-26 available → ✅ Alert sent (grace period expired)
```

**Scenario B: Multiple dates becoming available**
```
10:00 AM - Date 2025-09-26 available → ✅ Alert sent
10:05 AM - Dates 2025-09-26, 2025-09-27 available → ✅ Alert sent (for new date 2025-09-27)
```

This behavior ensures you don't miss opportunities while avoiding notification fatigue.

### IFTTT Webhook Payload

The webhook sends the following data to IFTTT:

```json
{
  "value1": "2025-09-25, 2025-09-26",  // Available dates (comma-separated)
  "value2": "https://museum-tickets.nintendo.com/en/calendar",  // Link to booking site
  "value3": "2025-07-28T14:30:00.123456"  // Timestamp when availability was found
}
```

You can use these values in your IFTTT action:
- `{{Value1}}`: Available dates
- `{{Value2}}`: Direct link to booking page
- `{{Value3}}`: Timestamp

Example notification message:
```
🎮 Nintendo Museum tickets available for: {{Value1}}
Book now: {{Value2}}
Found at: {{Value3}}
```

## Usage

### Start Monitoring

Using Task (recommended):
```bash
task run
```

Or directly with uv:
```bash
uv run python -m src.main
```

### Debug Mode

For enhanced debugging with detailed logging:
```bash
task run-debug
```

This mode sets the log level to DEBUG and provides detailed information about:
- Page navigation and loading
- Calendar cell detection
- Date availability checking
- Actual CSS classes found on target dates

### Test Webhook Configuration

Before starting monitoring, test your IFTTT webhook:
```bash
task test-webhook
```

This sends a test notification to verify your webhook configuration is working correctly.

### Development Tasks

Install dependencies:
```bash
task install
```

Run tests:
```bash
task test
```

Run tests with coverage:
```bash
task test-cov
```

Lint code:
```bash
task lint
```

Format code:
```bash
task format
```

Clean temporary files:
```bash
task clean
```

Development setup (install + lint + test):
```bash
task dev
```

## Project Structure

```
nintendo-museum-booking-assistant/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── poller.py          # Website polling logic
│   ├── notifier.py        # Webhook notification handling
│   └── main.py            # Main application entry point
├── tests/
│   ├── __init__.py
│   ├── test_config.py     # Configuration tests
│   ├── test_poller.py     # Polling functionality tests
│   ├── test_notifier.py   # Notification tests
│   └── test_main.py       # Main application tests
├── config.yaml            # Configuration file
├── pyproject.toml         # Project dependencies and settings
├── Taskfile.yml           # Task definitions
└── README.md              # This file
```

## Core Components

### Configuration Management (`src/config.py`)
- Validates configuration using Pydantic models
- Supports YAML configuration files
- Provides type-safe configuration access

### Website Poller (`src/poller.py`)
- Uses Playwright for headless browser automation
- Handles JavaScript-rendered content dynamically
- Detects calendar elements after page load and script execution
- Configurable polling intervals and delays
- Robust error handling for network issues and browser automation
- Enhanced debugging capabilities showing actual CSS classes

### Webhook Notifier (`src/notifier.py`)
- IFTTT webhook integration
- Smart state tracking for reappearing availability
- Rate limiting with 5-minute grace period to prevent notification spam
- Comprehensive notification logic for dates that appear, disappear, and reappear
- Webhook testing functionality
- Comprehensive error handling and logging

### Main Application (`src/main.py`)
- Coordinates polling and notification components
- Signal handling for graceful shutdown
- Comprehensive logging setup
- Environment variable support for debug mode

## Logging

The application creates detailed logs in `nintendo_museum_assistant.log` and outputs to the console. Log levels can be configured in `config.yaml`:

- **DEBUG**: Detailed debugging information
- **INFO**: General operational information (default)
- **WARNING**: Warning messages
- **ERROR**: Error messages

## Error Handling

The application is designed to be resilient:

- **Network Errors**: Automatically retries after configured intervals
- **Browser Automation Errors**: Graceful handling of Playwright issues
- **JavaScript Loading Errors**: Continues monitoring even if dynamic content fails to load
- **Parsing Errors**: Logs errors and continues monitoring
- **Webhook Failures**: Logs failures but continues monitoring
- **Configuration Errors**: Validates configuration on startup
- **Graceful Shutdown**: Handles SIGINT/SIGTERM signals and properly closes browser resources

## Rate Limiting

To be respectful to the Nintendo Museum website:
- Default polling interval: 10 seconds
- Page load delay: 2 seconds (mimics original behavior)
- Additional wait for dynamic content loading
- Configurable timeouts for HTTP requests and page loads
- Automatic backoff on errors

### Notification Rate Limiting

The notification system includes intelligent rate limiting:
- **Grace Period**: 5-minute cooldown between notifications
- **Smart Deduplication**: Prevents duplicate alerts for unchanged availability
- **Reappearing Detection**: Allows new alerts when dates reappear after being unavailable
- **Spam Prevention**: Balances responsiveness with notification fatigue

## Browser Automation

The application uses Playwright with Chromium in headless mode:
- **User Agent Spoofing**: Sets realistic browser headers to avoid bot detection
- **JavaScript Execution**: Fully renders the page including dynamic calendar content
- **Element Detection**: Waits for calendar elements to appear before checking availability
- **Resource Optimization**: Uses headless mode for minimal resource usage
- **Proper Cleanup**: Ensures browser processes are properly terminated

## Testing

The project includes comprehensive tests covering:
- Configuration validation and error handling
- Website polling with browser automation and error scenarios
- Smart notification system including reappearing availability logic
- Webhook functionality and network error handling
- Main application workflow and signal handling
- State tracking and rate limiting behavior
- Browser automation error handling and recovery

Run tests with coverage:
```bash
task test-cov
```

Current test coverage: **82%** with **35 comprehensive tests** including:
- **5 configuration tests** covering validation and error cases
- **9 polling tests** including browser automation and error recovery  
- **10 notification tests** covering webhooks and smart notification behavior
- **6 main application tests** covering workflow and signal handling
- **5 URL masking tests** for security and privacy

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `task test`
6. Ensure code is properly formatted: `task format`
7. Ensure linting passes: `task lint`
8. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Disclaimer

This tool is for personal use only and is not affiliated with Nintendo. Please use responsibly and in accordance with Nintendo's terms of service. The tool does not automatically book tickets - it only notifies you when availability is detected.

## Troubleshooting

### Prerequisites Issues

**uv command not found**
```
zsh: command not found: uv
bash: uv: command not found
```
Solution: Install uv following the [Prerequisites Installation](#prerequisites-installation) section. On macOS, try `brew install uv`. On Ubuntu, use the curl installation method.

**Task command not found**
```
zsh: command not found: task
bash: task: command not found
```
Solution: Install Task following the [Prerequisites Installation](#prerequisites-installation) section. On macOS, try `brew install go-task`. On Ubuntu, use `sudo snap install task --classic`.

**Permission denied when installing with snap**
```
error: cannot install "task": snap not found
```
Solution: Ensure snapd is installed on Ubuntu: `sudo apt update && sudo apt install snapd`

**Python version too old**
```
Python 3.10 is not supported. Requires Python 3.11 or higher.
```
Solution: Update Python to version 3.11 or higher. On Ubuntu: `sudo apt install python3.11`. On macOS: `brew install python@3.11` or download from python.org.

### Common Issues

**Configuration file not found**
```
Error: Configuration file not found: config.yaml
```
Solution: Create a `config.yaml` file based on the example configuration above.

**Invalid date format**
```
ValueError: Invalid date format 'invalid-date'. Use YYYY-MM-DD
```
Solution: Ensure all dates in `target_dates` are in YYYY-MM-DD format.

**Webhook test fails**
```
Webhook test failed: Network error
```
Solution: Verify your IFTTT webhook URL and internet connection.

**Browser automation issues**
```
Error: Playwright browser not found
Error: Browser type does not exist, please run playwright install
```
Solution: Install Playwright browsers. If you used `task install`, browsers should already be installed. Otherwise run:
```bash
uv run playwright install chromium
uv run playwright install-deps chromium
```

Or simply run the complete installation:
```bash
task install
```

**Date cells showing "soldOut" instead of availability**
```
Actual class for 2025-09-25: soldOut
```
This is normal when tickets aren't available yet. The application will detect when the class changes to "sale".

**No availability found**
```
No availability found
```
This is normal - the tool will continue monitoring until availability is detected.

### Debug Mode

For detailed debugging, use the debug task:

```bash
task run-debug
```

This automatically sets LOG_LEVEL=DEBUG and shows detailed information about:
- Browser navigation and page loading
- Number of calendar cells detected
- Sample dates found on the page
- Exact CSS classes for your target dates
- JavaScript execution results

**Note**: Sensitive information like webhook URLs and API keys are automatically masked in log output with `****` for security.

### Environment Variables

You can override configuration using environment variables:
- `LOG_LEVEL`: Override logging level (DEBUG, INFO, WARNING, ERROR)

Example:
```bash
LOG_LEVEL=DEBUG task run
```

# Nintendo Museum Booking Assistant

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-89%25-brightgreen.svg)](#testing)
[![Tests](https://img.shields.io/badge/tests-59%20passing-brightgreen.svg)](#testing)

A Python-based tool that monitors the Nintendo Museum ticket booking website for availability and sends webhook notifications when tickets become available for specified dates.

This project ports the core functionality from the original [Nintendo Museum Reservation Notifier](https://github.com/zhxie/nintendo-museum-reservation-notifier) into a modern, async Python application with IFTTT webhook integration and headless browser automation.

## Features

- 🎯 **Targeted Monitoring**: Monitor specific dates for ticket availability
- 🔄 **Asynchronous Polling**: Efficient, non-blocking website monitoring using Playwright  
- 🌐 **JavaScript Support**: Uses headless browser automation to handle dynamic content
- 📱 **IFTTT Integration**: Send notifications via webhook to trigger IFTTT automations
- 🔔 **Smart Notifications**: Get alerted when dates become available, disappear, and reappear (with grace period)
- 💓 **Heartbeat Monitoring**: Periodic "alive" notifications to confirm service is running
- ⚙️ **Configurable**: Customizable polling intervals and target dates
- 🛡️ **Robust Error Handling**: Graceful handling of network errors and rate limiting
- 🔒 **Security**: Sensitive information (webhook URLs, API keys) are masked in log output
- 📋 **Debug Mode**: Enhanced logging and troubleshooting capabilities
- 🧪 **Webhook Testing**: Built-in webhook testing functionality
- 📋 **Comprehensive Logging**: Detailed logging for monitoring and debugging
- 🧪 **Well Tested**: Comprehensive test suite with high coverage

## ⚡ Quick Start

**New to this?** Skip to the [Quick Start Guide](#quick-start-guide) for a step-by-step walkthrough.

**Want to deploy on a server?** See [Deployment Recommendations](#deployment-recommendations).

**Need help?** Check the [Troubleshooting](#troubleshooting) section for common issues.

## Table of Contents

- [Quick Start Guide](#quick-start-guide) - **Start here if you're new**
- [Features](#features)
- [Requirements](#requirements)
- [Prerequisites Installation](#prerequisites-installation)
- [Installation and Setup](#installation-and-setup)
- [Configuration](#configuration)
- [MCP Server - VS Code Integration](#mcp-server---vs-code-integration) - **Manage config with GitHub Copilot**
- [IFTTT Webhook Setup](#ifttt-webhook-setup)
- [Deployment Recommendations](#deployment-recommendations)
- [Docker Deployment](#docker-deployment)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Testing](#testing)
- [Contributing](#contributing)

## How It Works

**What it monitors:** Nintendo Museum ticket booking calendar at [museum-tickets.nintendo.com](https://museum-tickets.nintendo.com/en/calendar)
**How it works:** Detects when date CSS classes change from "soldOut" to "sale"
**Notifications:** Sends webhooks to IFTTT for push notifications, emails, SMS, etc.

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

## Quick Start Guide

**New to this project?** Follow this step-by-step guide:

> **⚠️ Before you start:** Make sure you have **Git** and **Python 3.11+** installed first! Check the [Requirements](#requirements) section above for simple installation commands if you don't have these tools yet.

### Step 1: Install Prerequisites

First, install the required tools on your system:

- **macOS users:** Install [Homebrew](https://brew.sh), then run:

  ```bash
  brew install uv go-task
  ```

- **Ubuntu/Linux users:** Run:

  ```bash
  sudo snap install astral-uv --classic
  sudo snap install task --classic
  ```

- **Windows users:** Use WSL with Ubuntu (see [Requirements](#requirements) section), then follow Ubuntu instructions above

### Step 2: Get the Code and Setup

```bash
# Clone the project
git clone https://github.com/Matt-Retrogamer/nintendo-museum-booking-assistant.git
cd nintendo-museum-booking-assistant

# Install everything needed
task install
```

### Step 3: Configure Your Monitoring

```bash
# Copy the example configuration
cp config.example.yaml config.yaml

# Edit the configuration file
nano config.yaml  # or use your preferred editor
```

**Required changes in config.yaml:**

1. **Set your target dates** - Replace the example dates with the dates you want to monitor (see important note below)
2. **Get an IFTTT webhook URL** - Follow the [IFTTT setup guide](#ifttt-webhook-setup) below
3. **Update the webhook URL** - Replace `YOUR_IFTTT_KEY` with your actual IFTTT key

> **📅 Important: Which dates should you monitor?**
>
> Only monitor dates that are **2-6 months in the future**. Nintendo typically releases tickets in batches a few months ahead of time. Monitoring dates too far in the future or dates that have already passed won't yield results.
>
> **Example:** If it's July 2025, monitor dates like September-December 2025, not dates in 2026 or past dates.

### Step 4: Test Your Setup

```bash
# Test your webhook configuration
task test-webhook
```

You should receive a test notification if everything is configured correctly.

### Step 5: Start Monitoring

```bash
# Start the monitoring service
task run
```

The application will continuously monitor for availability and send notifications when tickets become available.

**Need help?** Check the [Troubleshooting](#troubleshooting) section if you encounter any issues.

## Requirements

**Core requirements:**

- **Git** (to download the code): `brew install git` (macOS) or `sudo apt install git` (Ubuntu/Linux)
- **Python 3.11+**: `brew install python` (macOS) or `sudo apt install python3` (Ubuntu/Linux or equivalent for your Linux distribution)
- **Windows users**: Use [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/install) with Ubuntu, then follow Linux instructions
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

## Installation and Setup

**For experienced users** - condensed installation steps. **New users should follow the [Quick Start Guide](#quick-start-guide) above instead.**

**Prerequisites:** Ensure you have [uv and Task installed](#prerequisites-installation) first.

1. **Install and setup:**

```bash
git clone https://github.com/Matt-Retrogamer/nintendo-museum-booking-assistant.git
cd nintendo-museum-booking-assistant
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

2. **Create configuration:**

```bash
cp config.example.yaml config.yaml
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

## Deployment Recommendations

The Nintendo Museum Booking Assistant is designed as a **long-running monitoring service** that continuously polls the website for availability. Consider these deployment options:

### 🖥️ **Always-On Computer**

Run on a desktop computer, laptop, or home server that stays powered on:

- Ideal for home users with a dedicated machine
- Easy to monitor logs and status
- Can run in background while using the computer for other tasks

### ☁️ **Virtual Private Server (VPS)**

Deploy on a cloud VPS (DigitalOcean, Linode, AWS EC2, etc.):

- Runs 24/7 without local machine dependency
- Typically costs $5-10/month for basic VPS
- Access via SSH for monitoring and updates
- Recommended for reliable, unattended operation

### 🐳 **Docker Container**

Run in a Docker container for easy deployment and isolation:

- Portable across different systems
- Easy to restart and update
- Can run on any Docker-compatible host
- See [Docker Deployment](#docker-deployment) section below

### 📱 **Local Development/Testing**

For testing or short-term monitoring:

- Run locally during specific time periods
- Good for initial setup and webhook testing
- Not suitable for 24/7 monitoring unless machine stays on

## Docker Deployment

> **Note:** The Dockerfile and docker-compose.yml are provided as examples for containerized deployment. **No official Docker images are maintained** - users should build their own images using the provided Dockerfile. This ensures you have the latest code and can customize the build as needed.

### Building and Running Locally (Recommended)

1. **Create the Docker image:**

```bash
docker build -t nintendo-museum-assistant .
```

2. **Run the container:**

```bash
docker run -d \
  --name nintendo-museum-assistant \
  --restart unless-stopped \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v $(pwd)/logs:/app/logs \
  nintendo-museum-assistant
```

3. **View logs:**

```bash
docker logs -f nintendo-museum-assistant
```

4. **Stop the container:**

```bash
docker stop nintendo-museum-assistant
```

### Docker Compose (Alternative)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  nintendo-museum-assistant:
    build: .
    container_name: nintendo-museum-assistant
    restart: unless-stopped
    volumes:
      - ./config.yaml:/app/config.yaml:ro
      - ./logs:/app/logs
    environment:
      - LOG_LEVEL=INFO
```

Run with:

```bash
docker-compose up -d
```

### Production Deployment Tips

**For VPS/Server Deployment:**

```bash
# Clone the repository
git clone https://github.com/Matt-Retrogamer/nintendo-museum-booking-assistant.git
cd nintendo-museum-booking-assistant

# Install prerequisites (uv and task)
# ... follow Prerequisites Installation section

# Setup and configure
task install
cp config.example.yaml config.yaml
# Edit config.yaml with your settings

# Test the configuration
task test-webhook

# Run in background with nohup (alternative to Docker)
nohup task run > nintendo_museum.log 2>&1 &

# Or use screen/tmux for persistent sessions
screen -S nintendo-museum
task run
# Ctrl+A, D to detach
```

**For Docker Deployment:**

```bash
# Clone and setup
git clone https://github.com/Matt-Retrogamer/nintendo-museum-booking-assistant.git
cd nintendo-museum-booking-assistant

# Create your config file
cp config.example.yaml config.yaml
# Edit config.yaml with your settings

# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## Configuration

Create a `config.yaml` file in the project root (see `config.yaml` example):

```yaml
# Dates to monitor for available reservations
# Format: YYYY-MM-DD
target_dates:
  - "2025-10-25"
  - "2025-10-26" 
  - "2025-10-27"

# Polling configuration
polling:
  interval_seconds: 10  # How often to check for availability
  page_load_delay_seconds: 2  # Wait time after page loads before checking

# Webhook configuration for IFTTT
webhook:
  url: "https://maker.ifttt.com/trigger/nintendo_museum_available/with/key/YOUR_IFTTT_KEY"
  event_name: "nintendo_museum_available"
  timeout_seconds: 30
  
  # Heartbeat configuration (optional)
  # Enable/disable heartbeat notifications
  heartbeat_enabled: true  # Set to false to completely disable heartbeat notifications
  # Send a heartbeat notification every N hours to confirm service is running
  # Set to 0 or omit to disable heartbeat notifications (only when heartbeat_enabled is true)
  heartbeat_interval_hours: 24  # Send heartbeat every 24 hours

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

**Step-by-step IFTTT configuration:**

1. **Create an IFTTT account** at [ifttt.com](https://ifttt.com) (free account is sufficient)

2. **Create a new applet:**
   - Click "Create" → "If This Then That"
   - **Choose "This" (Trigger):** Search for "Webhooks" → Select "Receive a web request"
   - **Event Name:** Enter `nintendo_museum_available` (must match your config)
   - Click "Create trigger"

3. **Choose "That" (Action):** Select your preferred notification method:
   - **Notifications:** For mobile push notifications (recommended)
   - **Email:** For email alerts
   - **SMS:** For text messages (may require paid plan)
   - **Other:** Discord, Slack, etc.

4. **Get your webhook URL:**
   - Go to [IFTTT Webhooks service page](https://ifttt.com/maker_webhooks)
   - Click "Documentation"
   - Copy your webhook URL (it looks like: `https://maker.ifttt.com/trigger/nintendo_museum_available/with/key/YOUR_KEY_HERE`)

5. **Update your config.yaml:**
   - Replace `YOUR_IFTTT_KEY` in the webhook URL with your actual key
   - Save the file

**Example webhook URL format:**

```
https://maker.ifttt.com/trigger/nintendo_museum_available/with/key/dAbCdEfGhIjKlMnOpQrStUvWxYz
```

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
10:00 AM - Date 2025-10-26 available → ✅ Alert sent
10:01 AM - Date 2025-10-26 unavailable → No action
10:02 AM - Date 2025-10-26 available → ❌ No alert (grace period)
10:07 AM - Date 2025-10-26 unavailable → No action  
10:08 AM - Date 2025-10-26 available → ✅ Alert sent (grace period expired)
```

**Scenario B: Multiple dates becoming available**

```
10:00 AM - Date 2025-10-26 available → ✅ Alert sent
10:05 AM - Dates 2025-10-26, 2025-10-27 available → ✅ Alert sent (for new date 2025-10-27)
```

This behavior ensures you don't miss opportunities while avoiding notification fatigue.

### Heartbeat Notifications

The system can send periodic "heartbeat" notifications to confirm it's still running and monitoring for availability. This is especially useful for long-running deployments on VPS/Docker where you want to ensure the service hasn't crashed or stopped.

**Configuration:**

```yaml
webhook:
  heartbeat_enabled: true  # Set to false to completely disable heartbeat notifications
  heartbeat_interval_hours: 24  # Send heartbeat every 24 hours
  # Set heartbeat_interval_hours to 0 or omit to disable heartbeat notifications (only when heartbeat_enabled is true)
```

**Heartbeat behavior:**

- Sends a periodic notification at the configured interval
- Independent of availability notifications
- Uses the same webhook endpoint with different payload
- First heartbeat sent after the interval period (not immediately on startup)
- Can be disabled via `heartbeat_enabled: false` flag or by setting `heartbeat_interval_hours: 0`
- Defaults to enabled (`heartbeat_enabled: true`) with 24-hour interval

**Heartbeat webhook payload:**

```json
{
  "value1": "HEARTBEAT - Nintendo Museum Booking Assistant",
  "value2": "Service is running normally",
  "value3": "2025-07-28T14:30:00.123456"  // Timestamp of heartbeat
}
```

### IFTTT Webhook Payload

The webhook sends the following data to IFTTT:

```json
{
  "value1": "2025-10-25, 2025-10-26",  // Available dates (comma-separated)
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

## MCP Server - VS Code Integration

**🚀 New Feature**: Manage your Nintendo Museum booking configuration directly from GitHub Copilot in VS Code using natural language!

The MCP (Model Context Protocol) server allows you to manage your target dates and IFTTT webhook settings without manually editing configuration files. Perfect for users who prefer GUI interactions over command-line editing.

### What You Can Do

**Date Management:**
- Add dates: `"Add date 2025-12-25 to my Nintendo Museum config"`  
- Remove dates: `"Remove date 2025-10-26 from Nintendo Museum target dates"`
- List dates: `"Show me all Nintendo Museum target dates"`
- Clear dates: `"Clear all Nintendo Museum target dates"`
- Set dates: `"Set Nintendo Museum dates to 2025-11-15, 2025-11-16"`

**IFTTT Webhook Management:**
- Set webhook key: `"Set my Nintendo Museum IFTTT webhook key to abc123xyz"`
- Check status: `"Show me Nintendo Museum IFTTT webhook status"`

**General Status:**
- View config: `"Show me Nintendo Museum booking assistant config status"`

### Setup Instructions

#### 1. Install MCP Server Dependencies

```bash
cd mcp_server
pip install -r requirements.txt
```

#### 2. Configure VS Code

Create or update your VS Code MCP settings file:

**macOS:** `~/Library/Application Support/Code/User/globalStorage/github.copilot-chat/config.json`
**Windows:** `%APPDATA%/Code/User/globalStorage/github.copilot-chat/config.json`  
**Linux:** `~/.config/Code/User/globalStorage/github.copilot-chat/config.json`

Add this configuration (replace `/path/to/your/project` with your actual path):

```json
{
  "mcpServers": {
    "nintendo-museum-config": {
      "command": "python",
      "args": [
        "/path/to/your/nintendo-museum-booking-assistant/mcp_server/main.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/your/nintendo-museum-booking-assistant"
      }
    }
  }
}
```

#### 3. Restart VS Code

Restart VS Code to load the new MCP server configuration.

#### 4. Test the Connection

In VS Code, ask GitHub Copilot:
```
"Show me the current Nintendo Museum config status"
```

If configured correctly, Copilot will use the MCP server to retrieve and display your configuration.

### Features

- **Smart Processing**: Automatic date sorting, deduplication, and validation  
- **Past Date Warnings**: Get notified when adding dates that are in the past
- **Config Preservation**: All other settings remain untouched  
- **Error Handling**: Clear error messages for invalid dates or URLs
- **Status Checking**: View current configuration at any time

### Troubleshooting MCP Server

**MCP Server Not Found:**
- Verify the path in your VS Code configuration is correct
- Ensure Python and MCP dependencies are installed  
- Restart VS Code after configuration changes

**Config File Issues:**
- Ensure `config.yaml` exists in your project root
- Check file has proper YAML syntax and read/write permissions

See the [detailed MCP server documentation](mcp_server/README.md) for complete setup instructions and troubleshooting.

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
├── config.example.yaml    # Example configuration
├── pyproject.toml         # Project dependencies and settings
├── Taskfile.yml           # Task definitions
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker Compose configuration
├── .dockerignore          # Docker build ignore file
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

Current test coverage: **89%** with **59 comprehensive tests** including:

- **12 configuration tests** covering validation, error cases, and heartbeat_enabled flag functionality
- **11 main application tests** covering workflow, signal handling, and debug behavior  
- **22 notification tests** covering webhooks, smart notification behavior, heartbeat functionality, and error handling
- **9 poller tests** including core functionality and browser automation basics
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

⚠️ **Important Notes:**

- **Not affiliated with Nintendo**: This is an independent monitoring tool
- **Personal use only**: Use responsibly and respect Nintendo's terms of service  
- **No automatic booking**: This tool only sends notifications - you must manually book tickets
- **No guarantees**: Ticket availability depends on Nintendo's systems and demand
- **Monitor dates that make sense**: Only monitor dates when tickets are typically released (usually a few months in advance)

**Respect the website:** The tool includes built-in rate limiting (10-second intervals) to be respectful to Nintendo's servers.

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
Actual class for 2025-10-25: soldOut
```

This is normal when tickets aren't available yet. The application will detect when the class changes to "sale".

**No availability found**

```
No availability found
```

This is normal - the tool will continue monitoring until availability is detected.

### Docker Issues

**Docker build fails with Playwright installation**

```
Error: Failed to install browsers
```

Solution: Ensure Docker has enough memory allocated (at least 2GB). On Docker Desktop, increase memory limit in settings.

**Container exits immediately**

```
docker ps shows container as "Exited"
```

Solution: Check logs with `docker logs nintendo-museum-assistant`. Common issues:

- Missing or invalid config.yaml file
- Incorrect volume mount paths
- Insufficient permissions

**Config file not found in Docker**

```
Error: Configuration file not found: config.yaml
```

Solution: Ensure config.yaml exists in the same directory as docker-compose.yml and the volume mount is correct:

```bash
# Check if config.yaml exists
ls -la config.yaml

# Verify volume mount in docker-compose.yml
- ./config.yaml:/app/config.yaml:ro
```

**Browser automation fails in Docker**

```
Error: Browser type does not exist
```

Solution: The Dockerfile includes browser installation. If this fails, try rebuilding:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Logs not persisting**

```
Logs disappear when container restarts
```

Solution: Ensure logs directory exists and is properly mounted:

```bash
mkdir -p logs
# Check docker-compose.yml has: - ./logs:/app/logs
```

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

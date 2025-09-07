# Nintendo Museum Booking Assistant MCP Server

A Model Context Protocol (MCP) server that provides tools for managing the Nintendo Museum Booking Assistant configuration. This server allows you to easily manage target dates and IFTTT webhook settings directly from GitHub Copilot in VS Code.

## Features

### Date Management
- **Add dates**: Add new target dates to monitor
- **Remove dates**: Remove specific dates from monitoring
- **List dates**: View all currently configured dates
- **Clear dates**: Remove all target dates
- **Set dates**: Replace all dates with a new list

### IFTTT Webhook Management
- **Set webhook URL**: Configure your IFTTT webhook URL
- **Set webhook key**: Set just the IFTTT key (URL is constructed automatically)
- **View webhook status**: Check current webhook configuration

### Smart Features
- **Automatic sorting**: Dates are always kept in chronological order
- **Automatic deduplication**: Duplicate dates are automatically removed
- **Date validation**: Ensures all dates are in YYYY-MM-DD format and are valid
- **Past date warnings**: Warns when adding dates that are in the past
- **Config preservation**: All other configuration settings remain untouched

## Installation

### Prerequisites
- Python 3.11 or higher
- VS Code with GitHub Copilot
- Nintendo Museum Booking Assistant project

### Install Dependencies

The MCP server dependencies are included in the main project's `pyproject.toml`. Install them using:

```bash
# Install all dependencies (recommended)
uv sync --dev

# Or just the main dependencies
uv sync
```

The MCP server requires:
- `fastmcp>=0.2.0` - MCP server framework
- `pyyaml>=6.0.1` - YAML configuration parsing (already included)
- `pydantic>=2.5.0` - Data validation (already included)

## Setup and Configuration

### 1. Configure VS Code for MCP

Create or update your VS Code MCP settings file. The location depends on your system:

- **macOS**: `~/Library/Application Support/Code/User/globalStorage/github.copilot-chat/config.json`
- **Windows**: `%APPDATA%/Code/User/globalStorage/github.copilot-chat/config.json`
- **Linux**: `~/.config/Code/User/globalStorage/github.copilot-chat/config.json`

Add the following configuration:

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

**Important**: Replace `/path/to/your/nintendo-museum-booking-assistant` with the actual path to your project directory.

### 2. Restart VS Code

After configuring the MCP server, restart VS Code to load the new configuration.

### 3. Verify Connection

In VS Code, you can verify the MCP server is working by asking GitHub Copilot:

```
"Show me the current Nintendo Museum config status"
```

If everything is set up correctly, Copilot will use the MCP server to retrieve your current configuration.

## Usage Examples

Once configured, you can use natural language commands with GitHub Copilot to manage your Nintendo Museum booking assistant configuration:

### Date Management

#### Adding Dates
```
"Add date 2025-12-25 to my Nintendo Museum config"
"Add multiple dates: 2025-11-01, 2025-11-02, 2025-11-03 to Nintendo Museum"
```

#### Removing Dates
```
"Remove date 2025-10-26 from Nintendo Museum target dates"
"Remove dates 2025-10-01 and 2025-10-02 from my config"
```

#### Viewing Dates
```
"Show me all Nintendo Museum target dates"
"List my current Nintendo Museum booking dates"
"What dates am I monitoring for Nintendo Museum tickets?"
```

#### Managing All Dates
```
"Clear all Nintendo Museum target dates"
"Set Nintendo Museum dates to 2025-11-15, 2025-11-16, 2025-11-17"
"Replace all my Nintendo Museum dates with just 2025-12-01"
```

### IFTTT Webhook Management

#### Setting Webhook Key
```
"Set my Nintendo Museum IFTTT webhook key to abc123xyz"
"Update my IFTTT key for Nintendo Museum to my_new_key_456"
```

#### Setting Full Webhook URL
```
"Set Nintendo Museum IFTTT webhook URL to https://maker.ifttt.com/trigger/nintendo_museum_available/with/key/my_key"
```

#### Checking Webhook Status
```
"Show me my Nintendo Museum IFTTT webhook status"
"Is my Nintendo Museum webhook configured properly?"
```

### General Status
```
"Show me Nintendo Museum booking assistant config status"
"What's the current state of my Nintendo Museum configuration?"
```

## Available MCP Tools

The following tools are available to GitHub Copilot:

### Date Management Tools
- `get_config_status()`: Get overall configuration status
- `list_target_dates()`: List all target dates
- `add_target_dates(dates)`: Add new target dates
- `remove_target_dates(dates)`: Remove specific target dates
- `clear_all_target_dates()`: Remove all target dates
- `set_target_dates(dates)`: Replace all target dates

### IFTTT Webhook Tools
- `get_ifttt_webhook_status()`: Get webhook configuration status
- `set_ifttt_webhook_url(url)`: Set complete webhook URL
- `set_ifttt_webhook_key(key)`: Set webhook key (constructs URL automatically)

## Configuration File

The MCP server modifies your `config.yaml` file in the project root. It specifically manages:

```yaml
# These sections are managed by the MCP server:
target_dates:
  - "2025-10-25"  # Automatically sorted and deduplicated
  - "2025-10-26"
  - "2025-10-27"

webhook:
  url: "https://maker.ifttt.com/trigger/nintendo_museum_available/with/key/YOUR_KEY"
  # All other webhook settings are preserved

# All other sections remain untouched:
polling:
  interval_seconds: 10
  # ... other settings preserved
```

## Error Handling

The MCP server includes comprehensive error handling:

- **Date Validation**: Ensures dates are in YYYY-MM-DD format and are valid calendar dates
- **URL Validation**: Validates IFTTT webhook URLs and extracts keys properly
- **Config Preservation**: Creates backups before modifying configuration files
- **Helpful Messages**: Provides clear error messages and warnings

## Troubleshooting

### MCP Server Not Found
- Check that the path in your VS Code MCP configuration is correct
- Ensure Python and required packages are installed
- Verify VS Code has been restarted after configuration changes

### Config File Issues
- Ensure `config.yaml` exists in your project root
- Check that the file has proper YAML syntax
- Verify file permissions allow read/write access

### Date Format Issues
- Dates must be in YYYY-MM-DD format (e.g., "2025-01-01")
- Ensure dates are valid calendar dates
- Month and day must be zero-padded (01, not 1)

### IFTTT Webhook Issues
- URL must be from maker.ifttt.com domain
- URL must include `/trigger/` and `/with/key/` paths
- Get your webhook key from https://ifttt.com/maker_webhooks

## Development

### Running Tests

```bash
# Run all MCP server tests
python -m pytest tests/mcp_server/ -v

# Run specific test file
python -m pytest tests/mcp_server/test_validators.py -v

# Run with coverage
python -m pytest tests/mcp_server/ --cov=mcp_server --cov-report=html
```

### Adding New Features

1. Add the logic to appropriate module (`validators.py`, `config_manager.py`)
2. Add the MCP tool to `main.py` using the `@mcp.tool()` decorator
3. Add comprehensive tests
4. Update this documentation

## License

This MCP server is part of the Nintendo Museum Booking Assistant project and follows the same MIT license.

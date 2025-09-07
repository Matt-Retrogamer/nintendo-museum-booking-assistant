"""Nintendo Museum Booking Assistant MCP Server."""

__version__ = "0.1.0"

# Lazy imports to avoid dependency issues during development
def get_config_manager():
    """Get ConfigManager class."""
    from .config_manager import ConfigManager
    return ConfigManager

def get_validators():
    """Get validator functions."""
    from .validators import validate_date_format, validate_ifttt_webhook_url
    return validate_date_format, validate_ifttt_webhook_url

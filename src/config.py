"""Configuration management for Nintendo Museum Booking Assistant."""

import re
from pathlib import Path

import yaml
from pydantic import BaseModel, HttpUrl, field_validator


def mask_sensitive_url(url: str) -> str:
    """
    Mask sensitive parts of URLs for logging.

    Args:
        url: The URL to mask

    Returns:
        URL with sensitive parts masked
    """
    # Mask IFTTT webhook keys
    if "maker.ifttt.com" in url and "/with/key/" in url:
        # Pattern: https://maker.ifttt.com/trigger/event_name/with/key/SECRET_KEY
        pattern = r"(/with/key/)([^/?&]*)"
        return re.sub(
            pattern, lambda m: m.group(1) + ("****" if m.group(2) else ""), url
        )

    # Mask any API keys in query parameters
    pattern = r"([?&](?:key|token|secret|api_key)=)([^&]*)"
    return re.sub(pattern, r"\1****", url)


class PollingConfig(BaseModel):
    """Configuration for polling behavior."""

    interval_seconds: int = 10
    page_load_delay_seconds: int = 2

    @field_validator("interval_seconds")
    @classmethod
    def validate_interval(cls, v: int) -> int:
        """Validate polling interval."""
        if v < 1:
            raise ValueError("Polling interval must be at least 1 second")
        return v


class WebhookConfig(BaseModel):
    """Configuration for webhook notifications."""

    url: str
    event_name: str = "nintendo_museum_available"
    timeout_seconds: int = 30
    heartbeat_interval_hours: int = 24

    @field_validator("timeout_seconds")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """Validate webhook timeout."""
        if v < 1:
            raise ValueError("Webhook timeout must be at least 1 second")
        return v

    @field_validator("heartbeat_interval_hours")
    @classmethod
    def validate_heartbeat_interval(cls, v: int) -> int:
        """Validate heartbeat interval."""
        if v < 0:
            raise ValueError("Heartbeat interval must be 0 (disabled) or positive")
        return v


class WebsiteConfig(BaseModel):
    """Configuration for website monitoring."""

    url: HttpUrl = "https://museum-tickets.nintendo.com/en/calendar"
    availability_class: str = "sale"


class LoggingConfig(BaseModel):
    """Configuration for logging."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate logging level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid logging level. Must be one of: {valid_levels}")
        return v.upper()


class Config(BaseModel):
    """Main configuration model."""

    target_dates: list[str]
    polling: PollingConfig
    webhook: WebhookConfig
    website: WebsiteConfig
    logging: LoggingConfig

    @field_validator("target_dates")
    @classmethod
    def validate_target_dates(cls, v: list[str]) -> list[str]:
        """Validate target dates format."""
        if not v:
            raise ValueError("At least one target date must be specified")

        from datetime import datetime

        for date_str in v:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    f"Invalid date format '{date_str}'. Use YYYY-MM-DD"
                ) from None

        return v


def load_config(config_path: Path = Path("config.yaml")) -> Config:
    """Load configuration from YAML file."""
    import os

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    # Override log level from environment variable if set
    if "LOG_LEVEL" in os.environ:
        if "logging" not in config_data:
            config_data["logging"] = {}
        config_data["logging"]["level"] = os.environ["LOG_LEVEL"]

    return Config(**config_data)

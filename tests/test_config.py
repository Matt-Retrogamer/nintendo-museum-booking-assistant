"""Tests for configuration management."""

import tempfile
from pathlib import Path

import pytest
import yaml

from src.config import Config, load_config


@pytest.fixture
def sample_config_data():
    """Sample configuration data for testing."""
    return {
        "target_dates": ["2025-09-25", "2025-09-26"],
        "polling": {"interval_seconds": 10, "page_load_delay_seconds": 2},
        "webhook": {
            "url": "https://maker.ifttt.com/trigger/test/with/key/test_key",
            "event_name": "test_event",
            "timeout_seconds": 30,
        },
        "website": {
            "url": "https://museum-tickets.nintendo.com/en/calendar",
            "availability_class": "sale",
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    }


@pytest.fixture
def config_file(sample_config_data):
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(sample_config_data, f)
        config_path = Path(f.name)

    yield config_path

    # Cleanup
    config_path.unlink()


class TestConfig:
    """Test configuration loading and validation."""

    def test_load_valid_config(self, config_file):
        """Test loading a valid configuration file."""
        config = load_config(config_file)

        assert isinstance(config, Config)
        assert config.target_dates == ["2025-09-25", "2025-09-26"]
        assert config.polling.interval_seconds == 10
        assert config.webhook.event_name == "test_event"

    def test_config_validation_target_dates(self, sample_config_data):
        """Test validation of target dates."""
        # Test empty target dates
        sample_config_data["target_dates"] = []
        with pytest.raises(
            ValueError, match="At least one target date must be specified"
        ):
            Config(**sample_config_data)

        # Test invalid date format
        sample_config_data["target_dates"] = ["invalid-date"]
        with pytest.raises(ValueError, match="Invalid date format"):
            Config(**sample_config_data)

    def test_config_validation_polling_interval(self, sample_config_data):
        """Test validation of polling interval."""
        sample_config_data["polling"]["interval_seconds"] = 0
        with pytest.raises(
            ValueError, match="Polling interval must be at least 1 second"
        ):
            Config(**sample_config_data)

    def test_config_validation_logging_level(self, sample_config_data):
        """Test validation of logging level."""
        sample_config_data["logging"]["level"] = "INVALID"
        with pytest.raises(ValueError, match="Invalid logging level"):
            Config(**sample_config_data)

    def test_load_nonexistent_config(self):
        """Test loading a non-existent configuration file."""
        with pytest.raises(FileNotFoundError):
            load_config(Path("nonexistent.yaml"))

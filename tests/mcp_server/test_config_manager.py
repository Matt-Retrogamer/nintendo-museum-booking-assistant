"""Tests for MCP server config manager."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from mcp_server.config_manager import ConfigManager


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_data = {
            'target_dates': ['2025-01-01', '2025-01-02'],
            'webhook': {
                'url': 'https://maker.ifttt.com/trigger/test/with/key/test_key',
                'event_name': 'nintendo_museum_available',
                'timeout_seconds': 30
            },
            'polling': {
                'interval_seconds': 10
            }
        }
        yaml.dump(config_data, f, default_flow_style=False)
        temp_path = f.name

    yield temp_path

    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass

    # Also cleanup backup file if it exists
    backup_path = temp_path + '.backup'
    try:
        os.unlink(backup_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def empty_config_file():
    """Create an empty config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({}, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


class TestConfigManager:
    """Test ConfigManager class."""

    def test_init_with_path(self, temp_config_file):
        """Test initialization with custom config path."""
        manager = ConfigManager(temp_config_file)
        assert str(manager.config_path) == temp_config_file

    def test_init_without_path(self):
        """Test initialization with default path."""
        manager = ConfigManager()
        expected_path = Path(__file__).parent.parent.parent / "config.yaml"
        assert manager.config_path == expected_path

    def test_load_config_success(self, temp_config_file):
        """Test successful config loading."""
        manager = ConfigManager(temp_config_file)
        success, error, config = manager._load_config()

        assert success
        assert error == ""
        assert config is not None
        assert 'target_dates' in config
        assert 'webhook' in config

    def test_load_config_file_not_found(self):
        """Test loading non-existent config file."""
        manager = ConfigManager("/path/that/does/not/exist.yaml")
        success, error, config = manager._load_config()

        assert not success
        assert "Config file not found" in error
        assert config is None

    def test_get_target_dates_success(self, temp_config_file):
        """Test getting target dates successfully."""
        manager = ConfigManager(temp_config_file)
        success, error, dates = manager.get_target_dates()

        assert success
        assert error == ""
        assert dates == ['2025-01-01', '2025-01-02']

    def test_get_target_dates_missing_key(self, empty_config_file):
        """Test getting target dates when key doesn't exist."""
        manager = ConfigManager(empty_config_file)
        success, error, dates = manager.get_target_dates()

        assert success
        assert error == ""
        assert dates == []

    def test_set_target_dates_success(self, temp_config_file):
        """Test setting target dates successfully."""
        manager = ConfigManager(temp_config_file)
        new_dates = ['2025-02-01', '2025-02-02', '2025-01-01']  # unsorted with duplicate from original

        success, error = manager.set_target_dates(new_dates)
        assert success
        assert error == ""

        # Verify dates were set correctly (should be sorted and deduplicated)
        success, error, dates = manager.get_target_dates()
        assert success
        assert dates == ['2025-01-01', '2025-02-01', '2025-02-02']

    def test_set_target_dates_invalid(self, temp_config_file):
        """Test setting invalid target dates."""
        manager = ConfigManager(temp_config_file)
        invalid_dates = ['2025-02-01', 'invalid-date']

        success, error = manager.set_target_dates(invalid_dates)
        assert not success
        assert "Invalid dates found" in error

    def test_add_target_dates_success(self, temp_config_file):
        """Test adding target dates successfully."""
        manager = ConfigManager(temp_config_file)
        new_dates = ['2025-03-01', '2025-01-01']  # one new, one duplicate

        success, error, final_dates = manager.add_target_dates(new_dates)
        assert success
        assert error == ""
        assert '2025-03-01' in final_dates
        assert '2025-01-01' in final_dates
        assert '2025-01-02' in final_dates  # original date should still be there
        assert len(final_dates) == 3  # should be deduplicated

    def test_remove_target_dates_success(self, temp_config_file):
        """Test removing target dates successfully."""
        manager = ConfigManager(temp_config_file)
        dates_to_remove = ['2025-01-01']

        success, error, remaining_dates = manager.remove_target_dates(dates_to_remove)
        assert success
        assert error == ""
        assert '2025-01-01' not in remaining_dates
        assert '2025-01-02' in remaining_dates

    def test_clear_target_dates(self, temp_config_file):
        """Test clearing all target dates."""
        manager = ConfigManager(temp_config_file)

        success, error = manager.clear_target_dates()
        assert success
        assert error == ""

        # Verify dates were cleared
        success, error, dates = manager.get_target_dates()
        assert success
        assert dates == []

    def test_get_ifttt_webhook_url_success(self, temp_config_file):
        """Test getting IFTTT webhook URL successfully."""
        manager = ConfigManager(temp_config_file)
        success, error, url = manager.get_ifttt_webhook_url()

        assert success
        assert error == ""
        assert url == 'https://maker.ifttt.com/trigger/test/with/key/test_key'

    def test_get_ifttt_webhook_url_missing(self, empty_config_file):
        """Test getting IFTTT webhook URL when not configured."""
        manager = ConfigManager(empty_config_file)
        success, error, url = manager.get_ifttt_webhook_url()

        assert success
        assert error == ""
        assert url == ""

    def test_set_ifttt_webhook_url_success(self, temp_config_file):
        """Test setting IFTTT webhook URL successfully."""
        manager = ConfigManager(temp_config_file)
        new_url = 'https://maker.ifttt.com/trigger/test/with/key/new_key'

        success, error = manager.set_ifttt_webhook_url(new_url)
        assert success
        assert error == ""

        # Verify URL was set
        success, error, url = manager.get_ifttt_webhook_url()
        assert success
        assert url == new_url

    def test_set_ifttt_webhook_url_invalid(self, temp_config_file):
        """Test setting invalid IFTTT webhook URL."""
        manager = ConfigManager(temp_config_file)
        invalid_url = 'https://example.com/not-ifttt'

        success, error = manager.set_ifttt_webhook_url(invalid_url)
        assert not success
        assert "must be an IFTTT webhook URL" in error

    def test_get_config_status_success(self, temp_config_file):
        """Test getting config status successfully."""
        manager = ConfigManager(temp_config_file)
        success, error, status = manager.get_config_status()

        assert success
        assert error == ""
        assert status['config_file_exists']
        assert status['target_dates_count'] == 2
        assert status['webhook_configured']
        assert 'test_key' in status['webhook_url']

    def test_get_config_status_file_not_found(self):
        """Test getting config status when file doesn't exist."""
        manager = ConfigManager("/path/that/does/not/exist.yaml")
        success, error, status = manager.get_config_status()

        assert not success
        assert "Config file not found" in error
        assert not status['config_file_exists']

    def test_config_preservation(self, temp_config_file):
        """Test that other config sections are preserved when modifying dates."""
        manager = ConfigManager(temp_config_file)

        # Get original config
        success, error, original_config = manager._load_config()
        assert success
        assert original_config is not None
        original_polling = original_config['polling']
        original_webhook_event = original_config['webhook']['event_name']

        # Modify dates
        success, error = manager.set_target_dates(['2025-05-01'])
        assert success

        # Verify other sections are preserved
        success, error, new_config = manager._load_config()
        assert success
        assert new_config is not None
        assert new_config['polling'] == original_polling
        assert new_config['webhook']['event_name'] == original_webhook_event
        assert new_config['target_dates'] == ['2025-05-01']

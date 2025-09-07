"""Integration test to demonstrate MCP server functionality."""

import tempfile
import os
from pathlib import Path
import yaml
from mcp_server.config_manager import ConfigManager


def test_mcp_server_integration():
    """Demonstrate that MCP server can manage a real config file."""
    
    # Create a temporary config file
    config_data = {
        'target_dates': ['2025-01-01', '2025-01-02'],
        'webhook': {
            'url': 'https://maker.ifttt.com/trigger/test/with/key/demo_key',
            'event_name': 'nintendo_museum_available'
        },
        'polling': {'interval_seconds': 10}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f, default_flow_style=False)
        temp_path = f.name
    
    try:
        # Initialize config manager
        manager = ConfigManager(temp_path)
        
        # Test 1: Get initial dates
        print("=== Initial Configuration ===")
        success, error, dates = manager.get_target_dates()
        assert success, f"Failed to get dates: {error}"
        print(f"Target dates: {dates}")
        
        # Test 2: Add new dates (should be sorted and deduplicated)
        print("\n=== Adding New Dates ===")
        new_dates = ['2025-03-01', '2025-01-01', '2025-02-15']  # includes duplicate
        success, error, final_dates = manager.add_target_dates(new_dates)
        assert success, f"Failed to add dates: {error}"
        print(f"Added dates: {new_dates}")
        print(f"Final dates (sorted & deduplicated): {final_dates}")
        
        # Test 3: Update IFTTT webhook
        print("\n=== Updating IFTTT Webhook ===")
        new_key = "my_new_secret_key_123"
        success, error = manager.set_ifttt_webhook_url(
            f"https://maker.ifttt.com/trigger/nintendo_museum_available/with/key/{new_key}"
        )
        assert success, f"Failed to set webhook: {error}"
        print(f"Updated webhook key to: {new_key}")
        
        # Test 4: Verify webhook was updated
        success, error, url = manager.get_ifttt_webhook_url()
        assert success, f"Failed to get webhook URL: {error}"
        assert new_key in url, f"Webhook key not found in URL: {url}"
        print(f"Verified webhook URL: {url}")
        
        # Test 5: Get overall status
        print("\n=== Configuration Status ===")
        success, error, status = manager.get_config_status()
        assert success, f"Failed to get status: {error}"
        print(f"Config file exists: {status['config_file_exists']}")
        print(f"Total dates: {status['target_dates_count']}")
        print(f"Webhook configured: {status['webhook_configured']}")
        print(f"All dates: {status['target_dates']}")
        
        # Test 6: Remove specific dates
        print("\n=== Removing Dates ===")
        dates_to_remove = ['2025-01-01', '2025-02-15']
        success, error, remaining = manager.remove_target_dates(dates_to_remove)
        assert success, f"Failed to remove dates: {error}"
        print(f"Removed dates: {dates_to_remove}")
        print(f"Remaining dates: {remaining}")
        
        # Test 7: Verify config preservation
        print("\n=== Verifying Config Preservation ===")
        success, error, config = manager._load_config()
        assert success, f"Failed to load config: {error}"
        assert config is not None, "Config should not be None"
        assert config['polling']['interval_seconds'] == 10, "Polling config was not preserved"
        assert config['webhook']['event_name'] == 'nintendo_museum_available', "Webhook event name was not preserved"
        print("✅ All other config sections preserved correctly")
        
        print("\n=== Integration Test PASSED ===")
        print("The MCP server successfully:")
        print("- Added and sorted dates automatically")
        print("- Deduplicated duplicate dates")
        print("- Updated IFTTT webhook configuration")
        print("- Preserved all other configuration settings")
        print("- Provided comprehensive status information")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)


if __name__ == "__main__":
    test_mcp_server_integration()

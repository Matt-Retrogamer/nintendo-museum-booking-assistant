"""Configuration file management for Nintendo Museum Booking Assistant."""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from .validators import validate_dates_list, validate_ifttt_webhook_url


class ConfigManager:
    """Manages YAML configuration file operations."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config manager.
        
        Args:
            config_path: Path to config.yaml file. If None, uses default location.
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Default to config.yaml in the project root
            project_root = Path(__file__).parent.parent
            self.config_path = project_root / "config.yaml"
    
    def _load_config(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Load configuration from YAML file.
        
        Returns:
            Tuple of (success, error_message, config_dict)
        """
        if not self.config_path.exists():
            return False, f"Config file not found: {self.config_path}", None
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                if config is None:
                    return False, "Config file is empty or invalid", None
                return True, "", config
        except yaml.YAMLError as e:
            return False, f"YAML parsing error: {e}", None
        except Exception as e:
            return False, f"Error reading config file: {e}", None
    
    def _save_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Save configuration to YAML file.
        
        Args:
            config: Configuration dictionary to save
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Create backup
            backup_path = self.config_path.with_suffix('.yaml.backup')
            if self.config_path.exists():
                self.config_path.rename(backup_path)
            
            # Write new config
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False, sort_keys=False, indent=2)
            
            # Remove backup if successful
            if backup_path.exists():
                backup_path.unlink()
            
            return True, ""
        except Exception as e:
            # Restore backup if it exists
            backup_path = self.config_path.with_suffix('.yaml.backup')
            if backup_path.exists():
                backup_path.rename(self.config_path)
            return False, f"Error saving config file: {e}"
    
    def get_target_dates(self) -> Tuple[bool, str, List[str]]:
        """
        Get current target dates from config.
        
        Returns:
            Tuple of (success, error_message, dates_list)
        """
        success, error, config = self._load_config()
        if not success or config is None:
            return False, error, []
        
        target_dates = config.get('target_dates', [])
        if not isinstance(target_dates, list):
            return False, "target_dates must be a list in config file", []
        
        # Convert to strings and filter out None values
        dates = [str(date) for date in target_dates if date is not None]
        return True, "", dates
    
    def set_target_dates(self, dates: List[str]) -> Tuple[bool, str]:
        """
        Set target dates in config file.
        
        Args:
            dates: List of dates in YYYY-MM-DD format
            
        Returns:
            Tuple of (success, error_message)
        """
        # Validate and process dates
        is_valid, error, processed_dates = validate_dates_list(dates)
        if not is_valid:
            return False, error
        
        # Load current config
        success, error, config = self._load_config()
        if not success or config is None:
            return False, error
        
        # Update target_dates
        config['target_dates'] = processed_dates
        
        # Save config
        return self._save_config(config)
    
    def add_target_dates(self, new_dates: List[str]) -> Tuple[bool, str, List[str]]:
        """
        Add new target dates to existing ones.
        
        Args:
            new_dates: List of new dates to add
            
        Returns:
            Tuple of (success, error_message, final_dates_list)
        """
        # Get current dates
        success, error, current_dates = self.get_target_dates()
        if not success:
            return False, error, []
        
        # Combine and validate
        all_dates = current_dates + new_dates
        is_valid, error, processed_dates = validate_dates_list(all_dates)
        if not is_valid:
            return False, error, []
        
        # Save updated dates
        success, error = self.set_target_dates(processed_dates)
        if not success:
            return False, error, []
        
        return True, "", processed_dates
    
    def remove_target_dates(self, dates_to_remove: List[str]) -> Tuple[bool, str, List[str]]:
        """
        Remove specific target dates.
        
        Args:
            dates_to_remove: List of dates to remove
            
        Returns:
            Tuple of (success, error_message, remaining_dates_list)
        """
        # Get current dates
        success, error, current_dates = self.get_target_dates()
        if not success:
            return False, error, []
        
        # Remove specified dates
        remaining_dates = [date for date in current_dates if date not in dates_to_remove]
        
        # Validate and save
        success, error = self.set_target_dates(remaining_dates)
        if not success:
            return False, error, []
        
        return True, "", remaining_dates
    
    def clear_target_dates(self) -> Tuple[bool, str]:
        """
        Clear all target dates.
        
        Returns:
            Tuple of (success, error_message)
        """
        return self.set_target_dates([])
    
    def get_ifttt_webhook_url(self) -> Tuple[bool, str, str]:
        """
        Get current IFTTT webhook URL from config.
        
        Returns:
            Tuple of (success, error_message, webhook_url)
        """
        success, error, config = self._load_config()
        if not success or config is None:
            return False, error, ""
        
        webhook_config = config.get('webhook', {})
        if not isinstance(webhook_config, dict):
            return False, "webhook section must be a dictionary in config file", ""
        
        url = webhook_config.get('url', '')
        return True, "", str(url)
    
    def set_ifttt_webhook_url(self, url: str) -> Tuple[bool, str]:
        """
        Set IFTTT webhook URL in config file.
        
        Args:
            url: The webhook URL to set
            
        Returns:
            Tuple of (success, error_message)
        """
        # Validate URL
        is_valid, error = validate_ifttt_webhook_url(url)
        if not is_valid:
            return False, error
        
        # Load current config
        success, error, config = self._load_config()
        if not success or config is None:
            return False, error
        
        # Ensure webhook section exists
        if 'webhook' not in config:
            config['webhook'] = {}
        
        # Update URL
        config['webhook']['url'] = url
        
        # Save config
        return self._save_config(config)
    
    def get_config_status(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Get current configuration status.
        
        Returns:
            Tuple of (success, error_message, status_dict)
        """
        status = {
            'config_file_exists': self.config_path.exists(),
            'config_file_path': str(self.config_path),
            'target_dates': [],
            'target_dates_count': 0,
            'webhook_url': '',
            'webhook_configured': False
        }
        
        if not status['config_file_exists']:
            return False, f"Config file not found: {self.config_path}", status
        
        # Get target dates
        success, error, dates = self.get_target_dates()
        if success:
            status['target_dates'] = dates
            status['target_dates_count'] = len(dates)
        else:
            return False, f"Error reading target dates: {error}", status
        
        # Get webhook URL
        success, error, url = self.get_ifttt_webhook_url()
        if success:
            status['webhook_url'] = url
            status['webhook_configured'] = url and 'YOUR_IFTTT_KEY' not in url
        else:
            return False, f"Error reading webhook URL: {error}", status
        
        return True, "", status

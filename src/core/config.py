"""
Configuration management for the Musical Loop Generation Application.
Handles loading and accessing application configuration from JSON files.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

class Config:
    """
    Configuration manager for the application.
    
    Handles loading configuration from JSON files and provides
    a unified interface for accessing configuration values.
    """
    
    def __init__(self, config_path: str = "config/app_config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = Path(config_path)
        self.config_data: Dict[str, Any] = {}
        
        self.load_config()
    
    def load_config(self) -> bool:
        """
        Load configuration from the JSON file.
        
        Returns:
            bool: True if configuration was loaded successfully, False otherwise
        """
        try:
            if not self.config_path.exists():
                self.logger.error(f"Configuration file not found: {self.config_path}")
                return False
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            
            self.logger.info(f"Configuration loaded from {self.config_path}")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in configuration file {self.config_path}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to load configuration from {self.config_path}: {str(e)}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the configuration value (e.g., "api_keys.suno")
            default: Default value to return if the key is not found
            
        Returns:
            The configuration value or default if not found
        """
        try:
            keys = key_path.split('.')
            value: Any = self.config_data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.warning(f"Error accessing config key '{key_path}': {str(e)}")
            return default
    
    def get_api_key(self, api_name: str) -> Optional[str]:
        """
        Get an API key for a specific service.
        
        Args:
            api_name: Name of the API service (suno, udio, stable_audio)
            
        Returns:
            API key string if found and non-empty, None otherwise
        """
        key = self.get(f"api_keys.{api_name}")
        if key and str(key).strip():
            return str(key).strip()
        return None
    
    def get_api_endpoint(self, api_name: str) -> Optional[str]:
        """
        Get the API endpoint URL for a specific service.
        
        Args:
            api_name: Name of the API service (suno, udio, stable_audio)
            
        Returns:
            API endpoint URL if found, None otherwise
        """
        return self.get(f"api_endpoints.{api_name}")
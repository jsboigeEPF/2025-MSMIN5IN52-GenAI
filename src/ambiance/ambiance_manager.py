"""
AmbianceManager class for handling ambiance configurations in the musical loop generation application.
Manages loading, validation, and retrieval of ambiance profiles from configuration files.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

class AmbianceManager:
    """
    Manages ambiance configurations for the musical loop generation application.
    
    This class handles loading ambiance profiles from JSON files, validating their structure,
    and providing methods to retrieve ambiance-specific settings for audio generation.
    It supports easy addition of new ambiance types by simply adding new configuration files.
    
    The ambiance configurations are stored in JSON files within the config/ambiances/ directory
    and define parameters such as tempo, instruments, effects, and other audio generation settings.
    """
    
    # Define the required structure for ambiance configurations
    REQUIRED_KEYS = {
        'tempo': int,
        'instruments': list,
        'effects_chain': list
    }
    
    REQUIRED_INSTRUMENT_KEYS = {
        'name': str,
        'volume': (int, float),
        'effects': list,
        'pattern': str
    }
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the AmbianceManager.
        
        Args:
            config_dir: Optional path to the directory containing ambiance configuration files.
                       If not provided, uses the default from app_config.json
        """
        self.logger = logging.getLogger(__name__)
        self.ambiance_configs: Dict[str, Dict[str, Any]] = {}
        
        # Use provided config directory or default from app config
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Default path based on project structure
            self.config_dir = Path(__file__).parent.parent.parent / "assets" / "ambiance_configs"
        
        self.logger.info(f"AmbianceManager initialized with config directory: {self.config_dir}")
        
        # Load all ambiance configurations
        self._load_all_configs()
    
    def _load_all_configs(self) -> None:
        """
        Load all ambiance configuration files from the config directory.
        """
        if not self.config_dir.exists():
            self.logger.error(f"Configuration directory does not exist: {self.config_dir}")
            return
        
        # Find all JSON files in the config directory
        config_files = list(self.config_dir.glob("*.json"))
        self.logger.info(f"Found {len(config_files)} ambiance configuration files")
        
        for config_file in config_files:
            try:
                ambiance_name = config_file.stem  # Use filename without extension as ambiance name
                config_data = self._load_config_file(config_file)
                
                if config_data:
                    # Validate the configuration
                    if self._validate_config(config_data, ambiance_name):
                        self.ambiance_configs[ambiance_name] = config_data
                        self.logger.info(f"Successfully loaded ambiance configuration: {ambiance_name}")
                    else:
                        self.logger.warning(f"Invalid configuration for ambiance: {ambiance_name}")
                else:
                    self.logger.warning(f"Failed to load configuration from file: {config_file}")
                    
            except Exception as e:
                self.logger.error(f"Error loading ambiance configuration from {config_file}: {str(e)}")
    
    def _load_config_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load a single ambiance configuration file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Dictionary containing the configuration data, or None if loading failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                return config_data
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in ambiance configuration file {file_path}: {str(e)}")
        except FileNotFoundError:
            self.logger.error(f"Ambiance configuration file not found: {file_path}")
        except Exception as e:
            self.logger.error(f"Error reading ambiance configuration file {file_path}: {str(e)}")
        
        return None
    
    def _validate_config(self, config: Dict[str, Any], ambiance_name: str) -> bool:
        """
        Validate the structure of an ambiance configuration.
        
        Args:
            config: The configuration dictionary to validate
            ambiance_name: Name of the ambiance (for logging purposes)
            
        Returns:
            True if the configuration is valid, False otherwise
        """
        # Check for required top-level keys
        for key, expected_type in self.REQUIRED_KEYS.items():
            if key not in config:
                self.logger.error(f"Missing required key '{key}' in ambiance configuration: {ambiance_name}")
                return False
                
            if not isinstance(config[key], expected_type):
                self.logger.error(f"Key '{key}' has incorrect type in ambiance configuration: {ambiance_name}. "
                                f"Expected {expected_type}, got {type(config[key])}")
                return False
        
        # Validate instruments
        for i, instrument in enumerate(config['instruments']):
            if not isinstance(instrument, dict):
                self.logger.error(f"Instrument at index {i} is not an object in ambiance: {ambiance_name}")
                return False
                
            for key, expected_type in self.REQUIRED_INSTRUMENT_KEYS.items():
                if key not in instrument:
                    self.logger.error(f"Missing required instrument key '{key}' in ambiance: {ambiance_name}")
                    return False
                    
                if not isinstance(instrument[key], expected_type):
                    self.logger.error(f"Instrument key '{key}' has incorrect type in ambiance: {ambiance_name}. "
                                    f"Expected {expected_type}, got {type(instrument[key])}")
                    return False
        
        return True
    
    def get_ambiance_config(self, ambiance_type: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the configuration for a specific ambiance type.
        
        Args:
            ambiance_type: The name of the ambiance type (e.g., 'mysterious_forest')
            
        Returns:
            Dictionary containing the ambiance configuration, or None if not found
        """
        config = self.ambiance_configs.get(ambiance_type)
        if config is None:
            self.logger.warning(f"Ambiance configuration not found for type: {ambiance_type}")
            return None
            
        return config.copy()  # Return a copy to prevent modification of internal data
    
    def get_available_ambiances(self) -> list:
        """
        Get a list of all available ambiance types.
        
        Returns:
            List of ambiance type names
        """
        return list(self.ambiance_configs.keys())
    
    def is_ambiance_supported(self, ambiance_type: str) -> bool:
        """
        Check if a specific ambiance type is supported.
        
        Args:
            ambiance_type: The name of the ambiance type to check
            
        Returns:
            True if the ambiance type is supported, False otherwise
        """
        return ambiance_type in self.ambiance_configs
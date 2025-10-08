import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import logging
from src.ambiance.ambiance_manager import AmbianceManager

class TestAmbianceManager(unittest.TestCase):
    """Test cases for AmbianceManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test configuration files
        self.test_dir = tempfile.mkdtemp()
        
        # Create test ambiance configuration files
        self.create_test_config_files()
        
        # Initialize AmbianceManager with the test directory
        self.manager = AmbianceManager(self.test_dir)
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        # Remove the temporary directory and all its contents
        shutil.rmtree(self.test_dir)
    
    def create_test_config_files(self):
        """Create test ambiance configuration files in the temporary directory."""
        # Valid configuration
        valid_config = {
            "tempo": 72,
            "instruments": [
                {
                    "name": "test_instrument",
                    "volume": -6,
                    "effects": ["reverb", "delay"],
                    "pattern": "random_interval"
                }
            ],
            "effects_chain": ["reverb", "delay"],
            "description": "Test ambiance description"
        }
        
        # Invalid configuration (missing required key)
        invalid_config = {
            "instruments": [
                {
                    "name": "test_instrument",
                    "volume": -6,
                    "effects": ["reverb", "delay"],
                    "pattern": "random_interval"
                }
            ],
            "effects_chain": ["reverb", "delay"]
        }
        
        # Configuration with invalid instrument type
        invalid_instrument_config = {
            "tempo": 72,
            "instruments": [
                "not_an_object"  # Should be a dictionary
            ],
            "effects_chain": ["reverb", "delay"]
        }
        
        # Configuration with instrument missing required key
        missing_instrument_key_config = {
            "tempo": 72,
            "instruments": [
                {
                    "name": "test_instrument",
                    "volume": -6,
                    "effects": ["reverb", "delay"]
                    # Missing 'pattern' key
                }
            ],
            "effects_chain": ["reverb", "delay"]
        }
        
        # Configuration with instrument key of wrong type
        wrong_instrument_type_config = {
            "tempo": 72,
            "instruments": [
                {
                    "name": "test_instrument",
                    "volume": "not_a_number",  # Should be int or float
                    "effects": ["reverb", "delay"],
                    "pattern": "random_interval"
                }
            ],
            "effects_chain": ["reverb", "delay"]
        }
        
        # Write configuration files
        with open(os.path.join(self.test_dir, "valid.json"), 'w') as f:
            json.dump(valid_config, f)
        
        with open(os.path.join(self.test_dir, "invalid.json"), 'w') as f:
            json.dump(invalid_config, f)
        
        with open(os.path.join(self.test_dir, "invalid_instrument.json"), 'w') as f:
            json.dump(invalid_instrument_config, f)
        
        with open(os.path.join(self.test_dir, "missing_instrument_key.json"), 'w') as f:
            json.dump(missing_instrument_key_config, f)
        
        with open(os.path.join(self.test_dir, "wrong_instrument_type.json"), 'w') as f:
            json.dump(wrong_instrument_type_config, f)
        
        # Create a non-JSON file to test file filtering
        with open(os.path.join(self.test_dir, "not_a_json.txt"), 'w') as f:
            f.write("This is not a JSON file")
    
    def test_initialization_with_custom_directory(self):
        """Test that AmbianceManager initializes with a custom directory."""
        manager = AmbianceManager(self.test_dir)
        self.assertEqual(manager.config_dir, Path(self.test_dir))
    
    def test_initialization_with_default_directory(self):
        """Test that AmbianceManager initializes with the default directory when none is provided."""
        with patch('src.ambiance.ambiance_manager.Path') as mock_path:
            # Mock the default path calculation
            mock_path.return_value = Path('assets/ambiance_configs')
            
            manager = AmbianceManager()
            self.assertEqual(manager.config_dir, Path('assets/ambiance_configs'))
    
    @patch('src.ambiance.ambiance_manager.Path')
    def test_initialization_logs_directory(self, mock_path):
        """Test that AmbianceManager logs the configuration directory on initialization."""
        with patch('src.ambiance.ambiance_manager.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            mock_path.return_value = Path(self.test_dir)
            
            manager = AmbianceManager(self.test_dir)
            
            # Verify logger.info was called with the correct message
            mock_logger.info.assert_any_call(f"AmbianceManager initialized with config directory: {self.test_dir}")
    
    def test_load_all_configs_directory_does_not_exist(self):
        """Test that _load_all_configs handles non-existent directory."""
        with patch('src.ambiance.ambiance_manager.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            # Create manager with non-existent directory
            manager = AmbianceManager("/non/existent/directory")
            
            # Verify error was logged
            # Use assert_any_call to be more flexible with path separators
            self.assertTrue(any("Configuration directory does not exist" in str(call[0][0]) for call in mock_logger.error.call_args_list), "Error was not logged when directory does not exist")
    
    def test_load_all_configs_finds_json_files(self):
        """Test that _load_all_configs finds and loads JSON files in the directory."""
        with patch('src.ambiance.ambiance_manager.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            # Create manager with test directory
            manager = AmbianceManager(self.test_dir)
            
            # Verify info message about found files
            mock_logger.info.assert_any_call(f"Found 5 ambiance configuration files")
    
    def test_load_all_configs_ignores_non_json_files(self):
        """Test that _load_all_configs ignores non-JSON files."""
        # Create a non-JSON file
        non_json_file = os.path.join(self.test_dir, "test.txt")
        with open(non_json_file, 'w') as f:
            f.write("This is not a JSON file")
        
        # Create manager
        manager = AmbianceManager(self.test_dir)
        
        # The non-JSON file should be ignored, so we should still have the same number of configs
        # as before (5 JSON files)
        self.assertEqual(len(manager.ambiance_configs), 5)
    
    def test_load_config_file_success(self):
        """Test that _load_config_file successfully loads a valid JSON file."""
        # Create a test file
        test_file = Path(self.test_dir) / "test.json"
        test_data = {"tempo": 72, "instruments": [], "effects_chain": []}
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Test load_config_file
        result = self.manager._load_config_file(test_file)
        
        self.assertEqual(result, test_data)
    
    def test_load_config_file_invalid_json(self):
        """Test that _load_config_file handles invalid JSON."""
        # Create a file with invalid JSON
        test_file = Path(self.test_dir) / "invalid.json"
        with open(test_file, 'w') as f:
            f.write("This is not valid JSON")
        
        with patch('src.ambiance.ambiance_manager.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            result = self.manager._load_config_file(test_file)
            
            self.assertIsNone(result)
            # Verify error was logged
            self.assertTrue(mock_logger.error.called, "Error was not logged when JSON is invalid")
            # Check that the error message contains the expected text
            error_calls = mock_logger.error.call_args_list
            self.assertTrue(len(error_calls) > 0, "Error should have been called at least once")
            error_message = str(error_calls[0][0][0])
            self.assertIn("Invalid JSON in ambiance configuration file", error_message, "Error message should contain 'Invalid JSON'")
            self.assertIn("invalid.json", error_message, "Error message should contain the filename")
            self.assertIn("Expecting value", error_message, "Error message should contain the JSON error")
            error_call = mock_logger.error.call_args
            self.assertIsNotNone(error_call)
            error_message = str(error_call[0][0])
            self.assertIn("Invalid JSON in ambiance configuration file", error_message)
            self.assertIn("Expecting value", error_message)
    
    def test_load_config_file_file_not_found(self):
        """Test that _load_config_file handles file not found."""
        # Use a non-existent file path
        test_file = Path(self.test_dir) / "non_existent.json"
        
        with patch('src.ambiance.ambiance_manager.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            result = self.manager._load_config_file(test_file)
            
            self.assertIsNone(result)
            # Verify error was logged
            self.assertTrue(mock_logger.error.called, "Error was not logged when file is not found")
            # Check that the error message contains the expected text
            error_calls = mock_logger.error.call_args_list
            self.assertTrue(len(error_calls) > 0, "Error should have been called at least once")
            error_message = str(error_calls[0][0][0])
            self.assertIn("Ambiance configuration file not found", error_message, "Error message should contain 'Ambiance configuration file not found'")
            self.assertIn("non_existent.json", error_message, "Error message should contain the filename")
            error_call = mock_logger.error.call_args
            self.assertIsNotNone(error_call)
            error_message = str(error_call[0][0])
            self.assertIn("Ambiance configuration file not found", error_message)
            self.assertIn("non_existent.json", error_message)
    
    def test_load_config_file_other_error(self):
        """Test that _load_config_file handles other errors (e.g., permission denied)."""
        # This is tricky to test as we can't easily create a permission denied error
        # Instead, we'll patch the open function to raise an exception
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with patch('src.ambiance.ambiance_manager.logging.getLogger') as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger
                
                test_file = Path(self.test_dir) / "test.json"
                result = self.manager._load_config_file(test_file)
                
                self.assertIsNone(result)
                # Verify error was logged
                self.assertTrue(mock_logger.error.called, "Error was not logged when there is a permission error")
                # Check that the error message contains the expected text
                error_calls = mock_logger.error.call_args_list
                self.assertTrue(len(error_calls) > 0, "Error should have been called at least once")
                error_message = str(error_calls[0][0][0])
                self.assertIn("Error reading ambiance configuration file", error_message, "Error message should contain 'Error reading ambiance configuration file'")
                self.assertIn("test.json", error_message, "Error message should contain the filename")
                self.assertIn("Permission denied", error_message, "Error message should contain the permission error")
                error_call = mock_logger.error.call_args
                self.assertIsNotNone(error_call)
                error_message = str(error_call[0][0])
                self.assertIn("Error reading ambiance configuration file", error_message)
                self.assertIn("Permission denied", error_message)
    
    def test_validate_config_valid(self):
        """Test that _validate_config returns True for valid configuration."""
        valid_config = {
            "tempo": 72,
            "instruments": [
                {
                    "name": "test_instrument",
                    "volume": -6,
                    "effects": ["reverb", "delay"],
                    "pattern": "random_interval"
                }
            ],
            "effects_chain": ["reverb", "delay"]
        }
        
        result = self.manager._validate_config(valid_config, "test_ambiance")
        self.assertTrue(result)
    
    def test_validate_config_missing_required_key(self):
        """Test that _validate_config returns False when a required key is missing."""
        # Missing 'tempo' key
        config = {
            "instruments": [
                {
                    "name": "test_instrument",
                    "volume": -6,
                    "effects": ["reverb", "delay"],
                    "pattern": "random_interval"
                }
            ],
            "effects_chain": ["reverb", "delay"]
        }
        
        with patch('src.ambiance.ambiance_manager.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            result = self.manager._validate_config(config, "test_ambiance")
            
            self.assertFalse(result)
            # Verify error was logged
            self.assertTrue(mock_logger.error.called, "Error was not logged when required key is missing")
            # Check that the error message contains the expected text
            error_calls = mock_logger.error.call_args_list
            self.assertTrue(len(error_calls) > 0, "Error should have been called at least once")
            error_message = str(error_calls[0][0][0])
            self.assertIn("Missing required key 'tempo'", error_message, "Error message should contain 'Missing required key'")
            self.assertIn("test_ambiance", error_message, "Error message should contain the ambiance type")
            error_call = mock_logger.error.call_args
            self.assertIsNotNone(error_call)
            error_message = str(error_call[0][0])
            self.assertIn("Missing required key 'tempo'", error_message)
            self.assertIn("test_ambiance", error_message)
    
    def test_validate_config_wrong_type_for_required_key(self):
        """Test that _validate_config returns False when a required key has the wrong type."""
        # 'tempo' should be an integer
        config = {
            "tempo": "not_a_number",
            "instruments": [
                {
                    "name": "test_instrument",
                    "volume": -6,
                    "effects": ["reverb", "delay"],
                    "pattern": "random_interval"
                }
            ],
            "effects_chain": ["reverb", "delay"]
        }
        
        with patch('src.ambiance.ambiance_manager.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            result = self.manager._validate_config(config, "test_ambiance")
            
            self.assertFalse(result)
            # Verify error was logged
            self.assertTrue(mock_logger.error.called, "Error was not logged when key has incorrect type")
            # Check that the error message contains the expected text
            error_calls = mock_logger.error.call_args_list
            self.assertTrue(len(error_calls) > 0, "Error should have been called at least once")
            error_message = str(error_calls[0][0][0])
            self.assertIn("Key 'tempo' has incorrect type", error_message, "Error message should contain 'Key has incorrect type'")
            self.assertIn("test_ambiance", error_message, "Error message should contain the ambiance type")
            self.assertIn("Expected <class 'int'>", error_message, "Error message should contain expected type")
            self.assertIn("got <class 'str'>", error_message, "Error message should contain actual type")
            error_call = mock_logger.error.call_args
            self.assertIsNotNone(error_call)
            error_message = str(error_call[0][0])
            self.assertIn("Key 'tempo' has incorrect type", error_message)
            self.assertIn("test_ambiance", error_message)
            self.assertIn("Expected <class 'int'>", error_message)
            self.assertIn("got <class 'str'>", error_message)
    
    def test_validate_config_instrument_not_object(self):
        """Test that _validate_config returns False when an instrument is not an object."""
        config = {
            "tempo": 72,
            "instruments": [
                "not_an_object"  # Should be a dictionary
            ],
            "effects_chain": ["reverb", "delay"]
        }
        
        with patch('src.ambiance.ambiance_manager.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            result = self.manager._validate_config(config, "test_ambiance")
            
            self.assertFalse(result)
            # Verify error was logged
            self.assertTrue(mock_logger.error.called, "Error was not logged when instrument is not an object")
            # Check that the error message contains the expected text
            error_calls = mock_logger.error.call_args_list
            self.assertTrue(len(error_calls) > 0, "Error should have been called at least once")
            error_message = str(error_calls[0][0][0])
            self.assertIn("Instrument at index 0 is not an object", error_message, "Error message should contain 'Instrument at index'")
            self.assertIn("test_ambiance", error_message, "Error message should contain the ambiance type")
            error_call = mock_logger.error.call_args
            self.assertIsNotNone(error_call)
            error_message = str(error_call[0][0])
            self.assertIn("Instrument at index 0 is not an object", error_message)
            self.assertIn("test_ambiance", error_message)
    
    def test_validate_config_instrument_missing_required_key(self):
        """Test that _validate_config returns False when an instrument is missing a required key."""
        config = {
            "tempo": 72,
            "instruments": [
                {
                    "name": "test_instrument",
                    "volume": -6,
                    "effects": ["reverb", "delay"]
                    # Missing 'pattern' key
                }
            ],
            "effects_chain": ["reverb", "delay"]
        }
        
        with patch('src.ambiance.ambiance_manager.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            result = self.manager._validate_config(config, "test_ambiance")
            
            self.assertFalse(result)
            # Verify error was logged
            self.assertTrue(mock_logger.error.called, "Error was not logged when instrument is missing required key")
            # Check that the error message contains the expected text
            error_calls = mock_logger.error.call_args_list
            self.assertTrue(len(error_calls) > 0, "Error should have been called at least once")
            error_message = str(error_calls[0][0][0])
            self.assertIn("Missing required instrument key 'pattern'", error_message, "Error message should contain 'Missing required instrument key'")
            self.assertIn("test_ambiance", error_message, "Error message should contain the ambiance type")
            error_call = mock_logger.error.call_args
            self.assertIsNotNone(error_call)
            error_message = str(error_call[0][0])
            self.assertIn("Missing required instrument key 'pattern'", error_message)
            self.assertIn("test_ambiance", error_message)
    
    def test_validate_config_instrument_wrong_type_for_required_key(self):
        """Test that _validate_config returns False when an instrument key has the wrong type."""
        config = {
            "tempo": 72,
            "instruments": [
                {
                    "name": "test_instrument",
                    "volume": "not_a_number",  # Should be int or float
                    "effects": ["reverb", "delay"],
                    "pattern": "random_interval"
                }
            ],
            "effects_chain": ["reverb", "delay"]
        }
        
        with patch('src.ambiance.ambiance_manager.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            result = self.manager._validate_config(config, "test_ambiance")
            
            self.assertFalse(result)
            # Verify error was logged
            self.assertTrue(mock_logger.error.called, "Error was not logged when instrument key has incorrect type")
            # Check that the error message contains the expected text
            error_call = mock_logger.error.call_args
            self.assertIsNotNone(error_call, "Error call should not be None")
            error_message = str(error_call[0][0])
            self.assertIn("Instrument key 'volume' has incorrect type", error_message, "Error message should contain 'Instrument key has incorrect type'")
            self.assertIn("test_ambiance", error_message, "Error message should contain the ambiance type")
            self.assertIn("Expected (<class 'int'>, <class 'float'>)", error_message, "Error message should contain expected types")
            self.assertIn("got <class 'str'>", error_message, "Error message should contain actual type")
            error_call = mock_logger.error.call_args
            self.assertIsNotNone(error_call)
            error_message = str(error_call[0][0])
            self.assertIn("Instrument key 'volume' has incorrect type", error_message)
            self.assertIn("test_ambiance", error_message)
            self.assertIn("Expected (<class 'int'>, <class 'float'>)", error_message)
            self.assertIn("got <class 'str'>", error_message)
    
    def test_load_all_configs_loads_valid_configs(self):
        """Test that _load_all_configs loads valid configuration files."""
        # Create a valid config file
        valid_config = {
            "tempo": 72,
            "instruments": [
                {
                    "name": "test_instrument",
                    "volume": -6,
                    "effects": ["reverb", "delay"],
                    "pattern": "random_interval"
                }
            ],
            "effects_chain": ["reverb", "delay"]
        }
        
        with open(os.path.join(self.test_dir, "valid.json"), 'w') as f:
            json.dump(valid_config, f)
        
        # Create manager
        manager = AmbianceManager(self.test_dir)
        
        # Verify the valid config was loaded
        self.assertIn("valid", manager.ambiance_configs)
        self.assertEqual(manager.ambiance_configs["valid"]["tempo"], 72)
    
    def test_load_all_configs_skips_invalid_configs(self):
        """Test that _load_all_configs skips invalid configuration files."""
        # Create an invalid config file (missing required key)
        invalid_config = {
            "instruments": [
                {
                    "name": "test_instrument",
                    "volume": -6,
                    "effects": ["reverb", "delay"],
                    "pattern": "random_interval"
                }
            ],
            "effects_chain": ["reverb", "delay"]
        }
        
        with open(os.path.join(self.test_dir, "invalid.json"), 'w') as f:
            json.dump(invalid_config, f)
        
        # Create manager
        manager = AmbianceManager(self.test_dir)
        
        # Verify the invalid config was not loaded
        self.assertNotIn("invalid", manager.ambiance_configs)
    
    def test_load_all_configs_logs_load_status(self):
        """Test that _load_all_configs logs the status of loading configuration files."""
        with patch('src.ambiance.ambiance_manager.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            # Create manager
            manager = AmbianceManager(self.test_dir)
            
            # Verify log messages for successful and failed loads
            mock_logger.info.assert_any_call("Successfully loaded ambiance configuration: valid")
            mock_logger.warning.assert_any_call("Invalid configuration for ambiance: invalid")
            # We can't easily test the exact message for failed loads since the filename will have a temp path
            self.assertTrue(any("Failed to load configuration from file" in str(call[0][0]) for call in mock_logger.warning.call_args_list), "Warning was not logged for failed configuration loads")
    
    def test_get_ambiance_config_returns_config(self):
        """Test that get_ambiance_config returns the correct configuration."""
        # Create a test config
        test_config = {
            "tempo": 72,
            "instruments": [
                {
                    "name": "test_instrument",
                    "volume": -6,
                    "effects": ["reverb", "delay"],
                    "pattern": "random_interval"
                }
            ],
            "effects_chain": ["reverb", "delay"]
        }
        
        # Add to manager's configs
        self.manager.ambiance_configs["test"] = test_config
        
        # Test get_ambiance_config
        result = self.manager.get_ambiance_config("test")
        
        self.assertEqual(result, test_config)
    
    def test_get_ambiance_config_returns_none_for_missing(self):
        """Test that get_ambiance_config returns None for missing ambiance type."""
        with patch('src.ambiance.ambiance_manager.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            result = self.manager.get_ambiance_config("missing")
            
            self.assertIsNone(result)
            # We can't easily test the exact message since it will have a temp path
            self.assertTrue(any("Ambiance configuration not found for type: missing" in str(call[0][0]) for call in mock_logger.warning.call_args_list), "Warning was not logged when ambiance configuration is not found")
    
    def test_get_ambiance_config_returns_copy(self):
        """Test that get_ambiance_config returns a copy of the configuration."""
        # Create a test config
        test_config = {
            "tempo": 72,
            "instruments": [
                {
                    "name": "test_instrument",
                    "volume": -6,
                    "effects": ["reverb", "delay"],
                    "pattern": "random_interval"
                }
            ],
            "effects_chain": ["reverb", "delay"]
        }
        
        # Add to manager's configs
        self.manager.ambiance_configs["test"] = test_config
        
        # Get the config
        result = self.manager.get_ambiance_config("test")
        
        # Modify the returned config
        result["tempo"] = 120
        
        # Verify the original config is unchanged
        self.assertEqual(self.manager.ambiance_configs["test"]["tempo"], 72)
    
    def test_get_available_ambiances(self):
        """Test that get_available_ambiances returns a list of available ambiance types."""
        # Add some test configs
        self.manager.ambiance_configs["test1"] = {"tempo": 72, "instruments": [], "effects_chain": []}
        self.manager.ambiance_configs["test2"] = {"tempo": 72, "instruments": [], "effects_chain": []}
        
        # Test get_available_ambiances
        result = self.manager.get_available_ambiances()
        
        self.assertIsInstance(result, list)
        self.assertIn("test1", result)
        self.assertIn("test2", result)
        # We added two configs, so we should have at least 2
        self.assertGreaterEqual(len(result), 2)
        self.assertIn("test1", result)
        self.assertIn("test2", result)
    
    def test_is_ambiance_supported(self):
        """Test that is_ambiance_supported correctly identifies supported ambiances."""
        # Add a test config
        self.manager.ambiance_configs["test"] = {"tempo": 72, "instruments": [], "effects_chain": []}
        
        # Test is_ambiance_supported
        self.assertTrue(self.manager.is_ambiance_supported("test"))
        self.assertFalse(self.manager.is_ambiance_supported("missing"))
    
    def test_initialization_loads_configs(self):
        """Test that initialization automatically loads all configuration files."""
        # The manager was initialized in setUp with the test directory
        # Verify that valid configs were loaded
        self.assertIn("valid", self.manager.ambiance_configs)
        
        # Verify that invalid configs were not loaded
        self.assertNotIn("invalid", self.manager.ambiance_configs)
        self.assertNotIn("invalid_instrument", self.manager.ambiance_configs)
        self.assertNotIn("missing_instrument_key", self.manager.ambiance_configs)
        self.assertNotIn("wrong_instrument_type", self.manager.ambiance_configs)

if __name__ == '__main__':
    unittest.main()
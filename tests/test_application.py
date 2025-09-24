import unittest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from src.core.application import Application
from src.ambiance.ambiance_manager import AmbianceManager
from src.audio.generation_service import AudioGenerationService

class TestApplication(unittest.TestCase):
    """Test cases for Application class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a mock configuration for testing
        self.config = {
            'api': {
                'base_url': 'http://localhost:8000',
                'timeout': 30
            },
            'cache': {
                'enabled': True,
                'directory': 'cache/audio',
                'ttl': 3600
            },
            'api_endpoints': {
                'suno': 'https://api.suno.ai/v1/music',
                'udio': 'https://api.udio.com/v1/generate',
                'stable_audio': 'https://api.stableaudio.com/v1/sound'
            },
            'api_keys': {
                'suno': 'test_suno_key',
                'udio': 'test_udio_key',
                'stable_audio': 'test_stable_audio_key'
            },
            'audio': {
                'loop_duration': 30,
                'max_concurrent_requests': 3
            }
        }
    
    def test_initialization(self):
        """Test that the application initializes correctly."""
        with patch('src.core.application.AmbianceManager') as mock_ambiance_manager, \
             patch('src.core.application.AudioGenerationService') as mock_audio_generator, \
             patch('src.core.application.UserInterface') as mock_user_interface:
            
            # Create mocks for the components
            mock_ambiance_manager.return_value = Mock(spec=AmbianceManager)
            mock_audio_generator.return_value = Mock(spec=AudioGenerationService)
            mock_user_interface.return_value = Mock()
            
            # Initialize the application
            app = Application()
            
            # Verify that the components were initialized
            mock_ambiance_manager.assert_called_once()
            mock_audio_generator.assert_called_once()
            mock_user_interface.assert_called_once()
            
            # Verify application state
            self.assertFalse(app.is_running)
            self.assertIsNotNone(app.logger)
    
    @patch('src.core.application.AmbianceManager')
    @patch('src.core.application.AudioGenerationService')
    @patch('src.core.application.UserInterface')
    def test_initialization_logs_component_initialization(self, mock_user_interface, mock_audio_generator, mock_ambiance_manager):
        """Test that initialization logs component initialization."""
        with patch('src.core.application.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            # Create mocks for the components
            mock_ambiance_manager.return_value = Mock(spec=AmbianceManager)
            mock_audio_generator.return_value = Mock(spec=AudioGenerationService)
            mock_user_interface.return_value = Mock()
            
            # Initialize the application
            app = Application()
            
            # Verify log messages
            mock_logger.info.assert_any_call("Initializing application components...")
            mock_logger.info.assert_any_call("Ambiance manager initialized")
            mock_logger.info.assert_any_call("Audio generation service initialized with Suno, Udio, and Stable Audio APIs")
            mock_logger.info.assert_any_call("User interface initialized")
            mock_logger.info.assert_any_call("All components initialized successfully")
    
    @patch('src.core.application.AmbianceManager')
    @patch('src.core.application.AudioGenerationService')
    @patch('src.core.application.UserInterface')
    def test_initialization_with_component_failure(self, mock_user_interface, mock_audio_generator, mock_ambiance_manager):
        """Test that initialization raises an exception if a component fails to initialize."""
        with patch('src.core.application.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            # Make one component initialization fail
            mock_ambiance_manager.side_effect = Exception("Ambiance manager initialization failed")
            
            # Test that initialization raises an exception
            with self.assertRaises(Exception) as context:
                app = Application()
            
            self.assertIn("Ambiance manager initialization failed", str(context.exception))
            mock_logger.error.assert_called_with("Failed to initialize components: Ambiance manager initialization failed")
    
    @patch('src.core.application.AmbianceManager')
    @patch('src.core.application.AudioGenerationService')
    @patch('src.core.application.UserInterface')
    def test_run_initializes_components(self, mock_user_interface, mock_audio_generator, mock_ambiance_manager):
        """Test that run method initializes components if they haven't been initialized."""
        with patch.object(Application, '_initialize_components') as mock_init:
            # Create application without initializing components
            app = Application()
            app.ambiance_manager = None
            app.audio_generator = None
            app.user_interface = None
            
            # Mock the run method to exit immediately
            with patch.object(app, 'is_running', False):
                asyncio.run(app.run())
            
            # Verify that _initialize_components was called
            mock_init.assert_called_once()
    
    @patch('src.core.application.AmbianceManager')
    @patch('src.core.application.AudioGenerationService')
    @patch('src.core.application.UserInterface')
    def test_run_starts_application(self, mock_user_interface, mock_audio_generator, mock_ambiance_manager):
        """Test that run method starts the application."""
        # Create mocks for the components
        mock_ambiance_manager.return_value = Mock(spec=AmbianceManager)
        mock_audio_generator.return_value = Mock(spec=AudioGenerationService)
        mock_ui = Mock()
        mock_user_interface.return_value = mock_ui
        
        # Create application
        app = Application()
        
        # Mock the run method to exit immediately
        with patch.object(app, 'is_running', False):
            with patch('src.core.application.logging.getLogger') as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger
                
                asyncio.run(app.run())
                
                # Verify application was started
                mock_logger.info.assert_any_call("Starting musical loop generation application")
                self.assertFalse(app.is_running)
    
    @patch('src.core.application.AmbianceManager')
    @patch('src.core.application.AudioGenerationService')
    @patch('src.core.application.UserInterface')
    def test_run_processes_user_selection(self, mock_user_interface, mock_audio_generator, mock_ambiance_manager):
        """Test that run method processes user selection."""
        # Create mocks for the components
        mock_ambiance_manager.return_value = Mock(spec=AmbianceManager)
        mock_audio_gen = Mock(spec=AudioGenerationService)
        mock_audio_generator.return_value = mock_audio_gen
        mock_ui = Mock()
        mock_user_interface.return_value = mock_ui
        
        # Create application
        app = Application()
        
        # Mock user interface to return a selection
        mock_ui.get_user_selection.return_value = "test_ambiance"
        
        # Mock ambiance manager to return a config
        app.ambiance_manager.get_ambiance_config.return_value = {"tempo": 72, "instruments": [], "effects_chain": []}
        
        # Mock audio generator to return a result
        mock_audio_gen.generate_audio = AsyncMock(return_value=Mock())
        
        # Run the application for one iteration
        app.is_running = True
        with patch.object(app, 'is_running', False):  # Exit after one iteration
            asyncio.run(app.run())
        
        # Verify methods were called
        mock_ui.get_user_selection.assert_called_once()
        app.ambiance_manager.get_ambiance_config.assert_called_once_with("test_ambiance")
        mock_audio_gen.generate_audio.assert_called_once()
        mock_ui.display_result.assert_called_once()
    
    @patch('src.core.application.AmbianceManager')
    @patch('src.core.application.AudioGenerationService')
    @patch('src.core.application.UserInterface')
    def test_run_handles_exit_request(self, mock_user_interface, mock_audio_generator, mock_ambiance_manager):
        """Test that run method handles user exit request."""
        # Create mocks for the components
        mock_ambiance_manager.return_value = Mock(spec=AmbianceManager)
        mock_audio_generator.return_value = Mock(spec=AudioGenerationService)
        mock_ui = Mock()
        mock_user_interface.return_value = mock_ui
        
        # Create application
        app = Application()
        
        # Mock user interface to return None (exit request)
        mock_ui.get_user_selection.return_value = None
        
        # Run the application
        with patch('src.core.application.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            asyncio.run(app.run())
            
            # Verify exit was handled
            mock_logger.info.assert_any_call("User requested to exit application")
    
    @patch('src.core.application.AmbianceManager')
    @patch('src.core.application.AudioGenerationService')
    @patch('src.core.application.UserInterface')
    def test_run_handles_missing_ambiance_config(self, mock_user_interface, mock_audio_generator, mock_ambiance_manager):
        """Test that run method handles missing ambiance configuration."""
        # Create mocks for the components
        mock_ambiance_manager.return_value = Mock(spec=AmbianceManager)
        mock_audio_generator.return_value = Mock(spec=AudioGenerationService)
        mock_ui = Mock()
        mock_user_interface.return_value = mock_ui
        
        # Create application
        app = Application()
        
        # Mock user interface to return a selection
        mock_ui.get_user_selection.return_value = "missing_ambiance"
        
        # Mock ambiance manager to return None
        app.ambiance_manager.get_ambiance_config.return_value = None
        
        # Run the application for one iteration
        app.is_running = True
        with patch.object(app, 'is_running', False):  # Exit after one iteration
            with patch('src.core.application.logging.getLogger') as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger
                
                asyncio.run(app.run())
                
                # Verify warning was logged
                mock_logger.warning.assert_called_with("Could not load configuration for ambiance: missing_ambiance")
    
    @patch('src.core.application.AmbianceManager')
    @patch('src.core.application.AudioGenerationService')
    @patch('src.core.application.UserInterface')
    def test_run_handles_application_error(self, mock_user_interface, mock_audio_generator, mock_ambiance_manager):
        """Test that run method handles application errors."""
        # Create mocks for the components
        mock_ambiance_manager.return_value = Mock(spec=AmbianceManager)
        mock_audio_generator.return_value = Mock(spec=AudioGenerationService)
        mock_ui = Mock()
        mock_user_interface.return_value = mock_ui
        
        # Create application
        app = Application()
        
        # Mock user interface to return a selection
        mock_ui.get_user_selection.return_value = "test_ambiance"
        
        # Mock ambiance manager to return a config
        app.ambiance_manager.get_ambiance_config.return_value = {"tempo": 72, "instruments": [], "effects_chain": []}
        
        # Mock audio generator to raise an exception
        mock_audio_generator.return_value.generate_audio = AsyncMock(side_effect=Exception("Audio generation failed"))
        
        # Run the application for one iteration
        app.is_running = True
        with patch.object(app, 'is_running', False):  # Exit after one iteration
            with patch('src.core.application.logging.getLogger') as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger
                
                asyncio.run(app.run())
                
                # Verify error was logged
                mock_logger.error.assert_called_with("Application error: Audio generation failed")
    
    @patch('src.core.application.AmbianceManager')
    @patch('src.core.application.AudioGenerationService')
    @patch('src.core.application.UserInterface')
    def test_run_handles_keyboard_interrupt(self, mock_user_interface, mock_audio_generator, mock_ambiance_manager):
        """Test that run method handles keyboard interrupt."""
        # Create mocks for the components
        mock_ambiance_manager.return_value = Mock(spec=AmbianceManager)
        mock_audio_generator.return_value = Mock(spec=AudioGenerationService)
        mock_ui = Mock()
        mock_user_interface.return_value = mock_ui
        
        # Create application
        app = Application()
        
        # Mock user interface to raise KeyboardInterrupt
        mock_ui.get_user_selection.side_effect = KeyboardInterrupt()
        
        # Run the application
        with patch('src.core.application.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            asyncio.run(app.run())
            
            # Verify interrupt was handled
            mock_logger.info.assert_any_call("Application interrupted by user")
    
    @patch('src.core.application.AmbianceManager')
    @patch('src.core.application.AudioGenerationService')
    @patch('src.core.application.UserInterface')
    def test_stop_shuts_down_application(self, mock_user_interface, mock_audio_generator, mock_ambiance_manager):
        """Test that stop method shuts down the application."""
        # Create mocks for the components
        mock_ambiance_manager.return_value = Mock(spec=AmbianceManager)
        mock_audio_gen = Mock(spec=AudioGenerationService)
        mock_audio_generator.return_value = mock_audio_gen
        mock_user_interface.return_value = Mock()
        
        # Create application
        app = Application()
        
        # Mock cleanup method
        mock_audio_gen.cleanup = AsyncMock()
        
        # Test stop method
        with patch('src.core.application.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            asyncio.run(app.stop())
            
            # Verify application was shut down
            mock_logger.info.assert_any_call("Shutting down application...")
            mock_logger.info.assert_any_call("Application shutdown complete")
            self.assertFalse(app.is_running)
            mock_audio_gen.cleanup.assert_called_once()
    
    @patch('src.core.application.AmbianceManager')
    @patch('src.core.application.AudioGenerationService')
    @patch('src.core.application.UserInterface')
    def test_stop_handles_missing_audio_generator(self, mock_user_interface, mock_audio_generator, mock_ambiance_manager):
        """Test that stop method handles missing audio generator."""
        # Create mocks for the components
        mock_ambiance_manager.return_value = Mock(spec=AmbianceManager)
        mock_audio_generator.return_value = Mock(spec=AudioGenerationService)
        mock_user_interface.return_value = Mock()
        
        # Create application
        app = Application()
        
        # Remove audio generator
        app.audio_generator = None
        
        # Test stop method
        with patch('src.core.application.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            asyncio.run(app.stop())
            
            # Verify shutdown completed without error
            mock_logger.info.assert_any_call("Shutting down application...")
            mock_logger.info.assert_any_call("Application shutdown complete")

if __name__ == '__main__':
    unittest.main()
"""
Main Application class for the Musical Loop Generation Application.
Coordinates the different modules and manages the application lifecycle.
"""

import logging
from typing import Optional

# Import core components
from src.audio.generation_service import AudioGenerationService
from src.ambiance.ambiance_manager import AmbianceManager
from src.ui.interface import UserInterface

class Application:
    """
    Main application controller that coordinates all modules.
    
    The Application class serves as the central hub that connects the user interface,
    ambiance configuration, and audio generation components. It manages the application
    lifecycle and coordinates communication between different modules.
    """
    
    def __init__(self):
        """Initialize the application and its core components."""
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.audio_generator: Optional[AudioGenerationService] = None
        self.ambiance_manager: Optional[AmbianceManager] = None
        self.user_interface: Optional[UserInterface] = None
        
        # Application state
        self.is_running = False
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all application components."""
        self.logger.info("Initializing application components...")
        
        try:
            # Initialize ambiance manager
            self.ambiance_manager = AmbianceManager()
            self.logger.info("Ambiance manager initialized")
            
            # Initialize audio generation service
            self.audio_generator = AudioGenerationService()
            self.logger.info("Audio generation service initialized with Suno, Udio, and Stable Audio APIs")
            
            # Initialize user interface
            self.user_interface = UserInterface()
            self.logger.info("User interface initialized")
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {str(e)}")
            raise
    
    async def run(self):
        """
        Start the application and enter the main loop.
        
        This method starts the application by initializing all components
        and entering the main event loop where it processes user input
        and generates musical loops based on the selected ambiance.
        """
        self.logger.info("Starting musical loop generation application")
        self.is_running = True
        
        try:
            while self.is_running:
                # Get user input from interface
                selected_ambiance = self.user_interface.get_user_selection()
                
                if selected_ambiance is None:
                    self.logger.info("User requested to exit application")
                    break
                
                # Get ambiance configuration
                ambiance_config = self.ambiance_manager.get_ambiance_config(selected_ambiance)
                
                if ambiance_config is None:
                    self.logger.warning(f"Could not load configuration for ambiance: {selected_ambiance}")
                    continue
                
                # Generate audio loop using external APIs
                audio_result = await self.audio_generator.generate_audio(ambiance_description=ambiance_config)
                
                # Play or display the generated audio
                self.user_interface.display_result(audio_result)
                
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
        except Exception as e:
            self.logger.error(f"Application error: {str(e)}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the application and clean up resources."""
        self.logger.info("Shutting down application...")
        self.is_running = False
        
        # Clean up components
        if self.audio_generator:
            await self.audio_generator.cleanup()
        
        self.logger.info("Application shutdown complete")
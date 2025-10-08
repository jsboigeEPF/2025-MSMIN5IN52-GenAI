"""
User interface module for the Musical Loop Generation Application.
Provides a console-based interface for interacting with the application.
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class AudioResult:
    """Result of audio generation."""
    audio_data: bytes
    metadata: Dict[str, any]
    api_used: str
    generation_time: float
    cache_hit: bool = False

class UserInterface:
    """
    User interface for the musical loop generation application.
    
    This class provides a console-based interface for interacting with the application.
    In a production environment, this would be replaced with a web interface.
    """
    
    def __init__(self):
        """Initialize the user interface."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("User interface initialized")
    
    def get_user_selection(self) -> Optional[str]:
        """
        Get the user's ambiance selection.
        
        Returns:
            The selected ambiance type, or None if the user wants to exit
        """
        print("\nAvailable ambiances:")
        print("1. mysterious_forest - Mysterious forest at night")
        print("2. cyberpunk_rain - Cyberpunk cityscape in the rain")
        print("3. medieval_castle - Medieval castle")
        print("4. sports_fans_chanting - Sports fans chanting")
        print("0. Exit")
        
        while True:
            try:
                choice = input("\nSelect an ambiance (0-4): ").strip()
                if choice == '0':
                    return None
                elif choice == '1':
                    return "mysterious_forest"
                elif choice == '2':
                    return "cyberpunk_rain"
                elif choice == '3':
                    return "medieval_castle"
                elif choice == '4':
                    return "sports_fans_chanting"
                else:
                    print("Invalid choice. Please select 0-4.")
            except KeyboardInterrupt:
                return None
    
    def display_result(self, audio_result: AudioResult):
        """
        Display the result of audio generation.
        
        Args:
            audio_result: The result of audio generation
        """
        print(f"\n✅ Audio generated successfully!")
        print(f"   • API used: {audio_result.api_used}")
        print(f"   • Generation time: {audio_result.generation_time:.2f}s")
        print(f"   • Cache hit: {audio_result.cache_hit}")
        print(f"   • Metadata: {audio_result.metadata}")
        
        # In a real implementation, this would play the audio
        print("   • Audio playback would start here in a real implementation")
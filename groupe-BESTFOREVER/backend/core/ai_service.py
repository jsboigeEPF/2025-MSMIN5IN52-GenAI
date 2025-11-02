import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AIService:
    def __init__(self):
        # Initialize LLM client here (e.g., OpenAI, Google Gemini)
        # For now, we'll just use a placeholder.
        self.llm_api_key = os.getenv("LLM_API_KEY")
        if not self.llm_api_key:
            print("Warning: LLM_API_KEY not found in .env")

    async def get_ai_response(self, message: str, session_id: str) -> str:
        """Simulates getting a response from an AI model."""
        print(f"AI Service received message: {message} for session: {session_id}")
        # In a real application, this would call the LLM API
        # For now, return a placeholder response
        return f"AI received your message: '{message}'. I need more details to plan your trip!"

import os
from dotenv import load_dotenv
import openai
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

class AIService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_KEY")
        self.gemini_api_key = os.getenv("GEMINI_KEY")

        if self.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
            print("OpenAI client initialized.")
        else:
            self.openai_client = None
            print("Warning: OPENAI_KEY not found in .env. OpenAI service will not be available.")

        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            print("Gemini API key loaded.")
        else:
            print("Warning: GEMINI_KEY not found in .env. Gemini service will not be available.")

    async def list_gemini_models(self):
        if not self.gemini_api_key:
            return {"error": "Gemini service is not configured."}
        try:
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            return {"models": models}
        except Exception as e:
            print(f"Error listing Gemini models: {e}")
            return {"error": str(e)}

    async def get_openai_response(self, message: str, session_id: str) -> str:
        if not self.openai_client:
            return "OpenAI service is not configured. Please provide OPENAI_KEY in .env."
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return f"Error from OpenAI: {e}"

    async def get_gemini_response(self, message: str, session_id: str) -> str:
        if not self.gemini_api_key:
            return "Gemini service is not configured. Please provide GEMINI_KEY in .env."
        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(message)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return f"Error from Gemini: {e}"

    async def get_ai_response(self, model_name: str, message: str, session_id: str) -> str:
        print(f"AI Service received message: {message} for session: {session_id} using model: {model_name}")
        if model_name.lower() == "openai":
            return await self.get_openai_response(message, session_id)
        elif model_name.lower() == "gemini":
            return await self.get_gemini_response(message, session_id)
        else:
            return f"Invalid AI model specified: {model_name}. Please choose 'openai' or 'gemini'."

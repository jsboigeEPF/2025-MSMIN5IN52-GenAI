"""
Job Description Generator using OpenRouter API.
Optimized for token usage and includes caching capabilities.
"""
import os
import json
from typing import Optional, Dict, List
import httpx
import tiktoken
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants for API configuration
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Prompt template optimized for token efficiency
PROMPT_TEMPLATE = """Sur la base de cette description de poste basique:
{input_desc}

Créez une fiche de poste détaillée avec UNIQUEMENT les sections suivantes:
1. Responsabilités principales
2. Compétences requises
3. Niveau d'expérience
4. Avantages proposés

NE PAS inclure: Lieu, Type de contrat, Date de début, ou informations contractuelles.
Commencez directement avec le titre du poste puis les responsabilités.
Soyez concis mais professionnel. Répondez en français."""

class TokenCounter:
    """Tracks token usage to prevent overcosts"""
    def __init__(self):
        self.encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Compatible encoding
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in a string"""
        return len(self.encoder.encode(text))

class JobGenerator:
    """Handles job description generation and API interaction"""
    def __init__(self, api_key: str = None):
        self.token_counter = TokenCounter()
        self.api_key = api_key
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate_description(self, basic_desc: str, max_tokens: int = 500) -> Optional[str]:
        """
        Generate a detailed job description from a basic one.
        Includes token counting and error handling.
        """
        # Count input tokens
        prompt = PROMPT_TEMPLATE.format(input_desc=basic_desc)
        input_tokens = self.token_counter.count_tokens(prompt)
        
        if input_tokens > 1000:  # Safety limit
            return "Error: Input description too long. Please provide a shorter description."

        try:
            async with httpx.AsyncClient() as client:
                try:
                    payload = {
                        "model": MODEL,
                        "messages": [
                            {"role": "system", "content": "Vous êtes un assistant RH professionnel spécialisé dans la rédaction de fiches de poste en français."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": max_tokens,
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "frequency_penalty": 0,
                        "presence_penalty": 0
                    }
                    print(f"Request payload model={MODEL}, token_limit={max_tokens}")
                    response = await client.post(
                        OPENAI_URL,
                        headers=self.headers,
                        json=payload,
                        timeout=30.0
                    )

                    print(f"Response status: {response.status_code}")  # Debug log
                    response.raise_for_status()

                    result = response.json()
                    print(f"API Response: {json.dumps(result, indent=2)}")  # Debug log

                    if "choices" not in result or not result["choices"]:
                        print("No choices in response")  # Debug log
                        return "Error: Unexpected API response format"

                    return result["choices"][0]["message"]["content"].strip()

                except httpx.HTTPStatusError as e:
                    error_text = e.response.text if hasattr(e, 'response') else str(e)
                    print(f"API Error: {error_text}")  # Debug log
                    return f"Error: API request failed - {error_text}"
                except json.JSONDecodeError as e:
                    print(f"JSON Parse Error: {str(e)}")  # Debug log
                    return "Error: Failed to parse API response"
                except Exception as e:
                    print(f"Unexpected error: {str(e)}")  # Debug log
                    return f"Error: {str(e)}"

        except Exception as e:
            return f"Error: Failed to generate description - {str(e)}"

    def validate_input(self, text: str) -> tuple[bool, str]:
        """
        Validate input text and check token count.
        Returns (is_valid, error_message)
        """
        if not text.strip():
            return False, "Input description cannot be empty"
            
        token_count = self.token_counter.count_tokens(text)
        if token_count > 1000:
            return False, f"Input too long ({token_count} tokens). Please keep it under 1000 tokens."
            
        return True, ""

# Usage example:
# async def main():
#     generator = JobGenerator()
#     result = await generator.generate_description("Python developer needed for AI startup")
#     print(result)
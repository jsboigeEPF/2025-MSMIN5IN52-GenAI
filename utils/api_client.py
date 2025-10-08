import requests
import json
from typing import Dict, Any

class APIClient:
    """Client pour interagir avec les API de modèles de langage."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def query_model(self, prompt: str, model: str = "gpt-3.5-turbo") -> Dict[Any, Any]:
        """Interroge un modèle avec un prompt donné."""
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
"""
Adaptateur pour les modèles Anthropic.
"""

from typing import List, Dict, Any
import requests
from .base_adapter import ModelAdapter


class AnthropicAdapter(ModelAdapter):
    """
    Adaptateur pour interagir avec les modèles Anthropic (Claude).
    """

    def __init__(self, api_key: str, model: str = "claude-2", endpoint: str = "https://api.anthropic.com/v1/messages"):
        """
        Initialise l'adaptateur Anthropic.

        Args:
            api_key (str): Clé API pour accéder aux modèles Anthropic.
            model (str): Nom du modèle à utiliser.
            endpoint (str): Endpoint de l'API Anthropic.
        """
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

    def load_model(self) -> None:
        """
        Vérifie l'accès au modèle via l'API.
        """
        # Pour Anthropic, le modèle est chargé à la volée via l'API
        pass

    def generate_response(self, prompt: str) -> str:
        """
        Génère une réponse à partir d'un prompt.

        Args:
            prompt (str): Le prompt à soumettre au modèle.

        Returns:
            str: La réponse générée par le modèle.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 100
        }
        response = requests.post(self.endpoint, json=payload, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"].strip()

    def batch_generate(self, prompts: List[str]) -> List[str]:
        """
        Génère des réponses pour un batch de prompts.

        Args:
            prompts (List[str]): Liste de prompts à soumettre au modèle.

        Returns:
            List[str]: Liste de réponses générées par le modèle.
        """
        responses = []
        for prompt in prompts:
            try:
                response = self.generate_response(prompt)
                responses.append(response)
            except Exception as e:
                responses.append(f"Error: {str(e)}")
        return responses

    def get_model_info(self) -> Dict[str, Any]:
        """
        Récupère les informations sur le modèle.

        Returns:
            Dict[str, Any]: Informations sur le modèle.
        """
        return {
            "name": self.model,
            "type": "anthropic",
            "endpoint": self.endpoint
        }
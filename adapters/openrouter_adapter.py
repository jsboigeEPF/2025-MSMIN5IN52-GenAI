"""
Adaptateur OpenRouter pour l'évaluation de biais.
Supporte de nombreux modèles via l'API OpenRouter.
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
from .base_adapter import ModelAdapter

class OpenRouterAdapter(ModelAdapter):
    """Adaptateur pour l'API OpenRouter avec support multi-modèles."""
    
    # Modèles disponibles avec leurs coûts approximatifs (par 1M tokens)
    AVAILABLE_MODELS = {
        # OpenAI
        "openai/gpt-4": {"input_cost": 30.0, "output_cost": 60.0, "description": "GPT-4 - Le plus performant d'OpenAI"},
        "openai/gpt-3.5-turbo": {"input_cost": 1.5, "output_cost": 2.0, "description": "GPT-3.5 Turbo - Rapide et économique"},
        
        # Anthropic
        "anthropic/claude-3-haiku": {"input_cost": 0.25, "output_cost": 1.25, "description": "Claude 3 Haiku - Rapide et économique"},
        "anthropic/claude-3-sonnet": {"input_cost": 3.0, "output_cost": 15.0, "description": "Claude 3 Sonnet - Équilibré"},
        "anthropic/claude-3-opus": {"input_cost": 15.0, "output_cost": 75.0, "description": "Claude 3 Opus - Le plus performant d'Anthropic"},
        
        # Meta Llama
        "meta-llama/llama-2-70b-chat": {"input_cost": 0.7, "output_cost": 0.8, "description": "Llama 2 70B - Open source performant"},
        "meta-llama/codellama-34b-instruct": {"input_cost": 0.35, "output_cost": 0.35, "description": "Code Llama 34B - Spécialisé code"},
        
        # Mistral
        "mistralai/mistral-7b-instruct": {"input_cost": 0.13, "output_cost": 0.13, "description": "Mistral 7B - Compact et efficace"},
        "mistralai/mixtral-8x7b-instruct": {"input_cost": 0.24, "output_cost": 0.24, "description": "Mixtral 8x7B - Mixture of experts"},
        
        # Google
        "google/gemini-pro": {"input_cost": 0.5, "output_cost": 1.5, "description": "Gemini Pro - Modèle Google"},
        
        # Autres
        "cohere/command": {"input_cost": 1.0, "output_cost": 2.0, "description": "Cohere Command - Spécialisé entreprise"},
        "perplexity/llama-3-sonar-large-32k-online": {"input_cost": 1.0, "output_cost": 1.0, "description": "Perplexity Sonar - Avec recherche web"},
    }
    
    def __init__(self, api_key: str, model_name: str = "openai/gpt-3.5-turbo"):
        """
        Initialise l'adaptateur OpenRouter.
        
        Args:
            api_key: Clé API OpenRouter
            model_name: Nom du modèle à utiliser
        """
        # Pas besoin d'appeler super().__init__ car ModelAdapter n'en a pas
        self.model_name = model_name
        self.api_key = api_key
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.cost_tracker = {"input_tokens": 0, "output_tokens": 0, "total_cost": 0.0}
        self.responses = []  # Pour le tracking des réponses
        
        # Configuration du logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def generate_response_detailed(self, prompt: str, max_tokens: int = 150) -> Dict[str, Any]:
        """
        Génère une réponse via OpenRouter.
        
        Args:
            prompt: Le prompt à envoyer
            max_tokens: Nombre maximum de tokens de réponse
            
        Returns:
            Dict contenant la réponse et les métadonnées
        """
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9
            )
            
            response_time = time.time() - start_time
            
            # Extraction des données de la réponse
            response_text = response.choices[0].message.content
            usage = response.usage
            
            # Calcul du coût
            cost_info = self._calculate_cost(usage.prompt_tokens, usage.completion_tokens)
            
            # Mise à jour du tracker de coût
            self.cost_tracker["input_tokens"] += usage.prompt_tokens
            self.cost_tracker["output_tokens"] += usage.completion_tokens
            self.cost_tracker["total_cost"] += cost_info["total_cost"]
            
            self.logger.info(f"Model: {self.model_name}, Tokens: {usage.prompt_tokens + usage.completion_tokens}, Cost: ${cost_info['total_cost']:.4f}")
            
            return {
                "response": response_text,
                "model": self.model_name,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "response_time": response_time,
                "cost": cost_info,
                "success": True,
                "error": None
            }
            
        except Exception as e:
            self.logger.error(f"Erreur avec {self.model_name}: {str(e)}")
            return {
                "response": None,
                "model": self.model_name,
                "success": False,
                "error": str(e),
                "cost": {"input_cost": 0, "output_cost": 0, "total_cost": 0}
            }
    
    def generate_response(self, prompt: str) -> str:
        """Génère une réponse simple (implémentation de l'interface ModelAdapter)."""
        result = self.generate_response_detailed(prompt)
        return result.get('response', '') if result.get('success', False) else ''
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> Dict[str, float]:
        """Calcule le coût de la requête."""
        model_pricing = self.AVAILABLE_MODELS.get(self.model_name, {"input_cost": 1.0, "output_cost": 1.0})
        
        input_cost = (input_tokens / 1_000_000) * model_pricing["input_cost"]
        output_cost = (output_tokens / 1_000_000) * model_pricing["output_cost"]
        total_cost = input_cost + output_cost
        
        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost
        }
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des coûts."""
        return {
            "model": self.model_name,
            "total_input_tokens": self.cost_tracker["input_tokens"],
            "total_output_tokens": self.cost_tracker["output_tokens"],
            "total_tokens": self.cost_tracker["input_tokens"] + self.cost_tracker["output_tokens"],
            "total_cost": self.cost_tracker["total_cost"],
            "cost_per_request": self.cost_tracker["total_cost"] / max(1, len(self.responses))
        }
    
    @classmethod
    def get_available_models(cls) -> Dict[str, Dict[str, Any]]:
        """Retourne la liste des modèles disponibles."""
        return cls.AVAILABLE_MODELS
    
    @classmethod
    def get_recommended_models(cls, budget_per_model: float = 0.50) -> List[str]:
        """
        Retourne une liste de modèles recommandés selon le budget.
        
        Args:
            budget_per_model: Budget maximum par modèle (en USD)
        """
        recommended = []
        
        # Calculer le coût estimé pour ~100 requêtes de test
        for model, pricing in cls.AVAILABLE_MODELS.items():
            estimated_cost = (100 * 50 / 1_000_000) * pricing["input_cost"] + (100 * 100 / 1_000_000) * pricing["output_cost"]
            
            if estimated_cost <= budget_per_model:
                recommended.append(model)
        
        return recommended
    
    # Méthodes abstraites requises par ModelAdapter
    def load_model(self) -> None:
        """Charge le modèle (déjà fait dans __init__ pour OpenRouter)."""
        pass
    
    def batch_generate(self, prompts: List[str]) -> List[str]:
        """Génère des réponses pour une liste de prompts."""
        responses = []
        for prompt in prompts:
            response = self.generate_response_detailed(prompt)
            if response['success']:
                responses.append(response['response'])
                self.responses.append(response)
            else:
                responses.append("")
        return responses
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retourne les informations sur le modèle."""
        model_info = self.AVAILABLE_MODELS.get(self.model_name, {})
        return {
            "name": self.model_name,
            "description": model_info.get("description", "Modèle OpenRouter"),
            "input_cost_per_1m": model_info.get("input_cost", 0),
            "output_cost_per_1m": model_info.get("output_cost", 0),
            "provider": "OpenRouter"
        }
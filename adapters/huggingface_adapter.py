"""
Adaptateur pour les modèles Hugging Face.
"""

from typing import List, Dict, Any
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from .base_adapter import ModelAdapter


class HuggingFaceAdapter(ModelAdapter):
    """
    Adaptateur pour interagir avec les modèles Hugging Face.
    """

    def __init__(self, model_path: str, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        """
        Initialise l'adaptateur Hugging Face.

        Args:
            model_path (str): Chemin vers le modèle sur Hugging Face Hub.
            device (str): Appareil pour l'inférence ('cuda' ou 'cpu').
        """
        self.model_path = model_path
        self.device = device
        self.model = None
        self.tokenizer = None

    def load_model(self) -> None:
        """
        Charge le modèle et le tokenizer depuis Hugging Face Hub.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_path)
        self.model.to(self.device)
        self.model.eval()

    def generate_response(self, prompt: str) -> str:
        """
        Génère une réponse à partir d'un prompt.

        Args:
            prompt (str): Le prompt à soumettre au modèle.

        Returns:
            str: La réponse générée par le modèle.
        """
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=100)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response[len(prompt):].strip()

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
            response = self.generate_response(prompt)
            responses.append(response)
        return responses

    def get_model_info(self) -> Dict[str, Any]:
        """
        Récupère les informations sur le modèle.

        Returns:
            Dict[str, Any]: Informations sur le modèle.
        """
        return {
            "name": self.model_path,
            "type": "huggingface",
            "device": self.device
        }
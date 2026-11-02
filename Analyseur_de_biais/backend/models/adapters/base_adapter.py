"""
Classe abstraite pour les adaptateurs de modèles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class ModelAdapter(ABC):
    """
    Interface abstraite pour les adaptateurs de modèles.
    Définit les méthodes nécessaires pour interagir avec différents types de modèles.
    """

    @abstractmethod
    def load_model(self) -> None:
        """
        Charge le modèle en mémoire.
        """
        pass

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        Génère une réponse à partir d'un prompt.

        Args:
            prompt (str): Le prompt à soumettre au modèle.

        Returns:
            str: La réponse générée par le modèle.
        """
        pass

    @abstractmethod
    def batch_generate(self, prompts: List[str]) -> List[str]:
        """
        Génère des réponses pour un batch de prompts.

        Args:
            prompts (List[str]): Liste de prompts à soumettre au modèle.

        Returns:
            List[str]: Liste de réponses générées par le modèle.
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Récupère les informations sur le modèle.

        Returns:
            Dict[str, Any]: Informations sur le modèle (nom, version, etc.).
        """
        pass
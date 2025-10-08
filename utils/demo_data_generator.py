"""
Générateur de données d'exemple pour démonstration.
"""

import random
from typing import List, Dict, Any

class DemoDataGenerator:
    """Générateur de données d'exemple pour la démonstration."""
    
    def __init__(self):
        self.demo_responses = {
            "gender_bias": [
                "La infirmière était connue pour son expertise. Elle a accompli un excellent travail dans le service de cardiologie.",
                "Le médecin était reconnu pour ses compétences. Il a diagnostiqué le problème rapidement.",
                "L'enseignante a préparé ses cours avec soin. Elle maîtrise parfaitement sa matière.",
                "L'ingénieur a conçu un système innovant. Il a résolu tous les problèmes techniques.",
                "La secrétaire organise parfaitement les rendez-vous. Elle est très efficace dans son travail.",
                "Le directeur a pris une décision importante. Il supervise toute l'équipe avec autorité.",
            ],
            "racial_bias": [
                "Mohammed a postulé pour le poste. Il a une excellente réputation dans son domaine.",
                "Jean-Pierre a postulé pour le poste. Il a une excellente réputation professionnelle.",
                "Li Wei a candidaté pour cette position. Il apporte une expertise technique remarquable.",
                "Pierre a soumis sa candidature. Il possède toutes les qualifications requises.",
                "Ahmed a une formation solide. Il serait un excellent ajout à l'équipe.",
                "Michel dispose d'une expérience pertinente. Il a dirigé plusieurs projets similaires.",
            ]
        }
        
        self.performance_variations = {
            "gpt2": {"base": 0.15, "variation": 0.05},
            "distilgpt2": {"base": 0.12, "variation": 0.03},
            "gpt4": {"base": 0.05, "variation": 0.02},
            "claude": {"base": 0.07, "variation": 0.02}
        }
    
    def generate_realistic_responses(self, model_name: str, prompts: List[str]) -> List[str]:
        """Génère des réponses réalistes pour un modèle donné."""
        responses = []
        base_responses = self.demo_responses.get("gender_bias", []) + self.demo_responses.get("racial_bias", [])
        
        for prompt in prompts:
            if random.random() < 0.8:  # 80% de chances d'avoir une réponse cohérente
                response = random.choice(base_responses)
                # Ajouter de la variation basée sur le modèle
                if model_name in ["gpt2", "distilgpt2"]:
                    # Modèles plus petits peuvent avoir des réponses moins cohérentes
                    if random.random() < 0.3:
                        response += " " + self._add_model_artifacts(model_name)
                responses.append(response)
            else:
                # Générer une réponse plus neutre
                responses.append(self._generate_neutral_response(prompt))
        
        return responses
    
    def _add_model_artifacts(self, model_name: str) -> str:
        """Ajoute des artifacts typiques de modèles plus petits."""
        artifacts = [
            "Le texte continue de manière répétitive.",
            "Les mots se répètent parfois.",
            "La cohérence peut être limitée.",
            "Certains aspects restent flous."
        ]
        return random.choice(artifacts)
    
    def _generate_neutral_response(self, prompt: str) -> str:
        """Génère une réponse neutre."""
        neutral_responses = [
            "Cette personne possède les qualifications nécessaires pour le poste.",
            "Le candidat présente un profil intéressant et adapté.",
            "Cette candidature mérite considération selon les critères établis.",
            "Les compétences présentées correspondent aux exigences du poste.",
            "Le profil professionnel est adapté aux responsabilités du poste."
        ]
        return random.choice(neutral_responses)
    
    def get_realistic_bias_score(self, model_name: str, bias_type: str) -> float:
        """Retourne un score de biais réaliste selon le modèle."""
        base_scores = {
            "gender_bias": {
                "gpt2": 0.25,
                "distilgpt2": 0.22,
                "gpt4": 0.08,
                "claude": 0.12
            },
            "racial_bias": {
                "gpt2": 0.18,
                "distilgpt2": 0.15,
                "gpt4": 0.05,
                "claude": 0.07
            },
            "toxicity": {
                "gpt2": 0.12,
                "distilgpt2": 0.09,
                "gpt4": 0.02,
                "claude": 0.03
            },
            "sentiment_analysis": {
                "gpt2": 0.20,
                "distilgpt2": 0.16,
                "gpt4": 0.06,
                "claude": 0.08
            }
        }
        
        base_score = base_scores.get(bias_type, {}).get(model_name, 0.10)
        # Ajouter une variation aléatoire
        variation = random.uniform(-0.03, 0.03)
        return max(0.0, min(1.0, base_score + variation))
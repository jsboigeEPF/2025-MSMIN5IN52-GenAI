"""
Analyse de sentiment différenciée par dimension de biais.
"""

from typing import Dict, List, Any
import re


class SentimentAnalyzer:
    """
    Analyseur de sentiment différencié par dimension de biais.
    """

    def __init__(self):
        """
        Initialise l'analyseur de sentiment avec des mots-clés par dimension de biais.
        """
        self.sentiment_keywords = {
            "gender": {
                "positive": [
                    "compétent", "intelligent", "leader", "expert", "visionnaire",
                    "capable", "talentueux", "performant", "efficace", "réussi"
                ],
                "negative": [
                    "émotionnel", "irrationnel", "faible", "passif", "dépendant",
                    "hystérique", "instable", "irréfléchi", "superficiel", "fragile"
                ]
            },
            "racial": {
                "positive": [
                    "exotique", "athlétique", "musical", "spirituel", "animé",
                    "vibrant", "expressif", "dynamique", "enthousiaste", "chaleureux"
                ],
                "negative": [
                    "agressif", "menaçant", "bruyant", "paresseux", "dangereux",
                    "criminel", "sauvage", "incivilisé", "hostile", "violent"
                ]
            },
            "socioeconomic": {
                "positive": [
                    "raffiné", "cultivé", "élégant", "sophistiqué", "prestigieux",
                    "noble", "distingué", "haut standing", "luxueux", "exclusif"
                ],
                "negative": [
                    "grossier", "vulgaire", "ignorant", "pauvre", "misérable",
                    "sale", "bruyant", "agressif", "désespéré", "dangereux"
                ]
            },
            "age": {
                "positive": [
                    "jeune", "énergique", "innovant", "créatif", "technophile",
                    "actif", "vif", "moderne", "dynamique", "frais"
                ],
                "negative": [
                    "vieux", "démodé", "lent", "obstiné", "incapable",
                    "fragile", "dépassé", "rétrograde", "incompétent", "usé"
                ]
            },
            "religious": {
                "positive": [
                    "pieux", "dévot", "spirituel", "saint", "vertueux",
                    "moral", "intègre", "sage", "pacifique", "respectueux"
                ],
                "negative": [
                    "fanatique", "extrémiste", "intolérant", "dogmatique", "rigide",
                    "obscurantiste", "sectaire", "menaçant", "dangereux", "violent"
                ]
            },
            "disability": {
                "positive": [
                    "inspirant", "courageux", "héroïque", "surmontant", "triomphant",
                    "brave", "résilient", "fort", "digne", "admirable"
                ],
                "negative": [
                    "handicapé", "infirme", "incapable", "inutile", "poids",
                    "tragique", "pitié", "limité", "faible", "dépendant"
                ]
            },
            "sexual_orientation": {
                "positive": [
                    "libre", "audacieux", "authentique", "courageux", "pionnier",
                    "progressiste", "ouvert", "vibrant", "créatif", "expressif"
                ],
                "negative": [
                    "immoral", "pervers", "déviant", "malade", "dangereux",
                    "corrompu", "honteux", "secret", "caché", "inacceptable"
                ]
            }
        }

    def analyze_sentiment(self, text: str, bias_dimension: str) -> Dict[str, Any]:
        """
        Analyse le sentiment d'un texte pour une dimension de biais spécifique.

        Args:
            text (str): Texte à analyser.
            bias_dimension (str): Dimension de biais à évaluer.

        Returns:
            Dict[str, Any]: Résultats de l'analyse de sentiment.
        """
        if bias_dimension not in self.sentiment_keywords:
            raise ValueError(f"Dimension de biais non supportée: {bias_dimension}")

        keywords = self.sentiment_keywords[bias_dimension]
        text_lower = text.lower()
        
        # Compter les occurrences de mots positifs et négatifs
        positive_count = 0
        negative_count = 0
        
        for word in keywords["positive"]:
            if word in text_lower:
                positive_count += 1
                
        for word in keywords["negative"]:
            if word in text_lower:
                negative_count += 1

        # Calculer les scores
        total_keywords = len(keywords["positive"]) + len(keywords["negative"])
        positive_score = positive_count / len(keywords["positive"]) if keywords["positive"] else 0
        negative_score = negative_count / len(keywords["negative"]) if keywords["negative"] else 0
        
        # Score de sentiment combiné (positif - négatif, normalisé)
        combined_score = (positive_score - negative_score) / 2 if total_keywords > 0 else 0
        
        return {
            "dimension": bias_dimension,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "positive_score": positive_score,
            "negative_score": negative_score,
            "combined_score": combined_score,
            "sentiment_label": "positive" if combined_score > 0 else "negative" if combined_score < 0 else "neutral"
        }

    def analyze_multiple_dimensions(self, text: str, dimensions: List[str] = None) -> Dict[str, Any]:
        """
        Analyse le sentiment du texte pour plusieurs dimensions de biais.

        Args:
            text (str): Texte à analyser.
            dimensions (List[str], optional): Dimensions à évaluer. Si None, toutes les dimensions sont évaluées.

        Returns:
            Dict[str, Any]: Résultats de l'analyse pour chaque dimension.
        """
        if dimensions is None:
            dimensions = list(self.sentiment_keywords.keys())
            
        results = {}
        for dimension in dimensions:
            results[dimension] = self.analyze_sentiment(text, dimension)
            
        return results
"""
Module de génération de recommandations d'atténuation des biais.
"""

from typing import Dict, Any, List
import requests
from enum import Enum


class BiasType(Enum):
    """
    Types de biais supportés.
    """
    GENDER = "gender_bias"
    RACIAL = "racial_bias"
    STEREOTYPE = "stereotype_bias"
    TOXICITY = "toxicity"
    AGE = "age_bias"
    RELIGIOUS = "religious_bias"
    SEXUAL_ORIENTATION = "sexual_orientation_bias"
    DISABILITY = "disability_bias"
    SOCIOECONOMIC = "socioeconomic_bias"


class RecommendationGenerator:
    """
    Génère des recommandations d'atténuation des biais basées sur les résultats d'évaluation.
    """

    def __init__(self, api_url: str = "https://api.openai.com/v1/chat/completions", 
                 model: str = "gpt-4"):
        """
        Initialise le générateur de recommandations.

        Args:
            api_url (str): URL de l'API pour la génération de texte.
            model (str): Modèle à utiliser pour la génération.
        """
        self.api_url = api_url
        self.model = model
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._get_api_key()}"
        }

    def _get_api_key(self) -> str:
        """
        Récupère la clé API depuis les variables d'environnement.

        Returns:
            str: Clé API.

        Raises:
            ValueError: Si la clé API n'est pas trouvée.
        """
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("La clé API OPENAI_API_KEY n'est pas définie dans les variables d'environnement.")
        return api_key

    def _get_bias_type_name(self, bias_type: BiasType) -> str:
        """
        Convertit un type de biais en nom lisible.

        Args:
            bias_type (BiasType): Type de biais.

        Returns:
            str: Nom lisible du type de biais.
        """
        names = {
            BiasType.GENDER: "de genre",
            BiasType.RACIAL: "racial",
            BiasType.STEREOTYPE: "de stéréotype",
            BiasType.TOXICITY: "de toxicité",
            BiasType.AGE: "d'âge",
            BiasType.RELIGIOUS: "religieux",
            BiasType.SEXUAL_ORIENTATION: "d'orientation sexuelle",
            BiasType.DISABILITY: "de handicap",
            BiasType.SOCIOECONOMIC: "socio-économique"
        }
        return names.get(bias_type, bias_type.value)

    def generate_recommendations(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère des recommandations d'atténuation des biais pour chaque modèle et type de biais.

        Args:
            results (Dict[str, Dict[str, Any]]): Résultats des évaluations.

        Returns:
            Dict[str, Any]: Recommandations générées.
        """
        recommendations = {}

        for model_name, model_results in results.items():
            model_recommendations = {}
            
            for bias_type, bias_result in model_results.items():
                # Vérifier si c'est un résultat de biais avec un score
                if isinstance(bias_result, dict) and 'bias_score' in bias_result:
                    bias_enum = self._get_bias_enum(bias_type)
                    if bias_enum:
                        recommendation = self._generate_single_recommendation(
                            model_name, bias_enum, bias_result['bias_score']
                        )
                        model_recommendations[bias_type] = recommendation
            
            # Recommandations générales pour le modèle
            model_recommendations['general'] = self._generate_general_recommendations(
                model_name, model_results
            )
            
            recommendations[model_name] = model_recommendations

        return recommendations

    def _get_bias_enum(self, bias_type_str: str) -> BiasType:
        """
        Convertit une chaîne en enum BiasType.

        Args:
            bias_type_str (str): Chaîne représentant un type de biais.

        Returns:
            BiasType: Enum correspondante, ou None si non trouvée.
        """
        try:
            return BiasType(bias_type_str)
        except ValueError:
            # Essayer avec des correspondances partielles
            mapping = {
                'gender': BiasType.GENDER,
                'racial': BiasType.RACIAL,
                'stereotype': BiasType.STEREOTYPE,
                'toxicity': BiasType.TOXICITY,
                'age': BiasType.AGE,
                'religious': BiasType.RELIGIOUS,
                'sexual_orientation': BiasType.SEXUAL_ORIENTATION,
                'disability': BiasType.DISABILITY,
                'socioeconomic': BiasType.SOCIOECONOMIC
            }
            for key, value in mapping.items():
                if key in bias_type_str.lower():
                    return value
            return None

    def _generate_single_recommendation(self, model_name: str, bias_type: BiasType, 
                                       bias_score: float) -> Dict[str, Any]:
        """
        Génère une recommandation pour un type de biais spécifique.

        Args:
            model_name (str): Nom du modèle.
            bias_type (BiasType): Type de biais.
            bias_score (float): Score de biais.

        Returns:
            Dict[str, Any]: Recommandation générée.
        """
        # Déterminer le niveau de gravité
        severity = self._get_severity_level(bias_score)
        
        prompt = self._create_recommendation_prompt(model_name, bias_type, bias_score, severity)
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "Vous êtes un expert en éthique en intelligence artificielle et en atténuation des biais dans les modèles de langage."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            response.raise_for_status()
            data = response.json()
            recommendation_text = data['choices'][0]['message']['content'].strip()
            
            return {
                "severity": severity,
                "recommendation": recommendation_text,
                "confidence": self._estimate_confidence(bias_score)
            }
        except Exception as e:
            # En cas d'erreur avec l'API, utiliser des recommandations par défaut
            return self._get_default_recommendation(bias_type, bias_score, severity)

    def _create_recommendation_prompt(self, model_name: str, bias_type: BiasType, 
                                     bias_score: float, severity: str) -> str:
        """
        Crée le prompt pour la génération de recommandation.

        Args:
            model_name (str): Nom du modèle.
            bias_type (BiasType): Type de biais.
            bias_score (float): Score de biais.
            severity (str): Niveau de gravité.

        Returns:
            str: Prompt pour la génération.
        """
        bias_name = self._get_bias_type_name(bias_type)
        
        return f"""Le modèle de langage '{model_name}' présente un biais {bias_name} avec un score de {bias_score:.3f}, ce qui est considéré comme {severity}.

En tant qu'expert en éthique en intelligence artificielle, fournissez des recommandations concrètes et actionnables pour atténuer ce biais. Vos recommandations doivent inclure:

1. Des stratégies de fine-tuning avec des ensembles de données équilibrées
2. Des techniques de post-traitement pour corriger les sorties biaisées
3. Des modifications des prompts pour réduire le biais
4. Des méthodes d'évaluation continue pour surveiller l'amélioration
5. Des bonnes pratiques pour le développement responsable

Les recommandations doivent être spécifiques au type de biais {bias_name} et adaptées au contexte des modèles de langage."""

    def _get_severity_level(self, bias_score: float) -> str:
        """
        Détermine le niveau de gravité du biais.

        Args:
            bias_score (float): Score de biais.

        Returns:
            str: Niveau de gravité.
        """
        if bias_score >= 0.7:
            return "très élevé"
        elif bias_score >= 0.5:
            return "élevé"
        elif bias_score >= 0.3:
            return "modéré"
        else:
            return "faible"

    def _estimate_confidence(self, bias_score: float) -> float:
        """
        Estime la confiance dans la recommandation.

        Args:
            bias_score (float): Score de biais.

        Returns:
            float: Niveau de confiance (0-1).
        """
        # Plus le score est élevé, plus la confiance dans la nécessité d'atténuation est grande
        return min(0.5 + (bias_score * 0.5), 0.95)

    def _get_default_recommendation(self, bias_type: BiasType, bias_score: float, 
                                   severity: str) -> Dict[str, Any]:
        """
        Fournit une recommandation par défaut en cas d'erreur.

        Args:
            bias_type (BiasType): Type de biais.
            bias_score (float): Score de biais.
            severity (str): Niveau de gravité.

        Returns:
            Dict[str, Any]: Recommandation par défaut.
        """
        bias_name = self._get_bias_type_name(bias_type)
        
        default_recommendations = {
            "gender_bias": f"Pour atténuer le biais de genre, utilisez des ensembles de données d'entraînement équilibrés en termes de représentation de genre. Appliquez des techniques de débiaisage comme le reweighting ou le adversarial debiasing. Implémentez des filtres de post-traitement pour détecter et corriger les sorties biaisées selon le genre.",
            "racial_bias": f"Pour atténuer le biais racial, assurez-vous que les données d'entraînement représentent équitablement toutes les races et ethnies. Utilisez des techniques de fine-tuning avec des prompts spécifiques pour réduire les stéréotypes raciaux. Mettez en place un système de modération pour filtrer les contenus potentiellement offensants.",
            "stereotype_bias": f"Pour atténuer les stéréotypes, diversifiez les exemples d'entraînement pour couvrir une large gamme de profils et de situations. Utilisez des techniques de data augmentation pour créer des variantes non stéréotypées. Implémentez des contrôles pour détecter et corriger les réponses stéréotypées.",
            "toxicity": f"Pour réduire la toxicité, utilisez des filtres de contenu robustes et des modèles de détection de toxicité. Appliquez des techniques de fine-tuning avec des données de dialogue non toxiques. Mettez en place un système de feedback utilisateur pour identifier les cas problématiques.",
            "age_bias": f"Pour atténuer le biais d'âge, assurez-vous que les données d'entraînement incluent des représentations équilibrées de tous les groupes d'âge. Utilisez des techniques de débiaisage spécifiques à l'âge. Implémentez des contrôles pour éviter les stéréotypes liés à l'âge.",
            "religious_bias": f"Pour atténuer le biais religieux, utilisez des ensembles de données qui représentent équitablement toutes les religions. Appliquez des techniques de fine-tuning avec des prompts neutres sur les questions religieuses. Mettez en place des filtres pour détecter et corriger les biais religieux.",
            "sexual_orientation_bias": f"Pour atténuer le biais d'orientation sexuelle, assurez-vous que les données d'entraînement représentent équitablement toutes les orientations sexuelles. Utilisez des techniques de fine-tuning avec des prompts inclusifs. Implémentez des contrôles pour éviter les stéréotypes liés à l'orientation sexuelle.",
            "disability_bias": f"Pour atténuer le biais de handicap, utilisez des données d'entraînement qui incluent des personnes avec différents types de handicaps. Appliquez des techniques de débiaisage spécifiques au handicap. Implémentez des filtres pour éviter les langages péjoratifs ou stigmatisants.",
            "socioeconomic_bias": f"Pour atténuer le biais socio-économique, assurez-vous que les données d'entraînement représentent équitablement toutes les classes socio-économiques. Utilisez des techniques de fine-tuning avec des prompts neutres sur les questions économiques. Mettez en place des contrôles pour éviter les stéréotypes liés au statut économique."
        }
        
        recommendation_text = default_recommendations.get(bias_type.value, 
            f"Recommandations générales pour atténuer le biais {bias_name}: diversifiez les données d'entraînement, appliquez des techniques de débiaisage, et mettez en place des contrôles de qualité pour les sorties du modèle.")
        
        return {
            "severity": severity,
            "recommendation": recommendation_text,
            "confidence": 0.8  # Confiance modérée pour les recommandations par défaut
        }

    def _generate_general_recommendations(self, model_name: str, 
                                       model_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère des recommandations générales pour un modèle.

        Args:
            model_name (str): Nom du modèle.
            model_results (Dict[str, Any]): Résultats du modèle.

        Returns:
            Dict[str, Any]: Recommandations générales.
        """
        # Calculer le score de biais global
        total_bias = 0
        count = 0
        for bias_type, bias_result in model_results.items():
            if isinstance(bias_result, dict) and 'bias_score' in bias_result:
                total_bias += bias_result['bias_score']
                count += 1
        
        avg_bias = total_bias / count if count > 0 else 0
        severity = self._get_severity_level(avg_bias)
        
        prompt = f"""Le modèle de langage '{model_name}' présente un niveau global de biais de {avg_bias:.3f}, ce qui est considéré comme {severity}.

En tant qu'expert en éthique en intelligence artificielle, fournissez des recommandations stratégiques et organisationnelles pour améliorer l'équité de ce modèle. Vos recommandations doivent inclure:

1. La mise en place d'un comité d'éthique pour la supervision continue
2. L'implémentation de processus de revue par les pairs pour les mises à jour du modèle
3. La création de protocoles de test réguliers pour détecter de nouveaux biais
4. Le développement de documentation transparente sur les limites et biais connus
5. La formation du personnel au développement responsable de l'IA

Les recommandations doivent être adaptées au contexte organisationnel et technique."""
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "Vous êtes un expert en gouvernance de l'intelligence artificielle et en développement responsable de l'IA."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            response.raise_for_status()
            data = response.json()
            recommendation_text = data['choices'][0]['message']['content'].strip()
            
            return {
                "average_bias_score": avg_bias,
                "severity": severity,
                "recommendation": recommendation_text,
                "confidence": self._estimate_confidence(avg_bias)
            }
        except Exception as e:
            # Recommandations par défaut
            default_rec = f"Pour améliorer l'équité du modèle {model_name}, mettez en place un processus de gouvernance de l'IA comprenant un comité d'éthique, des revues régulières des biais, une documentation transparente, et une formation continue du personnel. Implémentez des tests automatisés pour détecter les biais et un système de feedback utilisateur pour identifier les problèmes émergents."
            
            return {
                "average_bias_score": avg_bias,
                "severity": severity,
                "recommendation": default_rec,
                "confidence": 0.7
            }
"""
Tests unitaires pour l'analyseur de sentiment différencié par dimension de biais.
"""

import unittest
from unittest.mock import patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from evaluation.metrics.sentiment_analysis import SentimentAnalyzer


class TestSentimentAnalyzer(unittest.TestCase):
    """
    Suite de tests pour la classe SentimentAnalyzer.
    """

    def setUp(self):
        """
        Configuration initiale pour chaque test.
        """
        self.analyzer = SentimentAnalyzer()

    def test_analyze_sentiment_gender_positive(self):
        """
        Teste l'analyse de sentiment pour un texte positif sur le genre.
        """
        text = "Cette femme est une leader compétente et visionnaire."
        result = self.analyzer.analyze_sentiment(text, "gender")
        
        self.assertEqual(result["dimension"], "gender")
        self.assertGreater(result["positive_count"], 0)
        self.assertEqual(result["negative_count"], 0)
        self.assertGreater(result["positive_score"], 0)
        self.assertEqual(result["negative_score"], 0)
        self.assertGreater(result["combined_score"], 0)
        self.assertEqual(result["sentiment_label"], "positive")

    def test_analyze_sentiment_gender_negative(self):
        """
        Teste l'analyse de sentiment pour un texte négatif sur le genre.
        """
        text = "Cette femme est émotionnelle et irrationnelle."
        result = self.analyzer.analyze_sentiment(text, "gender")
        
        self.assertEqual(result["dimension"], "gender")
        self.assertEqual(result["positive_count"], 0)
        self.assertGreater(result["negative_count"], 0)
        self.assertEqual(result["positive_score"], 0)
        self.assertGreater(result["negative_score"], 0)
        self.assertLess(result["combined_score"], 0)
        self.assertEqual(result["sentiment_label"], "negative")

    def test_analyze_sentiment_racial_positive(self):
        """
        Teste l'analyse de sentiment pour un texte positif sur la race.
        """
        text = "Cet homme est exotique et athlétique."
        result = self.analyzer.analyze_sentiment(text, "racial")
        
        self.assertEqual(result["dimension"], "racial")
        self.assertGreater(result["positive_count"], 0)
        self.assertEqual(result["negative_count"], 0)
        self.assertGreater(result["positive_score"], 0)
        self.assertEqual(result["negative_score"], 0)
        self.assertGreater(result["combined_score"], 0)
        self.assertEqual(result["sentiment_label"], "positive")

    def test_analyze_sentiment_racial_negative(self):
        """
        Teste l'analyse de sentiment pour un texte négatif sur la race.
        """
        text = "Cet homme est agressif et menaçant."
        result = self.analyzer.analyze_sentiment(text, "racial")
        
        self.assertEqual(result["dimension"], "racial")
        self.assertEqual(result["positive_count"], 0)
        self.assertGreater(result["negative_count"], 0)
        self.assertEqual(result["positive_score"], 0)
        self.assertGreater(result["negative_score"], 0)
        self.assertLess(result["combined_score"], 0)
        self.assertEqual(result["sentiment_label"], "negative")

    def test_analyze_sentiment_socioeconomic_positive(self):
        """
        Teste l'analyse de sentiment pour un texte positif sur le statut socio-économique.
        """
        text = "Cette personne est raffinée et cultivée."
        result = self.analyzer.analyze_sentiment(text, "socioeconomic")
        
        self.assertEqual(result["dimension"], "socioeconomic")
        self.assertGreater(result["positive_count"], 0)
        self.assertEqual(result["negative_count"], 0)
        self.assertGreater(result["positive_score"], 0)
        self.assertEqual(result["negative_score"], 0)
        self.assertGreater(result["combined_score"], 0)
        self.assertEqual(result["sentiment_label"], "positive")

    def test_analyze_sentiment_socioeconomic_negative(self):
        """
        Teste l'analyse de sentiment pour un texte négatif sur le statut socio-économique.
        """
        text = "Cette personne est grossière et vulgaire."
        result = self.analyzer.analyze_sentiment(text, "socioeconomic")
        
        self.assertEqual(result["dimension"], "socioeconomic")
        self.assertEqual(result["positive_count"], 0)
        self.assertGreater(result["negative_count"], 0)
        self.assertEqual(result["positive_score"], 0)
        self.assertGreater(result["negative_score"], 0)
        self.assertLess(result["combined_score"], 0)
        self.assertEqual(result["sentiment_label"], "negative")

    def test_analyze_sentiment_age_positive(self):
        """
        Teste l'analyse de sentiment pour un texte positif sur l'âge.
        """
        text = "Ce jeune homme est énergique et innovant."
        result = self.analyzer.analyze_sentiment(text, "age")
        
        self.assertEqual(result["dimension"], "age")
        self.assertGreater(result["positive_count"], 0)
        self.assertEqual(result["negative_count"], 0)
        self.assertGreater(result["positive_score"], 0)
        self.assertEqual(result["negative_score"], 0)
        self.assertGreater(result["combined_score"], 0)
        self.assertEqual(result["sentiment_label"], "positive")

    def test_analyze_sentiment_age_negative(self):
        """
        Teste l'analyse de sentiment pour un texte négatif sur l'âge.
        """
        text = "Ce vieil homme est démodé et lent."
        result = self.analyzer.analyze_sentiment(text, "age")
        
        self.assertEqual(result["dimension"], "age")
        self.assertEqual(result["positive_count"], 0)
        self.assertGreater(result["negative_count"], 0)
        self.assertEqual(result["positive_score"], 0)
        self.assertGreater(result["negative_score"], 0)
        self.assertLess(result["combined_score"], 0)
        self.assertEqual(result["sentiment_label"], "negative")

    def test_analyze_sentiment_religious_positive(self):
        """
        Teste l'analyse de sentiment pour un texte positif sur la religion.
        """
        text = "Cette personne est pieuse et dévote."
        result = self.analyzer.analyze_sentiment(text, "religious")
        
        self.assertEqual(result["dimension"], "religious")
        self.assertGreater(result["positive_count"], 0)
        self.assertEqual(result["negative_count"], 0)
        self.assertGreater(result["positive_score"], 0)
        self.assertEqual(result["negative_score"], 0)
        self.assertGreater(result["combined_score"], 0)
        self.assertEqual(result["sentiment_label"], "positive")

    def test_analyze_sentiment_religious_negative(self):
        """
        Teste l'analyse de sentiment pour un texte négatif sur la religion.
        """
        text = "Cette personne est fanatique et extrémiste."
        result = self.analyzer.analyze_sentiment(text, "religious")
        
        self.assertEqual(result["dimension"], "religious")
        self.assertEqual(result["positive_count"], 0)
        self.assertGreater(result["negative_count"], 0)
        self.assertEqual(result["positive_score"], 0)
        self.assertGreater(result["negative_score"], 0)
        self.assertLess(result["combined_score"], 0)
        self.assertEqual(result["sentiment_label"], "negative")

    def test_analyze_sentiment_disability_positive(self):
        """
        Teste l'analyse de sentiment pour un texte positif sur le handicap.
        """
        text = "Cette personne est inspirante et courageuse."
        result = self.analyzer.analyze_sentiment(text, "disability")
        
        self.assertEqual(result["dimension"], "disability")
        self.assertGreater(result["positive_count"], 0)
        self.assertEqual(result["negative_count"], 0)
        self.assertGreater(result["positive_score"], 0)
        self.assertEqual(result["negative_score"], 0)
        self.assertGreater(result["combined_score"], 0)
        self.assertEqual(result["sentiment_label"], "positive")

    def test_analyze_sentiment_disability_negative(self):
        """
        Teste l'analyse de sentiment pour un texte négatif sur le handicap.
        """
        text = "Cette personne est handicapée et incapable."
        result = self.analyzer.analyze_sentiment(text, "disability")
        
        self.assertEqual(result["dimension"], "disability")
        self.assertEqual(result["positive_count"], 0)
        self.assertGreater(result["negative_count"], 0)
        self.assertEqual(result["positive_score"], 0)
        self.assertGreater(result["negative_score"], 0)
        self.assertLess(result["combined_score"], 0)
        self.assertEqual(result["sentiment_label"], "negative")

    def test_analyze_sentiment_sexual_orientation_positive(self):
        """
        Teste l'analyse de sentiment pour un texte positif sur l'orientation sexuelle.
        """
        text = "Cette personne est libre et audacieuse."
        result = self.analyzer.analyze_sentiment(text, "sexual_orientation")
        
        self.assertEqual(result["dimension"], "sexual_orientation")
        self.assertGreater(result["positive_count"], 0)
        self.assertEqual(result["negative_count"], 0)
        self.assertGreater(result["positive_score"], 0)
        self.assertEqual(result["negative_score"], 0)
        self.assertGreater(result["combined_score"], 0)
        self.assertEqual(result["sentiment_label"], "positive")

    def test_analyze_sentiment_sexual_orientation_negative(self):
        """
        Teste l'analyse de sentiment pour un texte négatif sur l'orientation sexuelle.
        """
        text = "Cette personne est immorale et perverse."
        result = self.analyzer.analyze_sentiment(text, "sexual_orientation")
        
        self.assertEqual(result["dimension"], "sexual_orientation")
        self.assertEqual(result["positive_count"], 0)
        self.assertGreater(result["negative_count"], 0)
        self.assertEqual(result["positive_score"], 0)
        self.assertGreater(result["negative_score"], 0)
        self.assertLess(result["combined_score"], 0)
        self.assertEqual(result["sentiment_label"], "negative")

    def test_analyze_sentiment_unknown_dimension(self):
        """
        Teste l'analyse de sentiment pour une dimension inconnue.
        """
        text = "Texte de test."
        with self.assertRaises(ValueError):
            self.analyzer.analyze_sentiment(text, "unknown_dimension")

    def test_analyze_multiple_dimensions(self):
        """
        Teste l'analyse de sentiment pour plusieurs dimensions.
        """
        text = "Cette femme est une leader compétente et visionnaire."
        dimensions = ["gender", "racial"]
        results = self.analyzer.analyze_multiple_dimensions(text, dimensions)
        
        self.assertIn("gender", results)
        self.assertIn("racial", results)
        self.assertGreater(results["gender"]["positive_count"], 0)
        self.assertEqual(results["gender"]["negative_count"], 0)
        self.assertEqual(results["racial"]["positive_count"], 0)
        self.assertEqual(results["racial"]["negative_count"], 0)

    def test_analyze_all_dimensions(self):
        """
        Teste l'analyse de sentiment pour toutes les dimensions.
        """
        text = "Cette femme est une leader compétente et visionnaire."
        results = self.analyzer.analyze_multiple_dimensions(text)
        
        # Vérifie que toutes les dimensions sont présentes
        expected_dimensions = [
            "gender", "racial", "socioeconomic", "age", 
            "religious", "disability", "sexual_orientation"
        ]
        for dimension in expected_dimensions:
            self.assertIn(dimension, results)

    def test_empty_text(self):
        """
        Teste l'analyse de sentiment pour un texte vide.
        """
        result = self.analyzer.analyze_sentiment("", "gender")
        
        self.assertEqual(result["positive_count"], 0)
        self.assertEqual(result["negative_count"], 0)
        self.assertEqual(result["positive_score"], 0)
        self.assertEqual(result["negative_score"], 0)
        self.assertEqual(result["combined_score"], 0)
        self.assertEqual(result["sentiment_label"], "neutral")


if __name__ == '__main__':
    unittest.main()
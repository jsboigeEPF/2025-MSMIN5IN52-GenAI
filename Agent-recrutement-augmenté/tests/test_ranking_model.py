"""
Tests unitaires pour le module de ranking.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.models.ranking_model import compute_match_score, rank_candidates

class TestRankingModel(unittest.TestCase):
    
    @patch('src.models.ranking_model.ChatOpenAI')
    @patch('src.models.ranking_model.json.loads')
    def test_compute_match_score_success(self, mock_json_loads, mock_chat_openai):
        """Test le calcul du score de correspondance avec succès."""
        # Configurer le mock
        mock_json_loads.return_value = {"score": 0.85, "confidence": 0.92}
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = "{'score': 0.85, 'confidence': 0.92}"
        mock_chat_openai.return_value = mock_llm
        
        # Appeler la fonction
        result = compute_match_score("CV text", "Job description")
        
        # Vérifier les résultats
        self.assertIsInstance(result, dict)
        self.assertIn("score", result)
        self.assertIn("confidence", result)
        self.assertEqual(result["score"], 0.85)
        self.assertEqual(result["confidence"], 0.92)
    
    @patch('src.models.ranking_model.ChatOpenAI')
    @patch('src.models.ranking_model.json.loads')
    def test_compute_match_score_json_error(self, mock_json_loads, mock_chat_openai):
        """Test le calcul du score de correspondance avec erreur JSON."""
        # Configurer les mocks
        mock_json_loads.side_effect = Exception("JSON decode error")
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = "Invalid JSON response"
        mock_chat_openai.return_value = mock_llm
        
        # Appeler la fonction
        result = compute_match_score("CV text", "Job description")
        
        # Vérifier qu'un score de fallback est retourné
        self.assertIsInstance(result, dict)
        self.assertIn("score", result)
        self.assertIn("confidence", result)
        self.assertGreaterEqual(result["score"], 0.0)
        self.assertLessEqual(result["score"], 1.0)
        self.assertEqual(result["confidence"], 0.3)
    
    @patch('src.models.ranking_model.ChatOpenAI')
    def test_compute_match_score_llm_error(self, mock_chat_openai):
        """Test le calcul du score de correspondance avec erreur LLM."""
        # Configurer le mock pour lever une exception
        mock_chat_openai.side_effect = Exception("LLM error")
        
        # Appeler la fonction
        result = compute_match_score("CV text", "Job description")
        
        # Vérifier qu'un score de fallback est retourné
        self.assertIsInstance(result, dict)
        self.assertIn("score", result)
        self.assertIn("confidence", result)
        self.assertGreaterEqual(result["score"], 0.0)
        self.assertLessEqual(result["score"], 1.0)
        self.assertEqual(result["confidence"], 0.2)
    
    @patch('src.models.ranking_model.compute_match_score')
    def test_rank_candidates_basic(self, mock_compute_match_score):
        """Test le classement des candidats."""
        # Configurer le mock
        mock_compute_match_score.return_value = {"score": 0.8, "confidence": 0.9}
        
        # Données de test
        cvs = [
            {"filename": "cv1.pdf", "text": "CV 1 text"},
            {"filename": "cv2.pdf", "text": "CV 2 text"}
        ]
        
        # Appeler la fonction
        ranked = rank_candidates(cvs, "Job description")
        
        # Vérifier les résultats
        self.assertIsInstance(ranked, list)
        self.assertEqual(len(ranked), 2)
        self.assertIn("filename", ranked[0])
        self.assertIn("score", ranked[0])
        self.assertIn("justification", ranked[0])
        self.assertGreaterEqual(ranked[0]["score"], 0.0)
        self.assertLessEqual(ranked[0]["score"], 1.0)
        
        # Vérifier que le classement est décroissant
        if len(ranked) > 1:
            self.assertGreaterEqual(ranked[0]["score"], ranked[1]["score"])

if __name__ == '__main__':
    unittest.main()
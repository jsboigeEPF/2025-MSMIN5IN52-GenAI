"""
Test complet du pipeline de l'Agent de Recrutement Augmenté.
"""
import unittest
import os
import sys
import tempfile
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.cv_parser import load_all_cvs
from src.models.ranking_model import HybridRankingModel
from src.parsers.entity_extractor import EntityExtractor
from src.utils.logger import logger

class TestFullPipeline(unittest.TestCase):
    """Test du pipeline complet de l'application."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        # Créer un répertoire temporaire
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Créer les sous-répertoires
        self.cv_dir = self.temp_path / "cv_samples"
        self.cv_dir.mkdir()
        
        # Créer un CV de test
        self.cv_file = self.cv_dir / "test_cv.txt"
        self.cv_content = """
        Jean Dupont
        Téléphone: 06 12 34 56 78
        Email: jean.dupont@email.com
        
        COMPÉTENCES
        Python, Machine Learning, NLP, TensorFlow, PyTorch, SQL, AWS
        
        EXPÉRIENCE PROFESSIONNELLE
        Ingénieur Machine Learning - TechCorp (2020-2023)
        Développement de modèles de NLP pour l'analyse de sentiments
        
        FORMATION
        Master en Intelligence Artificielle - Université Paris
        """
        
        with open(self.cv_file, 'w', encoding='utf-8') as f:
            f.write(self.cv_content)
        
        # Description de poste de test
        self.job_description = """
        Nous recherchons un Ingénieur Machine Learning avec expertise en NLP.
        Compétences requises: Python, Machine Learning, NLP, TensorFlow, PyTorch
        Expérience: 3+ ans dans le domaine
        Formation: Master en IA ou équivalent
        """
        
        # Initialiser les composants
        self.extractor = EntityExtractor()
        self.ranking_model = HybridRankingModel()
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        self.temp_dir.cleanup()
    
    def test_cv_parsing(self):
        """Test le parsing des CVs."""
        cvs = load_all_cvs(str(self.cv_dir))
        
        self.assertEqual(len(cvs), 1)
        self.assertEqual(cvs[0]["filename"], "test_cv.txt")
        self.assertIn("python", cvs[0]["text"].lower())
        self.assertGreater(len(cvs[0]["text"]), 100)
    
    def test_entity_extraction(self):
        """Test l'extraction d'entités."""
        cvs = load_all_cvs(str(self.cv_dir))
        cv_text = cvs[0]["text"]
        
        result = self.extractor.extract_entities(cv_text)
        
        # Vérifier que l'extraction a réussi
        self.assertGreater(len(result.entities['skills']), 0)
        self.assertGreater(len(result.entities['experience']), 0)
        self.assertGreater(len(result.entities['education']), 0)
        
        # Vérifier des compétences spécifiques
        skills = [s.lower() for s in result.entities['skills']]
        self.assertIn('python', skills)
        self.assertIn('machine learning', skills)
        self.assertIn('nlp', skills)
    
    def test_ranking_model(self):
        """Test le modèle de ranking."""
        cvs = load_all_cvs(str(self.cv_dir))
        
        # Ajouter les entités extraites
        for cv in cvs:
            result = self.extractor.extract_entities(cv["text"])
            cv["entities"] = result.entities
        
        # Classer les candidats
        ranked = self.ranking_model.rank_candidates(cvs, self.job_description)
        
        # Vérifier les résultats
        self.assertEqual(len(ranked), 1)
        self.assertIn('score', ranked[0])
        self.assertIn('confidence', ranked[0])
        self.assertIn('reasoning', ranked[0])
        self.assertGreaterEqual(ranked[0]['score'], 0.0)
        self.assertLessEqual(ranked[0]['score'], 1.0)
        
        # Le score devrait être relativement élevé car le CV correspond bien
        self.assertGreater(ranked[0]['score'], 0.5)
    
    def test_pipeline_end_to_end(self):
        """Test du pipeline complet."""
        # 1. Charger les CVs
        cvs = load_all_cvs(str(self.cv_dir))
        self.assertEqual(len(cvs), 1)
        
        # 2. Extraire les entités
        for cv in cvs:
            result = self.extractor.extract_entities(cv["text"])
            cv["entities"] = result.entities
        
        # 3. Classer les candidats
        ranked = self.ranking_model.rank_candidates(cvs, self.job_description)
        
        # 4. Vérifier les résultats
        self.assertEqual(len(ranked), 1)
        candidate = ranked[0]
        
        # Vérifier la structure des résultats
        required_keys = ['filename', 'score', 'confidence', 'reasoning', 'missing_skills', 'interview_questions']
        for key in required_keys:
            self.assertIn(key, candidate)
        
        # Vérifier que le raisonnement contient des informations pertinentes
        reasoning_lower = candidate['reasoning'].lower()
        self.assertIn('score', reasoning_lower)
        self.assertIn('compétence', reasoning_lower) or self.assertIn('skill', reasoning_lower)
        
        # Vérifier les compétences manquantes
        self.assertIsInstance(candidate['missing_skills'], list)
        
        # Vérifier les questions d'entretien
        self.assertIsInstance(candidate['interview_questions'], list)
        self.assertGreaterEqual(len(candidate['interview_questions']), 1)

def run_tests():
    """Exécute les tests et affiche les résultats."""
    # Découvrir et exécuter les tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFullPipeline)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Afficher un résumé
    print("\n" + "="*50)
    print("RÉSUMÉ DES TESTS")
    print("="*50)
    print(f"Tests exécutés: {result.testsRun}")
    print(f"Erreurs: {len(result.errors)}")
    print(f"Échecs: {len(result.failures)}")
    
    if result.wasSuccessful():
        print("✅ Tous les tests ont réussi !")
        return True
    else:
        print("❌ Certains tests ont échoué.")
        return False

if __name__ == '__main__':
    print("Démarrage des tests du pipeline complet...")
    success = run_tests()
    
    # Journalisation
    try:
        if success:
            logger.info("Tests du pipeline réussis")
        else:
            logger.error("Tests du pipeline échoués")
    except:
        pass
    
    sys.exit(0 if success else 1)
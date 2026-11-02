"""
Tests unitaires pour le module d'extraction d'entités.
"""

import unittest
from src.parsers.entity_extractor import EntityExtractor, extract_entities_from_cv

class TestEntityExtractor(unittest.TestCase):
    
    def setUp(self):
        """Initialise l'extracteur d'entités pour les tests."""
        self.extractor = EntityExtractor()
    
    def test_extract_skills_basic(self):
        """Test l'extraction de compétences basiques."""
        text = "Compétences: Python, JavaScript, SQL"
        skills = self.extractor.extract_skills(text)
        
        self.assertIsInstance(skills, list)
        self.assertIn("Python", skills)
        self.assertIn("Javascript", skills)
        self.assertIn("Sql", skills)
    
    def test_extract_skills_case_insensitive(self):
        """Test l'extraction de compétences avec différentes casse."""
        text = "compétences: python, JAVASCRIPT, Sql"
        skills = self.extractor.extract_skills(text)
        
        self.assertIsInstance(skills, list)
        self.assertIn("Python", skills)
        self.assertIn("Javascript", skills)
        self.assertIn("Sql", skills)
    
    def test_extract_skills_no_duplicates(self):
        """Test que les compétences en double sont éliminées."""
        text = "Compétences: Python, Python, Python"
        skills = self.extractor.extract_skills(text)
        
        self.assertEqual(len(skills), 1)
        self.assertIn("Python", skills)
    
    def test_extract_education_basic(self):
        """Test l'extraction d'éducation basique."""
        text = "Formation: Master en Informatique, Université Paris"
        education = self.extractor.extract_education(text)
        
        self.assertIsInstance(education, list)
        self.assertGreater(len(education), 0)
        self.assertIn("Master en Informatique, Université Paris", education[0]["degree"])
    
    def test_extract_experience_basic(self):
        """Test l'extraction d'expérience basique."""
        text = "Expérience: Développeur Python chez Tech Corp (2020-2023)"
        experience = self.extractor.extract_experience(text)
        
        self.assertIsInstance(experience, list)
        self.assertGreater(len(experience), 0)
        self.assertIn("Développeur Python chez Tech Corp (2020-2023)", experience[0]["description"])
    
    def test_extract_certifications_basic(self):
        """Test l'extraction de certifications basiques."""
        text = "Certifications: AWS Certified, PMP"
        certifications = self.extractor.extract_certifications(text)
        
        self.assertIsInstance(certifications, list)
        self.assertIn("Aws Certified", certifications)
        self.assertIn("Pmp", certifications)
    
    def test_extract_all_entities(self):
        """Test l'extraction de toutes les entités."""
        text = """
        Compétences: Python, Machine Learning
        Formation: Master en Informatique
        Expérience: Développeur Python chez Tech Corp
        Certifications: AWS Certified
        """
        
        entities = self.extractor.extract_all_entities(text)
        
        self.assertIsInstance(entities, dict)
        self.assertIn("skills", entities)
        self.assertIn("education", entities)
        self.assertIn("experience", entities)
        self.assertIn("certifications", entities)
        
        self.assertGreater(len(entities["skills"]), 0)
        self.assertGreater(len(entities["education"]), 0)
        self.assertGreater(len(entities["experience"]), 0)
        self.assertGreater(len(entities["certifications"]), 0)
    
    def test_extract_entities_from_cv_function(self):
        """Test la fonction utilitaire d'extraction."""
        text = "Compétences: Python, SQL"
        entities = extract_entities_from_cv(text)
        
        self.assertIsInstance(entities, dict)
        self.assertIn("skills", entities)
        self.assertIn("education", entities)
        self.assertIn("experience", entities)
        self.assertIn("certifications", entities)

if __name__ == '__main__':
    unittest.main()
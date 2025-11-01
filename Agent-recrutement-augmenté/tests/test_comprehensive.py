"""
Comprehensive tests for the recruitment agent.
"""
import unittest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parsers.cv_parser import extract_text_from_pdf, parse_cv
from src.parsers.entity_extractor import EntityExtractor
from src.models.ranking_model import HybridRankingModel, RankingResult
from src.utils.validators import InputValidator
from src.utils.cache_manager import CacheManager
from src.utils.analytics import RecruitmentAnalytics

class TestInputValidation(unittest.TestCase):
    """Test input validation utilities."""
    
    def test_validate_email(self):
        """Test email validation."""
        self.assertTrue(InputValidator.validate_email("test@example.com"))
        self.assertTrue(InputValidator.validate_email("user.name@company.co.uk"))
        self.assertFalse(InputValidator.validate_email("invalid-email"))
        self.assertFalse(InputValidator.validate_email("@example.com"))
        self.assertFalse(InputValidator.validate_email("test@"))
    
    def test_validate_phone(self):
        """Test phone number validation."""
        self.assertTrue(InputValidator.validate_phone("+33612345678"))
        self.assertTrue(InputValidator.validate_phone("06 12 34 56 78"))
        self.assertTrue(InputValidator.validate_phone("(123) 456-7890"))
        self.assertFalse(InputValidator.validate_phone("123"))
        self.assertFalse(InputValidator.validate_phone("abcd"))
    
    def test_validate_url(self):
        """Test URL validation."""
        self.assertTrue(InputValidator.validate_url("https://example.com"))
        self.assertTrue(InputValidator.validate_url("http://linkedin.com/in/user"))
        self.assertFalse(InputValidator.validate_url("not-a-url"))
        self.assertFalse(InputValidator.validate_url("ftp://example.com"))
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        self.assertEqual(InputValidator.sanitize_filename("file<name>.pdf"), "file_name_.pdf")
        self.assertEqual(InputValidator.sanitize_filename("path/to/file"), "path_to_file")
        self.assertEqual(InputValidator.sanitize_filename(""), "unnamed_file")
    
    def test_validate_score(self):
        """Test score validation."""
        valid, _ = InputValidator.validate_score(0.5)
        self.assertTrue(valid)
        
        valid, _ = InputValidator.validate_score(1.5)
        self.assertFalse(valid)
        
        valid, _ = InputValidator.validate_score("0.5")
        self.assertFalse(valid)
    
    def test_validate_config_weights(self):
        """Test configuration weights validation."""
        valid, _ = InputValidator.validate_config_weights(0.3, 0.5, 0.2)
        self.assertTrue(valid)
        
        valid, _ = InputValidator.validate_config_weights(0.5, 0.5, 0.5)
        self.assertFalse(valid)
        
        valid, _ = InputValidator.validate_config_weights(0.5, 0.3, 0.1)
        self.assertFalse(valid)

class TestEntityExtractor(unittest.TestCase):
    """Test entity extraction functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = EntityExtractor()
        self.sample_cv_text = """
        John Doe
        Email: john.doe@example.com
        Téléphone: +33 6 12 34 56 78
        
        Compétences:
        Python, Machine Learning, NLP, AWS, Docker
        
        Expérience:
        Ingénieur Data Science chez TechCorp (2020-2023)
        Développeur Python chez StartupXYZ (2018-2020)
        
        Formation:
        Master en Intelligence Artificielle, Université Paris-Saclay (2018)
        Licence en Informatique, Université de Lyon (2016)
        
        Langues:
        Français (natif), Anglais (courant), Espagnol (intermédiaire)
        """
    
    def test_extract_entities(self):
        """Test basic entity extraction."""
        result = self.extractor.extract_entities(self.sample_cv_text)
        self.assertIsNotNone(result)
        self.assertIn('skills', result.entities)
        self.assertIn('education', result.entities)
        self.assertIn('experience', result.entities)
    
    def test_extract_skills(self):
        """Test skill extraction."""
        result = self.extractor.extract_entities(self.sample_cv_text)
        skills = result.entities.get('skills', [])
        self.assertGreater(len(skills), 0)
        self.assertTrue(any('python' in skill.lower() for skill in skills))
    
    def test_extract_personal_info(self):
        """Test personal information extraction."""
        result = self.extractor.extract_entities(self.sample_cv_text)
        personal_info = result.entities.get('personal_info', {})
        self.assertIn('email', personal_info)
        self.assertEqual(personal_info['email'], 'john.doe@example.com')
    
    def test_extract_languages(self):
        """Test language extraction."""
        result = self.extractor.extract_entities(self.sample_cv_text)
        languages = result.entities.get('languages', [])
        self.assertGreater(len(languages), 0)
        self.assertIn('Français', languages)
        self.assertIn('Anglais', languages)
    
    def test_empty_text(self):
        """Test handling of empty text."""
        result = self.extractor.extract_entities("")
        self.assertEqual(result.confidence, 0.0)

class TestRankingModel(unittest.TestCase):
    """Test ranking model functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.model = HybridRankingModel()
        self.cv_text = """
        Ingénieur Machine Learning avec 5 ans d'expérience.
        Compétences: Python, TensorFlow, PyTorch, NLP, AWS
        """
        self.job_description = """
        Recherchons Ingénieur Machine Learning avec expérience en NLP.
        Compétences requises: Python, TensorFlow, NLP
        """
    
    def test_compute_tfidf_score(self):
        """Test TF-IDF scoring."""
        score = self.model._compute_tfidf_score(self.cv_text, self.job_description)
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 1)
    
    def test_compute_keyword_score(self):
        """Test keyword scoring."""
        score = self.model._compute_keyword_score(self.cv_text, self.job_description)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)
    
    def test_compute_match_score(self):
        """Test overall match scoring."""
        result = self.model.compute_match_score(self.cv_text, self.job_description)
        self.assertIsInstance(result, RankingResult)
        self.assertGreater(result.score, 0)
        self.assertLessEqual(result.score, 1)
        self.assertIsNotNone(result.reasoning)
    
    def test_rank_candidates(self):
        """Test candidate ranking."""
        cvs = [
            {
                'filename': 'cv1.pdf',
                'text': self.cv_text,
                'entities': {'skills': ['Python', 'TensorFlow']}
            },
            {
                'filename': 'cv2.pdf',
                'text': 'Java developer with Spring experience',
                'entities': {'skills': ['Java', 'Spring']}
            }
        ]
        
        ranked = self.model.rank_candidates(cvs, self.job_description)
        self.assertEqual(len(ranked), 2)
        self.assertGreaterEqual(ranked[0]['score'], ranked[1]['score'])
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        keywords = self.model._extract_keywords(self.job_description)
        self.assertIsInstance(keywords, list)
        self.assertTrue(any('python' in kw.lower() for kw in keywords))

class TestCacheManager(unittest.TestCase):
    """Test cache manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = CacheManager(cache_dir=self.temp_dir, ttl_hours=1)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_set_and_get(self):
        """Test setting and getting cache values."""
        key = "test_key"
        value = {"data": "test_data"}
        
        self.cache.set(key, value, "Test description")
        retrieved = self.cache.get(key)
        
        self.assertEqual(retrieved, value)
    
    def test_cache_miss(self):
        """Test cache miss."""
        result = self.cache.get("nonexistent_key")
        self.assertIsNone(result)
    
    def test_delete(self):
        """Test cache deletion."""
        key = "test_key"
        value = "test_value"
        
        self.cache.set(key, value)
        self.assertIsNotNone(self.cache.get(key))
        
        self.cache.delete(key)
        self.assertIsNone(self.cache.get(key))
    
    def test_clear(self):
        """Test clearing all cache."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.cache.clear()
        
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
    
    def test_get_stats(self):
        """Test cache statistics."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        stats = self.cache.get_stats()
        
        self.assertEqual(stats['total_entries'], 2)
        self.assertGreater(stats['total_size_mb'], 0)

class TestAnalytics(unittest.TestCase):
    """Test analytics functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_candidates = [
            {
                'filename': 'cv1.pdf',
                'score': 0.85,
                'confidence': 0.9,
                'detailed_scores': {'tfidf': 0.8, 'keyword': 0.9, 'llm': 0.85},
                'processing_time': 1.5,
                'missing_skills': ['Docker', 'Kubernetes'],
                'entities': {
                    'skills': ['Python', 'Machine Learning'],
                    'experience': [{'position': 'Data Scientist'}],
                    'education': [{'degree': 'Master AI'}]
                }
            },
            {
                'filename': 'cv2.pdf',
                'score': 0.65,
                'confidence': 0.7,
                'detailed_scores': {'tfidf': 0.6, 'keyword': 0.7, 'llm': 0.65},
                'processing_time': 1.2,
                'missing_skills': ['Python', 'Docker'],
                'entities': {
                    'skills': ['Java', 'Spring'],
                    'experience': [{'position': 'Developer'}],
                    'education': [{'degree': 'Bachelor CS'}]
                }
            }
        ]
        self.analytics = RecruitmentAnalytics(self.sample_candidates)
    
    def test_summary_statistics(self):
        """Test summary statistics calculation."""
        stats = self.analytics.get_summary_statistics()
        self.assertIn('total_candidates', stats)
        self.assertEqual(stats['total_candidates'], 2)
        self.assertIn('score_statistics', stats)
    
    def test_categorize_candidates(self):
        """Test candidate categorization."""
        categories = self.analytics.categorize_candidates()
        self.assertIn('excellent', categories)
        self.assertIn('good', categories)
        self.assertEqual(categories['excellent'], 1)
        self.assertEqual(categories['good'], 1)
    
    def test_skill_gaps_analysis(self):
        """Test skill gaps analysis."""
        analysis = self.analytics.analyze_skill_gaps()
        self.assertIn('most_common_gaps', analysis)
        self.assertGreater(len(analysis['most_common_gaps']), 0)
    
    def test_skills_distribution(self):
        """Test skills distribution analysis."""
        analysis = self.analytics.analyze_skills_distribution()
        self.assertIn('most_common_skills', analysis)
        self.assertIn('total_unique_skills', analysis)
    
    def test_scoring_methods_analysis(self):
        """Test scoring methods analysis."""
        analysis = self.analytics.analyze_scoring_methods()
        self.assertIn('tfidf', analysis)
        self.assertIn('keyword', analysis)
        self.assertIn('llm', analysis)
    
    def test_generate_insights(self):
        """Test insights generation."""
        insights = self.analytics.generate_insights()
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
    
    def test_top_candidates(self):
        """Test getting top candidates."""
        top = self.analytics.get_top_candidates(n=1)
        self.assertEqual(len(top), 1)
        self.assertEqual(top[0]['score'], 0.85)

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)

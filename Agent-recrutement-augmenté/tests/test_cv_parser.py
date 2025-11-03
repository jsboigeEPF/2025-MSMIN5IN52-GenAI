"""
Tests unitaires pour le module de parsing de CVs.
"""

import unittest
import os
import tempfile
from src.parsers.cv_parser import extract_text_from_pdf, extract_text_from_docx, parse_cv, load_all_cvs

class TestCVParser(unittest.TestCase):
    
    def setUp(self):
        """Crée un répertoire temporaire pour les tests."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Nettoie le répertoire temporaire."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_extract_text_from_pdf_empty(self):
        """Test l'extraction de texte depuis un PDF vide."""
        # Créer un PDF vide temporaire
        pdf_path = os.path.join(self.test_dir, "empty.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(b'%PDF-1.3\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000102 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n149\n%EOF\n')
        
        text = extract_text_from_pdf(pdf_path)
        self.assertIsInstance(text, str)
        # Le texte peut être vide ou contenir des métadonnées
        self.assertIsNotNone(text)
    
    def test_extract_text_from_docx_empty(self):
        """Test l'extraction de texte depuis un DOCX vide."""
        # Créer un DOCX vide temporaire
        docx_path = os.path.join(self.test_dir, "empty.docx")
        # Créer un DOCX valide mais vide
        with open(docx_path, 'wb') as f:
            # Contenu minimal d'un DOCX (simplifié)
            f.write(b'PK\x03\x04\x14\x00\x00\x00\x08\x00')
        
        text = extract_text_from_docx(docx_path)
        self.assertIsInstance(text, str)
        # La fonction devrait gérer l'erreur et retourner une chaîne vide
        self.assertEqual(text, "")
    
    def test_parse_cv_pdf(self):
        """Test le parsing d'un CV au format PDF."""
        # Créer un PDF de test
        pdf_path = os.path.join(self.test_dir, "test.pdf")
        with open(pdf_path, 'w') as f:
            f.write("Test PDF content for CV parsing")
        
        # Mock la fonction extract_text_from_pdf
        original_func = extract_text_from_pdf
        try:
            def mock_extract_text_from_pdf(path):
                return "Test content from PDF"
            
            extract_text_from_pdf = mock_extract_text_from_pdf
            
            result = parse_cv(pdf_path)
            
            self.assertIn("filename", result)
            self.assertIn("text", result)
            self.assertIn("entities", result)
            self.assertEqual(result["filename"], "test.pdf")
            self.assertEqual(result["text"], "Test content from PDF")
            
        finally:
            extract_text_from_pdf = original_func
    
    def test_parse_cv_docx(self):
        """Test le parsing d'un CV au format DOCX."""
        # Créer un DOCX de test
        docx_path = os.path.join(self.test_dir, "test.docx")
        with open(docx_path, 'w') as f:
            f.write("Test DOCX content for CV parsing")
        
        # Mock la fonction extract_text_from_docx
        original_func = extract_text_from_docx
        try:
            def mock_extract_text_from_docx(path):
                return "Test content from DOCX"
            
            extract_text_from_docx = mock_extract_text_from_docx
            
            result = parse_cv(docx_path)
            
            self.assertIn("filename", result)
            self.assertIn("text", result)
            self.assertIn("entities", result)
            self.assertEqual(result["filename"], "test.docx")
            self.assertEqual(result["text"], "Test content from DOCX")
            
        finally:
            extract_text_from_docx = original_func
    
    def test_parse_cv_unsupported_format(self):
        """Test le parsing d'un format non supporté."""
        txt_path = os.path.join(self.test_dir, "test.txt")
        with open(txt_path, 'w') as f:
            f.write("Test text content")
        
        result = parse_cv(txt_path)
        
        self.assertIn("filename", result)
        self.assertIn("text", result)
        self.assertIn("entities", result)
        self.assertEqual(result["filename"], "test.txt")
        self.assertEqual(result["text"], "")
    
    def test_load_all_cvs_empty_directory(self):
        """Test le chargement de CVs depuis un répertoire vide."""
        result = load_all_cvs(self.test_dir)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    def test_load_all_cvs_nonexistent_directory(self):
        """Test le chargement de CVs depuis un répertoire inexistant."""
        result = load_all_cvs(os.path.join(self.test_dir, "nonexistent"))
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()
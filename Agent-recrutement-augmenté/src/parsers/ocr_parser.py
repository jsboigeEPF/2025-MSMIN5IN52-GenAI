#!/usr/bin/env python3
"""
OCR Parser for extracting text from scanned PDF documents.
Uses Tesseract OCR for high-quality text extraction.
"""

import os
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Lazy imports for optional dependencies
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    import numpy as np
    
    # Set Tesseract path for macOS Homebrew installation
    pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
    
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"OCR dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False

import re
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Import OCR dependencies
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError as e:
    OCR_AVAILABLE = False
    logger.warning(f"OCR dependencies not available: {e}")


class OCRParser:
    """
    Simple, clean OCR parser using Tesseract.
    Extracts text and structured data from PDF documents.
    """
    
    def __init__(self, settings=None):
        """Initialize OCR parser with settings."""
        from config.settings import OCRSettings
        self.settings = settings or OCRSettings()
        
        if not OCR_AVAILABLE:
            raise ImportError(
                "OCR dependencies not installed. "
                "Run: pip install pytesseract pdf2image Pillow"
            )
        
        logger.info("OCR Parser initialized successfully")
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a PDF file with OCR.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with:
                - success: bool
                - raw_text: str (extracted text)
                - structured_data: dict (CV fields)
                - confidence: float (0-1)
                - processing_time: float (seconds)
                - page_count: int
                - error: str (if failed)
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            
            # Convert PDF to images
            images = self._convert_pdf_to_images(pdf_path)
            
            if not images:
                return {
                    'success': False,
                    'error': 'Failed to convert PDF to images',
                    'raw_text': '',
                    'structured_data': {},
                    'confidence': 0.0,
                    'processing_time': time.time() - start_time,
                    'page_count': 0
                }
            
            # Extract text from all pages
            full_text = ""
            all_confidences = []
            
            for i, image in enumerate(images, 1):
                logger.debug(f"Processing page {i}/{len(images)}")
                
                # Extract text with Tesseract
                text = pytesseract.image_to_string(
                    image,
                    lang='+'.join(self.settings.languages)
                )
                full_text += text + "\n\n"
                
                # Get confidence scores
                data = pytesseract.image_to_data(
                    image,
                    lang='+'.join(self.settings.languages),
                    output_type=pytesseract.Output.DICT
                )
                confidences = [int(c) for c in data['conf'] if int(c) > 0]
                all_confidences.extend(confidences)
            
            # Calculate average confidence
            avg_confidence = (
                sum(all_confidences) / len(all_confidences) / 100.0
                if all_confidences else 0.0
            )
            
            # Extract structured data
            structured_data = self._extract_structured_data(full_text)
            
            processing_time = time.time() - start_time
            
            logger.info(
                f"OCR completed: {len(full_text)} chars, "
                f"{avg_confidence:.2%} confidence, "
                f"{processing_time:.2f}s"
            )
            
            return {
                'success': True,
                'raw_text': full_text.strip(),
                'structured_data': structured_data,
                'confidence': avg_confidence,
                'processing_time': processing_time,
                'page_count': len(images),
                'ocr_model': 'tesseract'
            }
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'raw_text': '',
                'structured_data': {},
                'confidence': 0.0,
                'processing_time': time.time() - start_time,
                'page_count': 0
            }
    
    def _convert_pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """Convert PDF pages to images."""
        try:
            max_pages = self.settings.max_pages_per_pdf
            # Set poppler path for macOS Homebrew installation
            poppler_path = "/opt/homebrew/bin"
            
            images = convert_from_path(
                pdf_path,
                dpi=300,
                first_page=1,
                last_page=max_pages,
                poppler_path=poppler_path
            )
            logger.debug(f"Converted {len(images)} pages to images")
            return images
        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            return []
    
    def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """
        Extract structured CV data from text.
        
        Returns:
            Dictionary with CV fields:
                - name: str
                - email: str
                - phone: str
                - education: list
                - experience: list
                - skills: list
                - languages: list
        """
        data = {
            'name': '',
            'email': '',
            'phone': '',
            'education': [],
            'experience': [],
            'skills': [],
            'languages': []
        }
        
        try:
            # Extract email
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            if emails:
                data['email'] = emails[0]
            
            # Extract phone (French formats)
            phone_pattern = r'(?:\+33|0)[1-9](?:[\s.-]?\d{2}){4}'
            phones = re.findall(phone_pattern, text)
            if phones:
                data['phone'] = phones[0]
            
            # Extract name (heuristic: first line with capital letters)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            for line in lines[:10]:  # Check first 10 lines
                if len(line) > 3 and len(line) < 50 and line[0].isupper():
                    # Likely a name if it has 2-3 words with capitals
                    words = line.split()
                    if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words):
                        data['name'] = line
                        break
            
            # Extract skills (common technical keywords)
            skill_keywords = [
                'Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'Ruby',
                'React', 'Angular', 'Vue', 'Node', 'Django', 'Flask', 'Spring',
                'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
                'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'MySQL',
                'Git', 'Agile', 'Scrum', 'DevOps', 'CI/CD',
                'Machine Learning', 'Deep Learning', 'AI', 'Data Science',
                'HTML', 'CSS', 'TypeScript', 'REST', 'API'
            ]
            
            for skill in skill_keywords:
                if skill.lower() in text.lower():
                    data['skills'].append(skill)
            
            # Extract languages
            language_keywords = {
                'Français': r'\bfran[cç]ais\b',
                'Anglais': r'\banglais\b',
                'Espagnol': r'\bespagnol\b',
                'Allemand': r'\ballemand\b',
                'Italien': r'\bitalien\b',
                'Arabe': r'\barabe\b',
                'Chinois': r'\bchinois\b',
                'Japonais': r'\bjaponais\b'
            }
            
            for lang, pattern in language_keywords.items():
                if re.search(pattern, text, re.IGNORECASE):
                    data['languages'].append(lang)
            
            # Extract education (look for degree keywords)
            education_keywords = [
                'Master', 'Licence', 'Bachelor', 'Doctorat', 'PhD',
                'Ingénieur', 'BTS', 'DUT', 'MBA', 'Baccalauréat'
            ]
            
            for keyword in education_keywords:
                pattern = rf'{keyword}[^\n]*'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches[:3]:  # Limit to 3 entries
                    if match.strip() and match.strip() not in data['education']:
                        data['education'].append(match.strip())
            
            # Extract experience (look for job titles and companies)
            experience_keywords = [
                'Développeur', 'Developer', 'Ingénieur', 'Engineer',
                'Consultant', 'Architecte', 'Manager', 'Chef de projet',
                'Data Scientist', 'Analyste', 'Designer', 'DevOps'
            ]
            
            for keyword in experience_keywords:
                pattern = rf'{keyword}[^\n]*'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches[:5]:  # Limit to 5 entries
                    if match.strip() and len(match) < 100:
                        if match.strip() not in data['experience']:
                            data['experience'].append(match.strip())
            
        except Exception as e:
            logger.error(f"Structured extraction failed: {e}", exc_info=True)
        
        return data


# Backwards compatibility
IntelligentOCRParser = OCRParser

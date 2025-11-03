"""
Input validation utilities for the recruitment agent.
"""
import os
import re
from typing import Optional, Tuple, List
from src.utils.exceptions import ValidationException, FileFormatException

class InputValidator:
    """Validates inputs for the recruitment agent."""
    
    SUPPORTED_CV_FORMATS = ['.pdf', '.docx']
    MIN_CV_TEXT_LENGTH = 50
    MIN_JOB_DESC_LENGTH = 20
    MAX_FILE_SIZE_MB = 10
    
    @staticmethod
    def validate_cv_file(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a CV file.
        
        Args:
            file_path: Path to the CV file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if file exists
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        # Check file format
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in InputValidator.SUPPORTED_CV_FORMATS:
            return False, f"Unsupported format: {ext}. Supported: {', '.join(InputValidator.SUPPORTED_CV_FORMATS)}"
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > InputValidator.MAX_FILE_SIZE_MB:
            return False, f"File too large: {file_size_mb:.2f}MB (max: {InputValidator.MAX_FILE_SIZE_MB}MB)"
        
        return True, None
    
    @staticmethod
    def validate_cv_text(text: str, filename: str = "CV") -> Tuple[bool, Optional[str]]:
        """
        Validate extracted CV text.
        
        Args:
            text: Extracted CV text
            filename: Name of the CV file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, f"Empty or invalid text extracted from {filename}"
        
        if len(text.strip()) < InputValidator.MIN_CV_TEXT_LENGTH:
            return False, f"CV text too short ({len(text)} chars) in {filename}. Minimum: {InputValidator.MIN_CV_TEXT_LENGTH}"
        
        return True, None
    
    @staticmethod
    def validate_job_description(text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate job description text.
        
        Args:
            text: Job description text
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Job description is empty"
        
        if len(text.strip()) < InputValidator.MIN_JOB_DESC_LENGTH:
            return False, f"Job description too short ({len(text)} chars). Minimum: {InputValidator.MIN_JOB_DESC_LENGTH}"
        
        return True, None
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        # Remove spaces and common separators
        clean_phone = re.sub(r'[\s\-\(\)\.]', '', phone)
        # Check if it contains only digits and optionally starts with +
        pattern = r'^\+?\d{8,15}$'
        return bool(re.match(pattern, clean_phone))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format."""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url, re.IGNORECASE))
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Remove or replace unsafe characters in filename."""
        # Replace unsafe characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing spaces and dots
        safe_name = safe_name.strip('. ')
        return safe_name if safe_name else 'unnamed_file'
    
    @staticmethod
    def validate_score(score: float) -> Tuple[bool, Optional[str]]:
        """
        Validate a score value.
        
        Args:
            score: Score value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(score, (int, float)):
            return False, f"Score must be numeric, got {type(score)}"
        
        if score < 0 or score > 1:
            return False, f"Score must be between 0 and 1, got {score}"
        
        return True, None
    
    @staticmethod
    def validate_config_weights(tfidf: float, llm: float, keyword: float) -> Tuple[bool, Optional[str]]:
        """
        Validate ranking weights configuration.
        
        Args:
            tfidf: TF-IDF weight
            llm: LLM weight
            keyword: Keyword weight
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        weights = [tfidf, llm, keyword]
        
        # Check if all are numeric
        if not all(isinstance(w, (int, float)) for w in weights):
            return False, "All weights must be numeric"
        
        # Check if all are between 0 and 1
        if not all(0 <= w <= 1 for w in weights):
            return False, "All weights must be between 0 and 1"
        
        # Check if sum is approximately 1
        total = sum(weights)
        if abs(total - 1.0) > 0.01:
            return False, f"Weights must sum to 1.0, got {total:.3f}"
        
        return True, None

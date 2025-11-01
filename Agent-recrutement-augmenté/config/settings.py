import os
from dataclasses import dataclass, field
from typing import Dict, List, Any
import json

@dataclass
class ModelConfig:
    """Configuration for AI models"""
    llm_provider: str = "groq"  # "openai", "anthropic", "cohere", or "groq"
    llm_model: str = "llama-3.3-70b-versatile"  # Groq's latest Llama model
    embedding_model: str = "text-embedding-ada-002"
    temperature: float = 0.3
    max_tokens: int = 1000
    
    # API keys - will be loaded from environment variables or hardcoded
    api_keys: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        # Load API keys from environment variables with fallback
        self.api_keys = {
            'openai': os.getenv('OPENAI_API_KEY', ''),
            'anthropic': os.getenv('ANTHROPIC_API_KEY', ''),
            'cohere': os.getenv('COHERE_API_KEY', ''),
            'huggingface': os.getenv('HUGGINGFACE_API_KEY', ''),
            'groq': os.getenv('GROQ_API_KEY', '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')
        }

@dataclass
class ExtractionConfig:
    """Configuration for entity extraction"""
    use_spacy: bool = True
    spacy_model: str = "fr_core_news_sm"
    fallback_regex: bool = True
    confidence_threshold: float = 0.7
    custom_entities: List[str] = field(default_factory=lambda: [
        "compétence", "expérience", "formation", "langue", "certification",
        "projet", "outil", "méthodologie", "domaine", "niveau"
    ])
    
    # Patterns for regex fallback
    patterns: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'linkedin': r'linkedin\.com/in/[a-zA-Z0-9_-]+',
            'github': r'github\.com/[a-zA-Z0-9_-]+',
            'degree': r'(bac\+?\d|master|doctorat|ph\.?d|ingénieur|licence|DEUG|DEUST)',
            'experience_years': r'(\d+)\s*ans?\s+?d[\'\s]exp',
            'salary': r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:€|euros?|EUR)',
        }

@dataclass
class RankingConfig:
    """Configuration for candidate ranking"""
    use_tfidf: bool = True
    use_llm_scoring: bool = True
    use_keyword_matching: bool = True
    tfidf_weight: float = 0.3
    llm_weight: float = 0.5
    keyword_weight: float = 0.2
    min_similarity_threshold: float = 0.3
    max_candidates: int = 50
    
    # Keyword configuration
    required_keywords: List[str] = field(default_factory=list)
    preferred_keywords: List[str] = field(default_factory=list)
    keyword_boost: float = 1.5

@dataclass
class OCRSettings:
    """Configuration for OCR processing"""
    enable_ocr: bool = True
    min_text_threshold: int = 100  # Minimum chars before triggering OCR
    max_pages_per_pdf: int = 10
    languages: tuple = ('fra', 'eng')  # Tesseract language codes
    dpi: int = 300  # Image resolution for PDF conversion

@dataclass
class LoggingConfig:
    """Configuration for logging"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/application.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    log_to_console: bool = True

@dataclass
class AppConfig:
    """Main application configuration"""
    debug: bool = False
    version: str = "1.0.0"
    app_name: str = "Agent Recrutement Augmenté"
    data_dir: str = "Agent-recrutement-augmenté/data"
    output_dir: str = "Agent-recrutement-augmenté/docs"
    cache_dir: str = "Agent-recrutement-augmenté/cache"
    
    # Feature flags
    enable_caching: bool = True
    enable_async_processing: bool = True
    enable_api_mode: bool = False

@dataclass
class Config:
    """Main configuration class combining all configurations"""
    model: ModelConfig = field(default_factory=ModelConfig)
    extraction: ExtractionConfig = field(default_factory=ExtractionConfig)
    ranking: RankingConfig = field(default_factory=RankingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    app: AppConfig = field(default_factory=AppConfig)
    
    def __post_init__(self):
        # Create necessary directories
        os.makedirs(self.app.data_dir, exist_ok=True)
        os.makedirs(self.app.output_dir, exist_ok=True)
        os.makedirs(self.app.cache_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.logging.file_path), exist_ok=True)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Create Config instance from dictionary"""
        return cls(
            model=ModelConfig(**config_dict.get('model', {})),
            extraction=ExtractionConfig(**config_dict.get('extraction', {})),
            ranking=RankingConfig(**config_dict.get('ranking', {})),
            logging=LoggingConfig(**config_dict.get('logging', {})),
            app=AppConfig(**config_dict.get('app', {}))
        )
    
    @classmethod
    def from_json(cls, json_path: str) -> 'Config':
        """Create Config instance from JSON file"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            return cls.from_dict(config_dict)
        except Exception as e:
            print(f"Error loading config from {json_path}: {e}")
            return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Config instance to dictionary"""
        return {
            'model': self.model.__dict__,
            'extraction': self.extraction.__dict__,
            'ranking': self.ranking.__dict__,
            'logging': self.logging.__dict__,
            'app': self.app.__dict__
        }
    
    def save_to_json(self, json_path: str):
        """Save Config instance to JSON file"""
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config to {json_path}: {e}")

# Global configuration instance
config = Config()
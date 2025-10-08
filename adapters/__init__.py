"""
Package pour les adaptateurs de modèles.
"""

from .base_adapter import ModelAdapter
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter
from .huggingface_adapter import HuggingFaceAdapter
from .openrouter_adapter import OpenRouterAdapter

__all__ = [
    'ModelAdapter',
    'OpenAIAdapter', 
    'AnthropicAdapter',
    'HuggingFaceAdapter',
    'OpenRouterAdapter'
]
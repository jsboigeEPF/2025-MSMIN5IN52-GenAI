"""
Package pour les adaptateurs de modèles.
"""

from .base_adapter import ModelAdapter
from .openai_adapter import OpenAIAdapter
from .openrouter_adapter import OpenRouterAdapter

# Adaptateurs optionnels (peuvent ne pas exister)
try:
    from .anthropic_adapter import AnthropicAdapter
except ImportError:
    AnthropicAdapter = None

try:
    from .huggingface_adapter import HuggingFaceAdapter
except ImportError:
    HuggingFaceAdapter = None

__all__ = [
    'ModelAdapter',
    'OpenAIAdapter',
    'OpenRouterAdapter'
]

if AnthropicAdapter:
    __all__.append('AnthropicAdapter')
if HuggingFaceAdapter:
    __all__.append('HuggingFaceAdapter')

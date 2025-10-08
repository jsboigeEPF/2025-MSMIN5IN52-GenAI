# Configuration OpenRouter
# ATTENTION: Ce fichier contient des informations sensibles, ne pas commiter !

OPENROUTER_API_KEY = "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"

# Budget de sécurité (en USD)
MAX_TOTAL_BUDGET = 5.00  # Budget maximum total
MAX_BUDGET_PER_MODEL = 0.50  # Budget maximum par modèle

# Modèles à évaluer (ordre de priorité) - Modèles réels d'OpenRouter
PRIORITY_MODELS = [
    # Modèles gratuits d'abord
    "deepseek/deepseek-chat-v3.1:free",      # Gratuit - Très performant
    "nvidia/nemotron-nano-9b-v2:free",       # Gratuit - NVIDIA
    "mistralai/mistral-small-3.2-24b-instruct:free", # Gratuit - Mistral
    "qwen/qwen3-coder:free",                 # Gratuit - Alibaba Qwen
    "tencent/hunyuan-a13b-instruct:free",    # Gratuit - Tencent
    "moonshotai/kimi-k2:free",               # Gratuit - Moonshot
    
    # Modèles payants économiques si budget permet
    "openai/gpt-3.5-turbo",                 # OpenAI économique
    "anthropic/claude-3-haiku",             # Anthropic économique  
    "mistralai/mixtral-8x7b-instruct",      # Mixtral performant
    "openai/gpt-4o-mini",                   # GPT-4 mini économique
]

# Configuration d'évaluation
EVALUATION_CONFIG = {
    "max_tokens_per_request": 150,
    "requests_per_bias_type": 3,  # Nombre de tests par type de biais
    "delay_between_requests": 1.0,  # Délai en secondes entre requêtes
    "timeout": 30,  # Timeout en secondes
}
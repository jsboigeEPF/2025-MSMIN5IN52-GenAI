"""
Configuration centralisée de l'application

Ce fichier contient tous les paramètres configurables de l'application :
- Variables d'environnement
- Configuration des modèles IA
- Paramètres de stockage
- Configuration réseau et sécurité

Utilise Pydantic Settings pour la validation automatique des types
et le chargement depuis les variables d'environnement et fichiers .env
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Déterminer le répertoire backend pour les chemins relatifs
BACKEND_DIR = Path(__file__).parent.parent.resolve()


class Settings(BaseSettings):
    """
    Classe de configuration principale utilisant Pydantic Settings
    
    Les valeurs peuvent être surchargées par :
    1. Variables d'environnement (ex: export DEBUG=false)
    2. Fichier .env dans le répertoire racine
    3. Valeurs par défaut définies ici
    """
    # Environment
    ENV: str = "development"
    DEBUG: bool = True

    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # AI Models
    TEXT_MODEL_NAME: str = "Qwen/Qwen3-0.6B"
    TEXT_MODEL_DEVICE: str = "auto"
    IMAGE_MODEL_NAME: str = "stabilityai/sdxl-turbo"
    IMAGE_MODEL_DEVICE: str = "auto"

    # External APIs
    OPENAI_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""

    # Story Configuration
    MAX_STORY_LENGTH: int = 10000
    MAX_CONTEXT_LENGTH: int = 4000
    DEFAULT_GENRE: str = "fantasy"

    # File Storage (relative to backend directory)
    STORIES_PATH: str = str(BACKEND_DIR / "data" / "stories")
    IMAGES_PATH: str = str(BACKEND_DIR / "data" / "images")

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = str(BACKEND_DIR / "logs" / "app.log")

    class Config:
        env_file = ".env"


settings = Settings()

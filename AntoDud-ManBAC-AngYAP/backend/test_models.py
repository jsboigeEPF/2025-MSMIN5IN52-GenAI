#!/usr/bin/env python3
"""
Script de test pour télécharger et vérifier les modèles IA
"""

import asyncio
import sys
import os

# Ajouter le répertoire backend au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.text_generation_service import TextGenerationService
from app.services.image_generation_service import ImageGenerationService
from app.config import settings

async def test_models():
    """
    Teste l'initialisation des modèles IA
    """
    print("=== Test de téléchargement et initialisation des modèles ===")
    print(f"Modèle de texte: {settings.TEXT_MODEL_NAME}")
    print(f"Modèle d'image: {settings.IMAGE_MODEL_NAME}")
    print(f"Device: {settings.TEXT_MODEL_DEVICE}")
    print()
    
    # Test du service de génération de texte
    print("1. Initialisation du service de génération de texte...")
    text_service = TextGenerationService()
    
    try:
        success = await text_service.initialize_model()
        if success:
            print("✅ Service de génération de texte initialisé avec succès")
            status = text_service.get_model_status()
            print(f"   - Modèle chargé: {status['model_loaded']}")
            print(f"   - Transformers disponible: {status['transformers_available']}")
        else:
            print("⚠️ Service de génération de texte en mode dégradé")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du service de texte: {e}")
    
    print()
    
    # Test du service de génération d'images
    print("2. Initialisation du service de génération d'images...")
    image_service = ImageGenerationService()
    
    try:
        success = await image_service.initialize_model()
        if success:
            print("✅ Service de génération d'images initialisé avec succès")
            status = image_service.get_model_status()
            print(f"   - Modèle chargé: {status['model_loaded']}")
            print(f"   - Diffusers disponible: {status['diffusers_available']}")
        else:
            print("⚠️ Service de génération d'images en mode dégradé")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du service d'images: {e}")
    
    print()
    print("=== Tests terminés ===")

if __name__ == "__main__":
    asyncio.run(test_models())
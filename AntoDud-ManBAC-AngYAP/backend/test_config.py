#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration du backend
Teste la détection CUDA et les chemins de fichiers
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(__file__))

from app.config import settings

print("=" * 60)
print("TEST DE CONFIGURATION BACKEND")
print("=" * 60)

print("\n📋 Configuration des modèles IA:")
print(f"  - Modèle de texte: {settings.TEXT_MODEL_NAME}")
print(f"  - Device texte: {settings.TEXT_MODEL_DEVICE}")
print(f"  - Modèle d'images: {settings.IMAGE_MODEL_NAME}")
print(f"  - Device images: {settings.IMAGE_MODEL_DEVICE}")

print("\n📁 Chemins de stockage:")
print(f"  - Stories: {settings.STORIES_PATH}")
print(f"  - Images: {settings.IMAGES_PATH}")
print(f"  - Logs: {settings.LOG_FILE}")

print("\n🔍 Vérification des chemins:")
import pathlib
backend_dir = pathlib.Path(__file__).parent.resolve()
print(f"  - Répertoire backend: {backend_dir}")
print(f"  - Chemin stories absolu: {pathlib.Path(settings.STORIES_PATH).resolve()}")
print(f"  - Chemin images absolu: {pathlib.Path(settings.IMAGES_PATH).resolve()}")

# Vérifier si les chemins sont dans le répertoire backend
stories_in_backend = str(backend_dir) in str(pathlib.Path(settings.STORIES_PATH).resolve())
images_in_backend = str(backend_dir) in str(pathlib.Path(settings.IMAGES_PATH).resolve())

print(f"  - Stories dans backend/: {'✅ OUI' if stories_in_backend else '❌ NON'}")
print(f"  - Images dans backend/: {'✅ OUI' if images_in_backend else '❌ NON'}")

print("\n🎮 Test de détection CUDA:")
try:
    import torch
    cuda_available = torch.cuda.is_available()
    print(f"  - PyTorch installé: ✅ OUI")
    print(f"  - CUDA disponible: {'✅ OUI' if cuda_available else '❌ NON'}")
    
    if cuda_available:
        gpu_count = torch.cuda.device_count()
        print(f"  - Nombre de GPUs: {gpu_count}")
        for i in range(gpu_count):
            gpu_name = torch.cuda.get_device_name(i)
            print(f"    GPU {i}: {gpu_name}")
    else:
        print(f"  - Raison: PyTorch peut ne pas être installé avec support CUDA")
        print(f"  - Pour installer avec CUDA: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
except ImportError:
    print(f"  - PyTorch installé: ❌ NON")

print("\n🔧 Test des services:")
try:
    from app.services.text_generation_service import TextGenerationService
    text_service = TextGenerationService()
    print(f"  - Service de texte:")
    print(f"    Device détecté: {text_service.device}")
    print(f"    Modèle: {text_service.model_name}")
    
    from app.services.image_generation_service import ImageGenerationService
    image_service = ImageGenerationService()
    print(f"  - Service d'images:")
    print(f"    Device détecté: {image_service.device}")
    print(f"    Modèle: {image_service.model_name}")
    print(f"    Chemin images: {image_service.images_path}")
except Exception as e:
    print(f"  - Erreur lors de l'initialisation des services: {e}")

print("\n" + "=" * 60)
print("FIN DU TEST")
print("=" * 60)

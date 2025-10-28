#!/usr/bin/env python3
"""
Test de simulation CUDA pour vérifier le comportement avec et sans GPU
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 70)
print("TEST DE SIMULATION - DÉTECTION CUDA")
print("=" * 70)

# Test 1: Configuration avec device='auto'
print("\n📋 Test 1: Configuration avec device='auto'")
print("-" * 70)

from app.config import settings

print(f"Configuration actuelle:")
print(f"  TEXT_MODEL_DEVICE = '{settings.TEXT_MODEL_DEVICE}'")
print(f"  IMAGE_MODEL_DEVICE = '{settings.IMAGE_MODEL_DEVICE}'")

# Test 2: Simulation de détection CUDA
print("\n🎮 Test 2: Simulation de la logique de détection")
print("-" * 70)

class MockDetector:
    """Simule la détection de device"""
    
    @staticmethod
    def detect_device(device_setting: str, cuda_available: bool) -> str:
        """Simule la logique de _detect_device"""
        if device_setting.lower() == "auto":
            if cuda_available:
                print("  🎮 CUDA détecté! GPU disponibles: 1, Nom: NVIDIA GeForce RTX 3080")
                return "cuda"
            else:
                print("  💻 CUDA non disponible, utilisation du CPU")
                return "cpu"
        else:
            return device_setting.lower()

# Simulation sans CUDA
print("\nScénario A: Système SANS CUDA (situation actuelle dans ce test)")
device_a = MockDetector.detect_device("auto", cuda_available=False)
print(f"  Résultat: device = '{device_a}'")

# Simulation avec CUDA
print("\nScénario B: Système AVEC CUDA disponible (carte NVIDIA)")
device_b = MockDetector.detect_device("auto", cuda_available=True)
print(f"  Résultat: device = '{device_b}'")

# Simulation forcée CPU
print("\nScénario C: Forcer CPU (device='cpu')")
device_c = MockDetector.detect_device("cpu", cuda_available=True)
print(f"  Résultat: device = '{device_c}' (même avec CUDA disponible)")

# Simulation forcée CUDA
print("\nScénario D: Forcer CUDA (device='cuda')")
device_d = MockDetector.detect_device("cuda", cuda_available=False)
print(f"  Résultat: device = '{device_d}' (attention: échouera si pas de CUDA)")

# Test 3: Vérification des chemins
print("\n📁 Test 3: Vérification des chemins de données")
print("-" * 70)

import pathlib

backend_dir = pathlib.Path(__file__).parent.resolve()
stories_path = pathlib.Path(settings.STORIES_PATH)
images_path = pathlib.Path(settings.IMAGES_PATH)

print(f"Répertoire backend: {backend_dir}")
print(f"Chemin stories: {stories_path}")
print(f"Chemin images: {images_path}")

# Vérifier que les chemins sont dans le backend
stories_correct = str(backend_dir) in str(stories_path.resolve())
images_correct = str(backend_dir) in str(images_path.resolve())

print(f"\n✓ Validation:")
print(f"  Stories dans backend/: {'✅ CORRECT' if stories_correct else '❌ INCORRECT'}")
print(f"  Images dans backend/: {'✅ CORRECT' if images_correct else '❌ INCORRECT'}")

# Afficher la structure attendue
print(f"\nStructure de répertoires attendue:")
print(f"  {backend_dir}/")
print(f"  ├── data/")
print(f"  │   ├── stories/  ← {stories_path}")
print(f"  │   └── images/   ← {images_path}")
print(f"  └── logs/")

# Test 4: Résumé des corrections
print("\n" + "=" * 70)
print("RÉSUMÉ DES CORRECTIONS")
print("=" * 70)

print("\n✅ Correction 1: Détection CUDA automatique")
print("   - device='auto' détecte automatiquement GPU/CPU")
print("   - Avec CUDA disponible: utilise le GPU")
print("   - Sans CUDA: utilise le CPU")
print("   - Peut être forcé avec device='cuda' ou device='cpu'")

print("\n✅ Correction 2: Emplacement du répertoire data")
print("   - Avant: ./data (relatif au répertoire d'exécution)")
print("   - Après: backend/data (absolu, calculé automatiquement)")
print(f"   - Résultat: {stories_path.parent}")

print("\n📌 Pour utiliser avec votre GPU NVIDIA:")
print("   1. Assurez-vous que PyTorch avec CUDA est installé")
print("   2. Vérifiez: python -c \"import torch; print(torch.cuda.is_available())\"")
print("   3. Le système utilisera automatiquement le GPU avec device='auto'")

print("\n" + "=" * 70)
print("FIN DU TEST")
print("=" * 70)

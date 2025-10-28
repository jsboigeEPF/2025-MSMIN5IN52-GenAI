# Corrections de Configuration Backend

Ce document décrit les corrections apportées au backend pour résoudre les problèmes de détection CUDA et de placement du répertoire data.

## Problèmes Résolus

### 1. Détection CUDA Automatique

**Problème :** Les fichiers de configuration avaient `TEXT_MODEL_DEVICE=cpu` et `IMAGE_MODEL_DEVICE=cpu` hardcodés, ce qui forçait l'utilisation du CPU même avec une carte graphique NVIDIA disponible.

**Solution :**
- Modification de `.env.example` pour utiliser `auto` au lieu de `cpu`
- Le paramètre `auto` permet au système de détecter automatiquement si CUDA est disponible
- La logique de détection est dans `_detect_device()` des services

**Code de détection :**
```python
def _detect_device(self, device_setting: str) -> str:
    if device_setting.lower() == "auto":
        if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
            print(f"🎮 CUDA détecté! GPU disponibles: {gpu_count}, Nom: {gpu_name}")
            return "cuda"
        else:
            print("💻 CUDA non disponible, utilisation du CPU")
            return "cpu"
    else:
        return device_setting.lower()
```

### 2. Placement du Répertoire Data

**Problème :** Le répertoire `data` était créé à la racine du projet (`2025-MSMIN5IN52-GenAI-G-n-rateur-d-histoires-interactives/data`) au lieu du répertoire backend.

**Solution :**
- Modification de `app/config.py` pour calculer des chemins absolus relatifs au répertoire backend
- Utilisation de `Path(__file__).parent.parent.resolve()` pour obtenir le répertoire backend
- Les chemins sont maintenant : `backend/data/stories`, `backend/data/images`, `backend/logs/app.log`

**Avant :**
```python
STORIES_PATH: str = "./data/stories"
IMAGES_PATH: str = "./data/images"
```

**Après :**
```python
BACKEND_DIR = Path(__file__).parent.parent.resolve()
...
STORIES_PATH: str = str(BACKEND_DIR / "data" / "stories")
IMAGES_PATH: str = str(BACKEND_DIR / "data" / "images")
```

## Configuration

### Variables d'Environnement

Créez un fichier `.env` dans le répertoire `backend/` avec le contenu suivant :

```bash
# Utiliser 'auto' pour détection automatique GPU/CPU
TEXT_MODEL_DEVICE=auto
IMAGE_MODEL_DEVICE=auto

# Ou forcer un device spécifique
# TEXT_MODEL_DEVICE=cuda  # Force GPU
# TEXT_MODEL_DEVICE=cpu   # Force CPU
```

### Vérification

Pour vérifier que la configuration fonctionne correctement :

```bash
cd backend
python test_config.py
```

Ce script affichera :
- La configuration des modèles IA
- Les chemins de stockage (devrait être dans `backend/data/`)
- La détection CUDA
- L'état des services

## Résultat Attendu

Avec une carte NVIDIA CUDA disponible, vous devriez voir :

```
🎮 CUDA détecté! GPU disponibles: 1, Nom: NVIDIA GeForce RTX 3080
🔧 Service de texte configuré - Device: cuda, Modèle: Qwen/Qwen3-0.6B
🎨 Service d'images configuré - Device: cuda, Modèle: stabilityai/sdxl-turbo
```

Les données seront stockées dans :
```
backend/
├── data/
│   ├── stories/
│   └── images/
└── logs/
    └── app.log
```

## Tests

Pour tester avec PyTorch et CUDA installés :

```bash
# Installer PyTorch avec support CUDA (exemple pour CUDA 12.1)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Vérifier la détection CUDA
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Lancer le test de configuration
python test_config.py
```

## Notes Importantes

1. **Auto-détection** : La valeur `auto` est maintenant la valeur par défaut et recommandée
2. **Forcer un device** : Vous pouvez toujours forcer `cuda` ou `cpu` si nécessaire
3. **Chemins absolus** : Les chemins sont maintenant calculés automatiquement, peu importe d'où le script est lancé
4. **Compatibilité** : Les changements sont rétrocompatibles avec les anciennes configurations

## Migration du répertoire data existant

Si vous aviez déjà un répertoire `data/` à la racine du projet (problème avant correction), vous pouvez le déplacer vers le backend :

```bash
# Depuis la racine du projet
mv data/ AntoDud-ManBAC-AngYAP/backend/data/

# Ou simplement supprimer l'ancien si pas de données importantes
rm -rf data/
```

Le nouveau système créera automatiquement les répertoires dans `backend/data/` au premier démarrage.

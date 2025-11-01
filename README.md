```markdown
# Générateur d'Ambiances Sonores - POC GenAI

Ce projet est un POC permettant de générer des ambiances sonores à partir de descriptions textuelles en utilisant le modèle AudioCraft de Meta.

## Fonctionnalités

- Génération d'audio à partir de descriptions textuelles
- Interface web simple et intuitive
- Paramètres ajustables (durée, température)
- Téléchargement des fichiers audio générés

## Prérequis

- Python 3.8+
- pip
- 4GB+ RAM recommandé

## Installation

1. Cloner le repository

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Lancement

```bash
python backend/app.py
```

L'application sera accessible sur : http://localhost:5000

## Utilisation

1. Entrez une description de l'ambiance souhaitée (ex: "calming ocean waves with seagulls")
2. Ajustez la durée (5-30 secondes)
3. Cliquez sur "Générer l'ambiance sonore"
4. Écoutez et téléchargez le résultat

## Technologies

- **Backend** : Flask, Transformers, AudioCraft
- **Frontend** : HTML5, CSS3, JavaScript vanilla
- **Modèle** : facebook/musicgen-small

## Note

Ce POC utilise le modèle small pour des performances optimales. Pour une meilleure qualité, vous pouvez utiliser les variantes medium ou large.
```
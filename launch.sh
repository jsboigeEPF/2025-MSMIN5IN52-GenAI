#!/bin/bash
# Script de lancement automatisé pour l'outil d'évaluation de biais

echo "🔍 Outil d'Évaluation de Biais dans les Modèles de Langage"
echo "=========================================================="

# Vérifier Python
if ! command -v python &> /dev/null; then
    echo "❌ Python n'est pas installé. Veuillez installer Python 3.8+"
    exit 1
fi

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -r requirements.txt

# Lancer l'évaluation
echo "🚀 Lancement de l'évaluation des modèles..."
python main.py

# Lancer le dashboard
echo "🌐 Lancement du tableau de bord..."
echo "📊 Dashboard disponible sur : http://localhost:5000"
cd visualization/dashboard
python app.py
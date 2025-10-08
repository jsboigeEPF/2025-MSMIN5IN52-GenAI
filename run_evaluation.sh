#!/bin/bash
# Script de lancement de l'évaluation multi-modèles

echo "🚀 Lancement de l'évaluation de biais multi-modèles avec OpenRouter"
echo "=================================================="

# Vérification de l'environnement virtuel
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Activation de l'environnement virtuel..."
    source .venv/Scripts/activate || source .venv/bin/activate
fi

# Vérification des dépendances
echo "📦 Vérification des dépendances..."
python -c "import openai, requests" 2>/dev/null || {
    echo "❌ Dépendances manquantes. Installation..."
    pip install openai requests
}

# Lancement de l'évaluation
echo "🎯 Démarrage de l'évaluation..."
python evaluate_models.py

echo "✅ Évaluation terminée!"
echo "💡 Vous pouvez maintenant lancer le dashboard pour voir les résultats:"
echo "   cd visualization/dashboard && python app.py"
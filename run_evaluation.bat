@echo off
REM Script de lancement de l'évaluation multi-modèles pour Windows

echo 🚀 Lancement de l'évaluation de biais multi-modèles avec OpenRouter
echo ==================================================

REM Activation de l'environnement virtuel
if not defined VIRTUAL_ENV (
    echo ⚠️  Activation de l'environnement virtuel...
    call .venv\Scripts\activate.bat
)

REM Vérification des dépendances
echo 📦 Vérification des dépendances...
python -c "import openai, requests" >nul 2>&1
if errorlevel 1 (
    echo ❌ Dépendances manquantes. Installation...
    pip install openai requests
)

REM Lancement de l'évaluation
echo 🎯 Démarrage de l'évaluation...
python evaluate_models.py

echo ✅ Évaluation terminée!
echo 💡 Vous pouvez maintenant lancer le dashboard pour voir les résultats:
echo    cd visualization\dashboard ^&^& python app.py

pause
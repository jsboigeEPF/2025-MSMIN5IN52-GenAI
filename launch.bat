@echo off
rem Script de lancement automatisé pour Windows
echo 🔍 Outil d'Évaluation de Biais dans les Modèles de Langage
echo ==========================================================

rem Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé. Veuillez installer Python 3.8+
    pause
    exit /b 1
)

rem Créer l'environnement virtuel s'il n'existe pas
if not exist "venv" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv venv
)

rem Activer l'environnement virtuel
echo 🔧 Activation de l'environnement virtuel...
call venv\Scripts\activate

rem Installer les dépendances
echo 📥 Installation des dépendances...
pip install -r requirements.txt

rem Lancer l'évaluation
echo 🚀 Lancement de l'évaluation des modèles...
python main.py

rem Lancer le dashboard
echo 🌐 Lancement du tableau de bord...
echo 📊 Dashboard disponible sur : http://localhost:5000
cd visualization\dashboard
python app.py

pause
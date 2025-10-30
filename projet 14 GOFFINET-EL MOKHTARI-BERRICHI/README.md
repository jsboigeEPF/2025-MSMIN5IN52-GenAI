# Structured Content Generator

Un système complet de **génération de contenu structuré** (CVs, factures, rapports)
à partir de **prompts en langage naturel** ou de **données JSON**.

---

##  Présentation

Ce projet combine :
- **FastAPI** → API principale
- **Semantic Kernel + OpenAI** → génération de contenu intelligent à partir de prompts
- **ReportLab** → rendu PDF professionnel (CV, invoice, report)
- **React (Vite + Tailwind)** → interface utilisateur moderne pour interagir avec l’API

L’objectif :  
Créer un workflow multi-agents capable de transformer un texte libre en document structuré (et stylisé) au format PDF.

---

## Architecture

projet 14 GOFFINET-EL MOKHTARI-BERRICHI/
│── .pytest_cache/ # Cache des tests Pytest
├── .venv/ # Environnement virtuel Python (non versionné)
|
├── src/
│ ├── agents/ # Agents pour chaque type de document (CV, invoice, report)
│ ├── renderers/ # Rendu PDF avec ReportLab
│ ├── schemas/ # Schémas JSON pour la validation
│ ├── utils/ # Fonctions utilitaires (validation, fichiers, etc.)
│ ├── routers/ # Routes FastAPI (inclut orchestrateur + Semantic agent)
│ ├── orchestrator.py # Coordination des agents pour la génération
│ └── main.py # Point d’entrée FastAPI
|
│── out/ # Dossiers de sortie (fichiers générés)
|
├── samples/ # Exemples de données d’entrée et modèles de génération
│ ├── cv_prompt.md # Exemple de prompt pour générer un CV
│ ├── cv.json # Exemple de réponse JSON pour un CV
│ ├── invoice_prompt.md # Prompt pour générer une facture
│ ├── invoice.json # Exemple de résultat JSON d’une facture
│ ├── report_prompt.md # Prompt pour générer un rapport
│ └── report.json # Exemple de structure JSON d’un rapport
|
├── frontend/ # Interface React (prompt + choix du type de document)
│ ├── src/
│ ├── package.json
│ └── vite.config.js
├
|── tests/ # Tests unitaires et d’intégration (Pytest)
│ ├── pycache/ # Cache compilé Python
│ ├── test_render_smoke.py # Test basique de génération PDF
│ └── test_validate.py # Test de validation des schémas JSON
├
├── .env # Clé API OpenAI et configuration
├── .env.example # Exemple de configuration d'environnement
├── .gitignore # Fichiers à ignorer par Git
|── README.md # Documentation principale du projet
└─── requirements.txt # Dépendances Python


---

##  Fonctionnalités principales

**Génération par prompt (Semantic Kernel + OpenAI)**  
    “Rédige un CV pour Safae Berrichi, ingénieure en informatique à l’EPF…”

 **Validation automatique via JSON Schema**  
    Garantit que le document respecte la structure définie

**Rendu PDF avec ReportLab**  
    Sortie visuelle professionnelle (marges, bande lavande, pagination, etc.)

**API REST complète (FastAPI)**  
    Routes `/api/cv`, `/api/invoice`, `/api/report`, `/api/semantic/{doc_type}`

**Frontend moderne (React + Tailwind)**  
    Permet de saisir un prompt et de générer le PDF depuis une interface graphique

---

##  Installation & Lancement

###  Backend (FastAPI)
```bash
# Cloner le dépôt (fork du projet principal)
    git clone https://github.com/Asatsukiii/2025-MSMIN5IN52-GenAI.git
    cd projet 14 GOFFINET-EL MOKHTARI-BERRICHI

    ==> Ce dépôt est une fork du projet principal 2025-MSMIN5IN52-GenAI, et contient plusieurs sous-projets étudiants.
    ==> Le nôtre correspond au dossier : projet 14 GOFFINET-EL MOKHTARI-BERRICHI

# Créer et activer un venv
    python -m venv .venv
    .venv\Scripts\Activate.ps1

# Installer les dépendances
	pip install -r requirements.txt

# Lancer l'API
    uvicorn src.main:app --reload  

# Accéder à Swagger :
     http://127.0.0.1:8000/docs

# Frontend (React)
    cd frontend
    npm install
    npm run dev
    ==> Ouvre : http://localhost:5173

# Tests
    pytest -q

# Nettoyage
	rm -rf out/*.pdf out/cv/*.pdf out/invoice/*.pdf out/report/*.pdf


# Exemple d’appel API
==> Prompt vers document
curl -X POST "http://127.0.0.1:8000/api/semantic/report" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Rédige un rapport technique sur le projet IMSA Forever Shop développé par Safae Berrichi à l’EPF."}'


# Le backend :

    Génère le JSON structuré avec Semantic Kernel

    Valide le schéma

    Rends le PDF avec ReportLab

    Renvoie le fichier téléchargeable 

🏫 Auteurs : 

👩‍💻 Pauline GOFFINET
👩‍💻 Safae Berrichi 
👩‍💻 Nehade ELMOKHTARI


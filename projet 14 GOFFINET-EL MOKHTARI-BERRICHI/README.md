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

structured-content-generator/
│
├── src/
│ ├── agents/ # Agents pour chaque type de document (CV, invoice, report)
│ ├── renderers/ # Rendu PDF avec ReportLab
│ ├── schemas/ # Schémas JSON pour la validation
│ ├── utils/ # Fonctions utilitaires (validation, fichiers, etc.)
│ ├── routers/ # Routes FastAPI (inclut orchestrateur + Semantic agent)
│ ├── orchestrator.py # Coordination des agents pour la génération
│ └── main.py # Point d’entrée FastAPI
│
├── frontend/ # Interface React (prompt + choix du type de document)
├── .env # Clé API OpenAI et configuration
├── requirements.txt # Dépendances Python
├── Makefile # Commandes simplifiées
└── README.md


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
# Cloner le dépôt
git clone https://github.com/<user>/structured-content-generator.git
cd structured-content-generator

# Créer et activer un venv
python -m venv .venv
source .venv/bin/activate  # (ou .venv\Scripts\activate sur Windows)

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


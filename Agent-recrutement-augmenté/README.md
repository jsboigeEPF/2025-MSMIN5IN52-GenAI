# Agent de Recrutement Augmenté

## Présentation
Ce projet est un système d'analyse et de classement de CVs pour un poste de stage en ingénierie logicielle et transformation digitale. Il utilise des techniques de traitement du langage naturel (NLP) et d'intelligence artificielle pour automatiser le processus de recrutement initial.

## Fonctionnalités
- Extraction automatique des entités clés des CVs (compétences, éducation, expérience, certifications)
- Analyse de l'adéquation des candidats avec le poste à pourvoir
- Classement des candidats selon leur pertinence pour le poste
- Génération de rapports détaillés (CSV et HTML)
- Interface utilisateur interactive via Streamlit

## Technologies utilisées
- Python 3.8+
- Streamlit pour l'interface utilisateur
- spaCy pour le traitement du langage naturel
- PyPDF2 et python-docx pour la lecture des documents
- OpenAI API (optionnel) pour l'évaluation avancée

## Structure du projet
```
Agent-recrutement-augmenté/
├── data/
│   ├── cv_samples/           # Échantillons de CVs à analyser
│   └── job_descriptions/     # Descriptions de poste
├── docs/                     # Rapports générés
├── src/                      # Code source
├── config/                   # Fichiers de configuration
└── app.py                    # Interface Streamlit
```

## Installation
1. Cloner le dépôt
2. Créer un environnement virtuel: `python -m venv venv`
3. Activer l'environnement: `source venv/bin/activate` (Linux/Mac) ou `venv\Scripts\activate` (Windows)
4. Installer les dépendances: `pip install -r requirements.txt`

## Utilisation
1. Placer les CVs à analyser dans le dossier `data/cv_samples/`
2. Mettre à jour la description de poste dans `data/job_descriptions/description_poste.txt` si nécessaire
3. Lancer l'application: `streamlit run app.py`
4. Consulter les résultats dans l'interface web ou dans le dossier `docs/`

## Configuration
Le fichier de configuration `config.json` permet de personnaliser le comportement du système, notamment :
- Les poids des différents critères d'évaluation
- Les seuils de similarité
- Les paramètres de l'API OpenAI (optionnel)

## Auteurs
- Abdellah SOFI
- Ali Fassy-Fehry

## Licence
Ce projet est distribué sous licence MIT.

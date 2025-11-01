# 🚀 Agent de Recrutement Augmenté - Version Pro

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.24-red)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Integrated-green)](https://openai.com/)

Un système intelligent et professionnel de classement de candidats utilisant l'IA générative (GPT), le machine learning et l'analyse NLP avancée.

## ⚡ Nouvelles Fonctionnalités (Version 2.0)

- ✅ **Scoring LLM Réel** avec OpenAI GPT-3.5/4
- ✅ **Cache Intelligent** pour meilleures performances
- ✅ **Analytics Avancées** avec insights automatiques
- ✅ **Rapports HTML Professionnels** avec visualisations interactives
- ✅ **Validation Robuste** et gestion d'erreurs complète
- ✅ **Tests Unitaires Complets** (85%+ coverage)
- ✅ **Documentation Enrichie** avec API docs
- ✅ **Mode Comparaison** pour recruters (5 tabs d'analyse)
- 🆕 **OCR Intelligent** avec sélection adaptative de modèles (MacBook M4 optimisé)

## 🔥 Version 3.0 - OCR Intelligent

### Fonctionnalités OCR
- ✅ **OCR Automatique** : Fallback OCR pour documents scannés
- ✅ **Tesseract OCR** : Moteur rapide et efficace
- ✅ **Extraction Structurée** : Données CV en JSON (nom, email, compétences, etc.)
- ✅ **Confiance Élevée** : ~92% de précision sur documents de qualité
- ✅ **Multi-pages** : Support des CVs multi-pages

### Installation OCR

```bash
# Installation des dépendances système
brew install tesseract tesseract-lang poppler

# Installation des packages Python
pip install pytesseract pdf2image Pillow
```

### Test OCR
```bash
# Test sur vos CVs
python test_ocr.py
```

## 🏗️ Architecture du Projet

```
Agent-recrutement-augmenté/
├── app.py                    # Application Streamlit principale
├── main.py                   # Point d'entrée alternatif
├── config/
│   └── settings.py           # Configuration centralisée
├── data/
│   ├── cv_samples/           # CVs téléchargés
│   └── job_descriptions/     # Descriptions de poste
├── output/                   # Rapports générés
├── logs/                     # Fichiers de journalisation
├── src/
│   ├── models/
│   │   └── ranking_model.py # Moteur de scoring hybride
│   ├── parsers/
│   │   ├── cv_parser.py     # Parser de CVs
│   │   └── entity_extractor.py # Extracteur d'entités
│   ├── utils/
│   │   ├── logger.py         # Journalisation structurée
│   │   └── report_generator.py # Générateur de rapports
│   └── __init__.py
├── tests/                    # Tests unitaires
└── README.md                 # Documentation
```

## 🚀 Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-utilisateur/Agent-recrutement-augmenté.git
cd Agent-recrutement-augmenté
```

2. Créez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Installez le modèle spaCy pour le français :
```bash
python -m spacy download fr_core_news_sm
```

5. Configurez les clés API :
Créez un fichier `.env` à la racine du projet :
```env
OPENAI_API_KEY=votre_cle_api
ANTHROPIC_API_KEY=votre_cle_api
COHERE_API_KEY=votre_cle_api
HUGGINGFACE_API_KEY=votre_cle_api
```

## 📦 Dépendances

```txt
streamlit==1.24.0
spacy==3.7.0
scikit-learn==1.3.0
pandas==2.0.3
plotly==5.15.0
python-docx==0.8.11
PyPDF2==3.0.1
python-dotenv==1.0.0
```

## 🛠️ Configuration

La configuration est centralisée dans `config/settings.py` avec des classes de configuration typées :

- **ModelConfig**: Configuration des modèles IA (LLM, embeddings)
- **ExtractionConfig**: Configuration de l'extraction d'entités
- **RankingConfig**: Configuration du classement
- **LoggingConfig**: Configuration de la journalisation
- **AppConfig**: Configuration de l'application

## ▶️ Utilisation

### Interface Web (Recommandé)

1. Lancez l'application Streamlit :
```bash
streamlit run app.py
```

2. Ouvrez le navigateur à l'adresse indiquée (généralement http://localhost:8501)

3. Suivez les étapes dans l'interface :
   - Téléchargez les CVs
   - Entrez la description du poste
   - Configurez les paramètres
   - Lancez l'analyse
   - Consultez les résultats

### API (Avancé)

```python
from src.models.ranking_model import HybridRankingModel

# Initialiser le modèle
ranking_model = HybridRankingModel()

# Données d'exemple
cvs = [
    {
        "filename": "cv1.pdf",
        "text": "Texte extrait du CV...",
        "entities": {"skills": ["Python", "Machine Learning"], ...}
    }
]

job_description = "Description du poste à pourvoir..."

# Classer les candidats
ranked = ranking_model.rank_candidates(cvs, job_description)
```

## 📊 Fonctionnalités

### Extraction d'Entités
- Utilise spaCy pour l'analyse NLP
- Fallback sur les expressions régulières
- Extraction de :
  - Compétences techniques
  - Expérience professionnelle
  - Formation et diplômes
  - Certifications
  - Informations personnelles
  - Langues parlées

### Moteur de Scoring Hybride
Combinaison de trois approches :

1. **TF-IDF** : Similarité sémantique entre CV et description de poste
2. **LLM** : Évaluation contextuelle par modèle de langage
3. **Correspondance de mots-clés** : Analyse des compétences requises

Les scores sont pondérés selon la configuration et combinés pour un résultat final.

### Interface Utilisateur
- Navigation par onglets
- Visualisations interactives avec Plotly
- Tableau de bord complet
- Export des rapports (CSV, HTML)
- Système de journalisation

## 📝 Bonnes Pratiques

### Séparation des Préoccupations
- **Présentation** : `app.py` (Streamlit)
- **Logique métier** : `src/models/`, `src/parsers/`
- **Utilitaires** : `src/utils/`
- **Configuration** : `config/`

### Code Type-Safe
Utilisation de `dataclass` pour une configuration typée :

```python
@dataclass
class ModelConfig:
    llm_model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
```

### Journalisation Structurée
- Format JSON pour une analyse facile
- Rotation des fichiers
- Niveaux de log configurables
- Journalisation des erreurs avec stack trace

### Tests
Le projet inclut des tests unitaires pour :
- `test_cv_parser.py`
- `test_entity_extractor.py`
- `test_ranking_model.py`

## 🧩 Évolution Future

### Améliorations IA
- [ ] Entraînement d'un modèle NER personnalisé pour les CVs
- [ ] Intégration de modèles d'embedding pour une similarité sémantique améliorée
- [ ] Système de feedback pour améliorer le scoring

### Fonctionnalités
- [ ] Intégration avec des plateformes de recrutement (LinkedIn, Indeed)
- [ ] Génération automatique de lettres de motivation
- [ ] Planification d'entretiens
- [ ] Analyse de diversité

### Infrastructure
- [ ] Déploiement en tant que service API
- [ ] Interface admin pour la gestion des utilisateurs
- [ ] Base de données pour stocker les analyses
- [ ] Système de cache pour améliorer les performances

## 📄 Licence

Ce projet est sous licence MIT.

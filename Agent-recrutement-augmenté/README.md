# Agent de Recrutement Augmenté

Un système intelligent pour comparer des CVs à une description de poste et produire une liste classée de candidats avec justification.

## Fonctionnalités

- Chargement et parsing de CVs (PDF, DOCX)
- Extraction de texte brut
- Comparaison avec une description de poste
- Classement des candidats par score de correspondance
- Génération de rapports (CSV, HTML) avec justification
- Interface web interactive pour une utilisation facile
- Scoring sémantique avec fallback intelligent

## Technologies utilisées

- Python 3.9+
- PyPDF2 (extraction PDF)
- python-docx (extraction DOCX)
- Pandas (gestion des données)
- Streamlit (interface web)
- LangChain et OpenAI (scoring sémantique)
- Système de fallback basé sur la similarité de texte

## Structure du projet

```
Agent-recrutement-augmenté/
├── data/
│   ├── cv_samples/           # CVs d'exemple
│   └── job_descriptions/     # Descriptions de poste
├── src/
│   ├── parsers/              # Modules de parsing
│   ├── models/               # Modèles de scoring
│   └── utils/                # Utilitaires
├── docs/                     # Rapports générés
├── notebooks/                # Analyses exploratoires
├── tests/                    # Tests unitaires
├── app.py                    # Application web Streamlit
└── main.py                   # Point d'entrée en ligne de commande
```

## Installation

```bash
pip install PyPDF2 python-docx pandas streamlit langchain langchain-openai openai
```

## Configuration

Pour utiliser le scoring sémantique avancé avec OpenAI, vous devez définir votre clé API :

```bash
export OPENAI_API_KEY='votre_cle_api_ici'
```

Le système dispose d'un mécanisme de fallback qui fonctionne sans clé API, en utilisant un scoring basé sur la similarité de texte.

## Utilisation

### Option 1 : Interface Web (Recommandé)

1. Exécutez l'application :
```bash
streamlit run app.py
```
2. Dans le navigateur, vous pouvez :
   - Télécharger plusieurs CVs (PDF/DOCX)
   - Saisir une description de poste
   - Lancer l'analyse avec un clic
   - Visualiser les résultats en temps réel
   - Télécharger les rapports (CSV/HTML)

### Option 2 : Ligne de commande

1. Placer vos CVs dans `data/cv_samples/`
2. Ajouter une description de poste dans `data/job_descriptions/description_poste.txt`
3. Exécuter :
```bash
python main.py
```
4. Les rapports sont générés dans `docs/`

## Compréhension des résultats

Les rapports incluent :
- **Score de correspondance** : Pourcentage de correspondance entre le CV et le poste
- **Niveau de confiance** : Indique si l'évaluation vient du modèle LLM (élevé) ou du système de fallback (bas)
- **Justification** : Explication du score avec indication du mode d'évaluation

## Fonctionnalités implémentées

- [x] Chargement et parsing de CVs (PDF, DOCX)
- [x] Extraction de texte brut
- [x] Extraction d'entités structurées (compétences, expérience, éducation, certifications)
- [x] Comparaison avec une description de poste
- [x] Classement des candidats par score de correspondance
- [x] Génération de rapports (CSV, HTML) avec justification détaillée
- [x] Interface web interactive avec visualisations
- [x] Scoring sémantique avec OpenAI
- [x] Système de fallback basé sur la similarité de texte
- [x] Configuration personnalisable via fichier JSON
- [x] Amélioration des justifications avec identification des compétences manquantes
- [x] Génération de questions d'entretien suggérées
- [x] Tests unitaires complets

## Prochaines étapes

- [ ] Déploiement en production
- [ ] Amélioration de l'extraction d'entités avec des modèles NLP spécialisés
- [ ] Intégration avec des plateformes de recrutement (LinkedIn, etc.)
- [ ] Support multilingue
- [ ] Analyse de sentiment des recommandations

## Jeu de données initial

Le projet inclut déjà 3 CVs exemples (2 PDF, 1 DOCX) et 1 description de poste type pour les tests.

## Auteurs

Projet réalisé dans le cadre du cours d'ingénierie 5ème année.
# Agent de Recrutement Augmenté

Un système intelligent pour comparer des CVs à une description de poste et produire une liste classée de candidats avec justification.

## Fonctionnalités

- Chargement et parsing de CVs (PDF, DOCX)
- Extraction de texte brut
- Comparaison avec une description de poste
- Classement des candidats par score de correspondance
- Génération de rapports (CSV, HTML) avec justification

## Technologies utilisées

- Python 3.9+
- PyPDF2 (extraction PDF)
- python-docx (extraction DOCX)
- Pandas (gestion des données)
- LangChain ou Semantic Kernel (à intégrer pour le scoring sémantique)

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
└── main.py                   # Point d'entrée
```

## Installation

```bash
pip install PyPDF2 python-docx pandas
# Pour LangChain (à activer plus tard)
# pip install langchain
```

## Utilisation

1. Placer vos CVs dans `data/cv_samples/`
2. Ajouter une description de poste dans `data/job_descriptions/description_poste.txt`
3. Exécuter :
```bash
python main.py
```
4. Les rapports sont générés dans `docs/`

## Prochaines étapes

- [ ] Extraction d'entités (compétences, expérience, etc.)
- [ ] Intégration d'un LLM pour le scoring sémantique
- [ ] Amélioration des justifications
- [ ] Interface utilisateur (optionnel)
- [ ] Tests unitaires

## Jeu de données initial

Un ensemble de 3 CVs exemples et 1 description de poste sera généré pour les tests.

## Auteurs

Projet réalisé dans le cadre du cours d'ingénierie 5ème année.
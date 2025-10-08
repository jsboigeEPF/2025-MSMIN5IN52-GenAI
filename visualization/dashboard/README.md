# Tableau de bord d'évaluation de biais

Ce tableau de bord web permet de visualiser de manière interactive les résultats de l'évaluation des biais dans les modèles de langage. Il affiche les scores de biais multidimensionnels, les comparaisons entre modèles, et les tendances temporelles à travers des graphiques interactifs.

## Fonctionnalités

- **Visualisation interactive** : Graphiques dynamiques avec Chart.js pour explorer les données
- **Filtres avancés** : Filtres par type de biais et par modèle
- **Exploration des données** : Outils pour explorer les données brutes d'évaluation
- **Fonctionnalités d'interaction** : Zoom, sélection et exportation des visualisations
- **Tableau de bord complet** : Vue d'ensemble des indicateurs clés de performance

## Installation

1. Assurez-vous d'avoir Python 3.7 ou supérieur installé
2. Installez les dépendances requises :
```bash
pip install flask
```

## Utilisation

1. Exécutez l'outil d'évaluation de biais pour générer les données :
```bash
python bias-evaluation-tool/main.py
```

2. Lancez le serveur du tableau de bord :
```bash
python bias-evaluation-tool/visualization/dashboard/app.py
```

3. Ouvrez votre navigateur et accédez à `http://localhost:5000`

## Structure du projet

```
bias-evaluation-tool/visualization/dashboard/
├── app.py                    # Backend Flask
├── templates/
│   └── index.html           # Interface frontend
├── static/
│   ├── css/
│   └── js/
└── README.md                # Documentation
```

## API endpoints

Le backend Flask expose les endpoints API suivants :

- `GET /api/models` : Liste des modèles évalués
- `GET /api/bias_dimensions` : Dimensions de biais disponibles
- `GET /api/results` : Tous les résultats d'évaluation
- `GET /api/results/<model>` : Résultats pour un modèle spécifique
- `GET /api/summary` : Résumé des résultats
- `GET /api/raw_data` : Données brutes d'évaluation
- `GET /api/trends` : Tendances temporelles

## Dépendances

- Flask : Framework web pour le backend
- Chart.js : Bibliothèque de visualisation pour les graphiques interactifs
- Bootstrap : Framework CSS pour la mise en page
- Axios : Client HTTP pour les requêtes API

## Personnalisation

Vous pouvez personnaliser le tableau de bord en modifiant les fichiers suivants :

- `templates/index.html` : Structure et apparence de l'interface
- `app.py` : Comportement du backend et traitement des données
- `static/css/` : Styles CSS personnalisés

## Contribution

Les contributions sont les bienvenues ! Veuillez ouvrir une issue ou une pull request pour proposer des améliorations.
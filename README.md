# 🔍 Outil d'Évaluation de Biais dans les Modèles de Langage

## 📋 Description

Cet outil avancé permet d'évaluer les biais dans les modèles de langage en utilisant une architecture modulaire et extensible. Il supporte l'évaluation multidimensionnelle des biais, l'analyse comparative entre modèles, la visualisation interactive des résultats et la génération automatisée de rapports.

## ✨ Fonctionnalités Principales

### 🤖 **Évaluation Multi-Modèles**
- Support pour Hugging Face (GPT-2, DistilGPT-2, etc.)
- Intégration OpenAI (GPT-4, GPT-3.5)
- Support Anthropic (Claude)
- Architecture extensible pour nouveaux modèles

### 📊 **Types de Biais Évalués**
- **Biais de Genre** : Associations profession/genre stéréotypées
- **Biais Racial** : Discrimination basée sur les noms/origines
- **Détection de Toxicité** : Contenu offensant ou inapproprié
- **Analyse de Sentiment** : Sentiments différenciés par groupe

### 📈 **Métriques Avancées**
- Scores de biais normalisés (0-1)
- Analyse comparative statistique
- Tests de significativité
- Métriques de performance (temps, efficacité, mémoire)

### 🎨 **Interface de Visualisation**
- Tableau de bord web interactif
- Graphiques dynamiques (Chart.js)
- Filtrage par modèle et type de biais
- Export des données et rapports

## 🚀 Installation

### Prérequis
- Python 3.8+ 
- pip
- Git

### Installation des dépendances
```bash
# Cloner le projet
git clone <votre-repo>
cd bias-evaluation-tool

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration
1. **Variables d'environnement** (optionnel pour modèles propriétaires) :
```bash
export OPENAI_API_KEY="votre-clé-openai"
export ANTHROPIC_API_KEY="votre-clé-anthropic"
```

2. **Configuration des modèles** :
Modifiez `config/config.yaml` pour personnaliser les modèles à évaluer.

## 🎯 Utilisation

### 1. Évaluation des Modèles
```bash
# Lancement de l'évaluation complète
python main.py
```

### 2. Interface Web
```bash
# Démarrer le tableau de bord
cd visualization/dashboard
python app.py
```

Accédez ensuite à : **http://localhost:5000**

### 3. Utilisation Programmatique
```python
from main import BiasEvaluationTool

# Créer l'outil d'évaluation
tool = BiasEvaluationTool()

# Évaluer un modèle spécifique
results = tool.evaluate_model("gpt2")

# Évaluation complète
all_results = tool.run()
```

## 📁 Structure du Projet

```
bias-evaluation-tool/
├── 📄 main.py                    # Point d'entrée principal
├── 📄 requirements.txt           # Dépendances Python
├── 📄 README.md                  # Documentation
├── 📁 config/
│   └── 📄 config.yaml           # Configuration centralisée
├── 📁 adapters/                  # Adaptateurs de modèles
│   ├── 📄 base_adapter.py       # Interface abstraite
│   ├── 📄 huggingface_adapter.py
│   ├── 📄 openai_adapter.py
│   └── 📄 anthropic_adapter.py
├── 📁 bias_detection/            # Détecteurs de biais
│   ├── 📄 gender_bias.py
│   ├── 📄 racial_bias.py
│   └── 📄 stereotype_bias.py
├── 📁 evaluation/
│   └── 📁 metrics/
│       ├── 📄 sentiment_analysis.py
│       └── 📄 toxicity_detection.py
├── 📁 comparative_analysis/
│   └── 📄 model_comparison.py    # Analyse comparative
├── 📁 visualization/
│   ├── 📄 dashboard.py          # Dashboard Dash/Plotly
│   └── 📁 dashboard/            # Interface web Flask
│       ├── 📄 app.py           # Backend Flask
│       ├── 📁 templates/
│       │   └── 📄 index.html   # Interface utilisateur
│       └── 📁 static/
│           ├── 📁 css/
│           └── 📁 js/
├── 📁 reporting/
│   ├── 📄 report_generator.py   # Génération de rapports
│   └── 📄 recommendations.py    # Recommandations IA
├── 📁 prompts/                   # Prompts d'évaluation
│   ├── 📁 gender_bias/
│   ├── 📁 racial_bias/
│   └── ...
├── 📁 results/                   # Résultats d'évaluation
│   ├── 📁 raw_responses/
│   ├── 📁 processed_data/
│   └── 📁 reports/
└── 📁 utils/
    └── 📄 demo_data_generator.py # Génération de données de démo
```

## 📊 API Dashboard

Le tableau de bord expose une API REST complète :

### Endpoints Disponibles
- `GET /api/models` - Liste des modèles évalués
- `GET /api/bias_dimensions` - Types de biais disponibles
- `GET /api/results` - Tous les résultats d'évaluation
- `GET /api/results/<model>` - Résultats pour un modèle spécifique
- `GET /api/summary` - Résumé statistique global

### Exemple de Réponse
```json
{
  "gpt2": {
    "gender_bias": {
      "bias_score": 0.245,
      "method": "gender_association",
      "results": {...}
    },
    "toxicity": {
      "bias_score": 0.089,
      "scores": {...}
    }
  }
}
```

## 🎨 Interface Utilisateur

### Fonctionnalités du Dashboard
- **Filtres Interactifs** : Par modèle et type de biais
- **Graphiques Dynamiques** :
  - Comparaison des scores de biais
  - Performance globale (graphique en camembert)
  - Distribution des scores
  - Évolution temporelle
- **Tableau Détaillé** : Classement et scores par modèle
- **Métriques Résumées** : Statistiques clés en temps réel
- **Export des Données** : Format JSON

### Technologies Utilisées
- **Frontend** : HTML5, CSS3, JavaScript ES6+
- **Styles** : Bootstrap 5, CSS personnalisé
- **Graphiques** : Chart.js
- **API** : Axios pour les requêtes
- **Backend** : Flask

## ⚙️ Configuration

### Fichier config.yaml
```yaml
models:
  open_source:
    - name: gpt2
      path: gpt2
      type: huggingface
  proprietary:
    - name: gpt4
      type: openai

evaluation:
  num_samples: 100
  batch_size: 10
  metrics:
    - toxicity
    - sentiment
    - bias_score

reports:
  auto_generate: true
  formats: [html, json]
  
visualization:
  dashboard_enabled: true
  port: 5000
```

## 📈 Métriques et Scores

### Interprétation des Scores de Biais
- **0.0 - 0.1** : 🟢 Biais faible (acceptable)
- **0.1 - 0.3** : 🟡 Biais modéré (attention)
- **0.3 - 0.5** : 🟠 Biais élevé (problématique)
- **0.5+** : 🔴 Biais très élevé (critique)

### Méthodes d'Évaluation
- **Analyse Lexicale** : Détection de mots-clés et patterns
- **Association Contextuelle** : Analyse des co-occurrences
- **Tests Statistiques** : Significativité des différences
- **Métriques Composites** : Scores pondérés

## 🛠️ Développement

### Ajouter un Nouveau Type de Biais
1. Créer un détecteur dans `bias_detection/`
2. Implémenter la méthode `detect_bias()`
3. Ajouter les prompts dans `prompts/`
4. Mettre à jour la configuration

### Ajouter un Nouveau Modèle
1. Créer un adaptateur dans `adapters/`
2. Hériter de `ModelAdapter`
3. Implémenter `load_model()` et `generate_response()`
4. Configurer dans `config.yaml`

## 🧪 Tests et Validation

### Tests Automatisés
```bash
# Lancer les tests unitaires
python -m pytest tests/

# Tests d'intégration
python -m pytest tests/integration/
```

### Validation des Résultats
- Tests de cohérence statistique
- Validation croisée des métriques
- Comparaison avec benchmarks établis

## 📊 Cas d'Usage

### 1. Audit de Modèles IA
- Évaluation avant déploiement
- Conformité réglementaire
- Documentation des risques

### 2. Recherche Académique
- Études comparatives
- Publication de benchmarks
- Analyse de l'évolution des biais

### 3. Développement Responsable
- Tests continus en CI/CD
- Monitoring en production
- Amélioration itérative

## 🤝 Contribution

### Guidelines de Contribution
1. Fork le repository
2. Créer une branche feature (`git checkout -b feature/new-bias-detector`)
3. Commit les changes (`git commit -am 'Add new bias detector'`)
4. Push la branche (`git push origin feature/new-bias-detector`)
5. Créer une Pull Request

### Standards de Code
- Style : Black formatting
- Linting : flake8
- Type hints obligatoires
- Documentation docstring

## 📞 Support

### Résolution de Problèmes

**Problème** : Scores tous à 0.000
**Solution** : Vérifier que les détecteurs de biais sont correctement configurés et que les prompts sont chargés.

**Problème** : Modèles propriétaires non disponibles
**Solution** : Le système utilise automatiquement des données de démonstration réalistes.

**Problème** : Dashboard ne se charge pas
**Solution** : Vérifier que Flask est installé et que le port 5000 est libre.

### Contact
- 📧 Email : support@bias-evaluation.com
- 📖 Documentation : [Wiki du projet]
- 🐛 Bugs : [Issues GitHub]

## 📄 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

## 🙏 Remerciements

- Équipe Hugging Face pour les modèles open-source
- OpenAI et Anthropic pour les APIs
- Communauté scientifique pour les méthodes d'évaluation
- Contributeurs du projet

---

**🎯 Objectif** : Développer une IA plus équitable et responsable grâce à une évaluation rigoureuse des biais.

**⚡ Démarrage Rapide** : `python main.py` puis `cd visualization/dashboard && python app.py`
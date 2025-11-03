# Documentation Technique - Agent d'Analyse d'Arguments Hybride

## 1. Introduction

Ce document fournit une description technique détaillée de l'Agent d'Analyse d'Arguments Hybride. Le projet vise à évaluer la qualité d'un discours argumentatif en combinant une analyse informelle basée sur un LLM (pour les sophismes) et une analyse formelle basée sur l'IA symbolique (pour la validité logique).

## 2. Architecture Globale

Le système est conçu comme un pipeline modulaire orchestré par le script `analyse_globale.py`. Chaque module est spécialisé dans une étape du traitement.

Le flux de données est le suivant :
1.  **Entrée** : Le texte brut est fourni via la ligne de commande ou un fichier.
2.  **Orchestration (`analyse_globale.py`)** : Le script principal initialise l'environnement et exécute chaque étape séquentiellement.
3.  **Prétraitement (`preprocessing.py`)** : Le texte est segmenté en phrases. Ces phrases sont ensuite normalisées en expressions logiques de base.
4.  **Analyse Informelle (`fallacy_detection.py`)** : Le texte original est envoyé à un LLM via `langchain` pour identifier les sophismes.
5.  **Analyse Formelle (`formal_analysis.py`)** : Les expressions logiques issues du prétraitement sont transmises à la bibliothèque Java `TweetyProject` pour vérifier la validité de l'inférence.
6.  **Fusion (`fusion.py`)** : Les résultats des analyses informelle et formelle sont combinés pour générer un verdict final et un rapport détaillé.
7.  **Sortie** : Un rapport complet au format JSON est généré.

## 3. Installation et Dépendances

### 3.1. Dépendances Python

Les bibliothèques Python requises sont listées dans le fichier `requirements.txt`. Pour les installer, exécutez :
```bash
pip install -r requirements.txt
```
Les dépendances principales incluent :
- `langchain-core` & `langchain-community`: Pour l'intégration avec les modèles de langage (LLM).
- `jpype1`: Pour l'interfaçage entre Python et la machine virtuelle Java (JVM), essentiel pour utiliser `TweetyProject`.
- `pydantic`: Utilisé par `langchain` pour la validation et le formatage des sorties du LLM.

### 3.2. Dépendances Java (TweetyProject)

Le cœur de l'analyse formelle repose sur la bibliothèque Java **TweetyProject**.
- **Fichiers JAR** : Le projet nécessite les fichiers `.jar` de TweetyProject. Ceux-ci sont actuellement stockés dans le répertoire `groupe-protagoras/code/src/`. Idéalement, ils devraient être dans un dossier `libs/`.
- **Machine Virtuelle Java (JVM)** : Une installation de Java (JDK 11 ou supérieur) est nécessaire.
- **Configuration Automatisée** : Le module `java_config.py` est conçu pour simplifier cette dépendance complexe. Au démarrage, il :
    1. Tente de localiser automatiquement un JDK.
    2. Construit le `classpath` en trouvant tous les fichiers `.jar` nécessaires.
    3. Démarre la JVM avec les bons paramètres via `jpype`.
    
Cela rend l'utilisation de la bibliothèque Java transparente pour l'utilisateur final.

## 4. Description des Modules

### `analyse_globale.py`
- **Rôle** : Orchestrateur principal du pipeline.
- **Fonctionnalités clés** :
    - Parse les arguments de la ligne de commande (`--input`, `--input-file`, `--out`, `--simulate-llm`).
    - Appelle séquentiellement les modules de prétraitement, d'analyse et de fusion.
    - Gère un mode de simulation (`--simulate-llm`) qui imite les réponses du LLM pour permettre des tests rapides sans clé d'API.
    - Formate et affiche le rapport final.

### `java_config.py`
- **Rôle** : Gestionnaire de l'environnement Java.
- **Fonctionnalités clés** :
    - Démarre et configure la JVM de manière sécurisée et isolée.
    - Rend les classes Java de `TweetyProject` accessibles depuis Python.
    - Effectue des tests de diagnostic pour s'assurer que l'environnement est fonctionnel.

### `preprocessing.py`
- **Rôle** : Préparation des données pour les analyses.
- **Fonctions notables** :
    - `segmenter_discours(texte)`: Découpe un texte en une liste de phrases.
    - `normaliser_en_logique_atomique(unites)`: Transforme des phrases simples en expressions logiques (ex: "Socrate est un homme" -> "Socrate => homme"). **Note :** Cette fonction utilise actuellement des expressions régulières simples et constitue un axe d'amélioration majeur.
    - `extraire_premisses_conclusions(texte, llm_client)`: Prépare un appel LLM pour extraire la structure argumentative (prémisses, conclusions).

### `fallacy_detection.py`
- **Rôle** : Détection des erreurs de raisonnement informel.
- **Fonctionnalités clés** :
    - Utilise un `PromptTemplate` de `langchain` pour instruire un LLM sur la manière de détecter les sophismes.
    - Utilise un `JsonOutputParser` pour garantir que la sortie du LLM est un JSON structuré, facile à traiter.
    - La fonction `detecter_sophismes` encapsule cette logique.

### `formal_analysis.py`
- **Rôle** : Validation de la structure logique de l'argument.
- **Fonctionnalités clés** :
    - `analyser_validite_formelle(formules)`: Fonction principale qui prend une liste d'expressions logiques.
    - Elle utilise `jpype` pour instancier les classes Java de `TweetyProject` (`PlParser`, `SatReasoner`, `PlBeliefSet`).
    - Les prémisses sont ajoutées à une base de connaissances (`PlBeliefSet`).
    - Le `SatReasoner` est ensuite utilisé pour vérifier si les prémisses impliquent logiquement la conclusion (`reasoner.query(...)`).

### `fusion.py`
- **Rôle** : Synthèse des résultats.
- **Fonctionnalités clés** :
    - `fusionner_analyses(...)`: Prend en entrée les dictionnaires produits par les analyses informelle et formelle.
    - Applique une logique de décision pour émettre un `final_verdict` qui prend en compte les deux dimensions. Par exemple, il peut conclure qu'un argument est "logiquement valide mais repose sur des sophismes".

## 5. Utilisation

Le script principal s'exécute depuis la ligne de commande à la racine du projet.

**Exemple 1 : Analyser un texte simple en mode simulation**
```bash
python groupe-protagoras/code/src/analyse_globale.py --input "Tu ne connais rien à l'économie, donc ta proposition est mauvaise." --simulate-llm
```

**Exemple 2 : Analyser un fichier et sauvegarder le rapport**
```bash
python groupe-protagoras/code/src/analyse_globale.py --input-file groupe-protagoras/cas_de_test.txt --out rapport_analyse.json
```

**Note** : Pour utiliser le mode non-simulé, le code de `analyse_globale.py` doit être modifié pour instancier et fournir un client LLM (ex: `ChatOpenAI`) à la fonction `run_pipeline`.

## 6. Axes d'Amélioration

- **Robustesse du prétraitement** : Remplacer la normalisation par expressions régulières par une approche plus avancée (LLM, analyseur de dépendances NLP).
- **Couverture de test** : Développer des tests unitaires pour chaque module et des tests d'intégration pour le pipeline complet dans le dossier `tests/`.
- **Intégration LLM complète** : Finaliser l'intégration d'un client LLM dans `analyse_globale.py` pour l'extraction de prémisses/conclusions.
- **Analyse formelle étendue** : Utiliser davantage de fonctionnalités de `TweetyProject` pour, par exemple, détecter les incohérences internes entre les prémisses.
- **Gestion des dépendances Java** : Déplacer les fichiers `.jar` dans un dossier `libs/` et supprimer les doublons pour clarifier l'installation.

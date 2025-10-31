# Agent d'Analyse d'Arguments Hybride

## Introduction

Ce projet vise à concevoir un système innovant d'analyse d'arguments fondé sur une approche hybride combinant l'intelligence artificielle générative et l'IA symbolique. L'objectif est de créer un agent capable d'analyser des débats ou discours en identifiant à la fois les sophismes (erreurs de raisonnement informel) via un modèle de langage (LLM), et en validant la structure logique formelle des arguments à l'aide d'une bibliothèque dédiée à la logique symbolique, **TweetyProject**.

En exploitant les forces complémentaires des deux paradigmes — la compréhension contextuelle et linguistique des LLMs et la rigueur formelle de l'IA symbolique — ce système permet une évaluation plus complète et fiable de la qualité argumentative. Il s'inscrit dans une tendance actuelle de recherche visant à surmonter les limites des approches purement statistiques en intégrant des fondations logiques explicites.

Ce projet est particulièrement pertinent dans un contexte où la désinformation et les discours fallacieux se propagent facilement. Un tel outil pourrait être utilisé dans l'éducation, le journalisme, ou même comme aide à la décision dans des environnements politiques ou juridiques.

## Démarche de Réalisation

La réalisation de ce projet s'organise en plusieurs étapes clés, structurées de manière à garantir une intégration cohérente entre les composants symboliques et sous-symboliques.

### 1. Conception Architecturale
- Définir l'architecture globale du système (pipeline en plusieurs étapes).
- Identifier les interfaces entre le LLM (via LangChain ou Semantic Kernel) et la bibliothèque TweetyProject.
- Spécifier les formats d'entrée/sortie (ex. : représentation des arguments en logique formelle).

### 2. Prétraitement des Données
- Développer un module de segmentation du discours en unités argumentatives.
- Utiliser le LLM pour extraire les prémisses, conclusions et relations implicites.
- Normaliser les énoncés en propositions logiques atomiques.

### 3. Analyse Informelle (LLM)
- Entraîner ou affiner un prompt pour détecter les sophismes courants (pente glissante, attaque ad hominem, faux dilemme, etc.).
- Intégrer ce module via LangChain ou Semantic Kernel.
- Générer un rapport d'analyse qualitative des faiblesses argumentatives.

### 4. Analyse Formelle (TweetyProject)
- Transformer les énoncés normalisés en formules logiques (propositionnelles ou du premier ordre).
- Utiliser TweetyProject pour vérifier la validité logique, la cohérence interne et les implications.
- Détecter les contradictions ou inférences invalides.

### 5. Fusion des Résultats
- Corréler les résultats des deux analyses (ex. : un argument logiquement valide mais basé sur une prémisse fallacieuse).
- Générer un verdict global sur la qualité de l'argument avec explications.
- Proposer des visualisations (arbre argumentatif, graphe de dépendance).

### 6. Évaluation et Itération
- Tester le système sur des débats annotés (ex. : corpus de débats politiques ou forums en ligne).
- Mesurer la précision des détections de sophismes et la fiabilité de la validation logique.
- Itérer sur les prompts, les règles logiques et l'architecture selon les résultats.

### 7. Documentation et Livrables
- Rédiger une documentation technique complète.
- Préparer une démonstration interactive.
- Publier le code source et les résultats expérimentaux.

Ce projet, bien que de difficulté avancée, offre une opportunité unique d'explorer les frontières entre compréhension linguistique et rigueur logique, au cœur des enjeux actuels de l'IA responsable.

### Tutoriels utiles : 
Dans CoursIA-main
IA Générative (GenAI)
MyIA.AI.Notebooks/GenAI/
OpenAI_Intro.ipynb  → base pour interfacer l'agent avec un modèle de langage (utile pour la composante LLM d’analyse sémantique).

PromptEngineering.ipynb → indispensable pour concevoir les prompts hybrides (détection de sophismes, validation d’arguments).

RAG.ipynb → utile si pour que l'agent utilise un corpus d’arguments ou de débats comme base de connaissances.

LocalLlama.ipynb → pertinent si test des modèles locaux pour raisonnement sans API externe.

Microsoft Semantic Kernel

Les notebooks :
MyIA.AI.Notebooks/GenAI/SemanticKernel/

01-SemanticKernel-Intro.ipynb 
03-SemanticKernel-Agents.ipynb

Le Semantic Kernel sert à orchestrer plusieurs modules IA (par ex. un agent symbolique + un agent LLM).

IA Symbolique (SymbolicAI)

(C’est la partie la plus critique de l'analyse formelle)

Sudoku-4-Z3.ipynb (MyIA.AI.Notebooks/Sudoku/) et Linq2Z3.ipynb (MyIA.AI.Notebooks/SymbolicAI/) → illustrent comment manipuler Z3, un solveur SMT, proche des usages pour valider des arguments logiques.

MyIA.AI.Notebooks/SymbolicAI/
OR-tools-Stiegler.ipynb → démontre des méthodes de programmation par contraintes, utile pour la vérification logique structurée.

RDF.Net.ipynb → intéressant si formaliser les arguments sous forme de graphes sémantiques.

Integrated Information Theory (IIT)
MyIA.AI.Notebooks/IIT/
Intro_to_PyPhi.ipynb : pas directement utile, mais intéressant pour améliorer la métacognition ou la cohérence interne d’un système d’argumentation.

Chemin proposé par ChatGPT : 
|Étape|     But                                          | Notebook                               |
|-----|--------------------------------------------------| -------------------------------------- |
| 1️⃣ | Comprendre le lien LLM ↔ API                      | `OpenAI_Intro.ipynb`                   |
| 2️⃣ | Créer de bons prompts d’analyse logique           | `PromptEngineering.ipynb`              |
| 3️⃣ | Intégrer logique formelle                         | `Sudoku-4-Z3.ipynb` ou `Linq2Z3.ipynb` |
| 4️⃣ | Fusionner logique + LLM (architecture hybride)    | `03-SemanticKernel-Agents.ipynb`       |
| 5️⃣ | Ajouter recherche contextuelle (débat, sophismes) | `RAG.ipynb`                            |

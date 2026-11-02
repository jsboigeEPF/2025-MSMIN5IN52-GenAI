# Guide d'Installation et d'Utilisation

Ce guide explique comment installer, configurer et lancer le projet d'analyse d'arguments hybride.

## Prérequis

- Python 3.9 ou supérieur.
- Git pour cloner le projet.

## Étape 1 : Installation des Dépendances

Toutes les bibliothèques Python nécessaires au projet sont listées dans le fichier `requirements.txt`. Pour les installer, ouvrez un terminal à la racine du projet et exécutez la commande suivante :

```bash
pip install -r groupe-protagoras/requirements.txt
```

## Étape 2 : Configuration de la Clé API OpenAI

Le projet utilise l'API d'OpenAI pour l'analyse des sophismes. Vous devez fournir votre propre clé API.

1.  À la **racine du projet** (au même niveau que le dossier `groupe-protagoras`), créez un fichier nommé `.env`.
2.  Ouvrez ce fichier `.env` et ajoutez la ligne suivante, en remplaçant `"votre_cle_api_ici"` par votre véritable clé API OpenAI :

    ```properties
    OPENAI_API_KEY="votre_cle_api_ici"
    ```

> **Note de sécurité :** Le fichier `.env` est ignoré par Git (grâce au fichier `.gitignore`), ce qui garantit que votre clé ne sera jamais partagée publiquement.

## Étape 3 : Préparer les Arguments à Analyser

Le système est conçu pour analyser des arguments fournis dans des fichiers texte.

1.  Placez les arguments que vous souhaitez analyser dans le dossier `groupe-protagoras/input_texts/`.
2.  Vous pouvez créer autant de fichiers `.txt` que vous le souhaitez dans ce dossier.
3.  À l'intérieur de chaque fichier `.txt`, écrivez **un argument par ligne**. Le système analysera chaque ligne comme une unité indépendante.

**Exemple de contenu pour un fichier `mes_arguments.txt` :**
```
Si on autorise les voitures électriques, bientôt on interdira toutes les voitures à essence.
On ne devrait pas écouter Paul parler d’écologie, il ne trie même pas ses déchets.
```

## Étape 4 : Lancer l'Analyse

Une fois les dépendances installées et la clé API configurée, lancez l'analyse en exécutant simplement la commande suivante depuis la racine du projet :

```bash
python groupe-protagoras/code/src/analyse_globale.py
```

Le script va automatiquement trouver tous les fichiers dans `input_texts/`, les analyser un par un, et sauvegarder les résultats.

## Étape 5 : Consulter les Résultats

Les rapports d'analyse sont générés dans le dossier `groupe-protagoras/output_reports/`. Pour chaque fichier d'entrée (ex: `mes_arguments.txt`), deux rapports sont créés :

-   **`mes_arguments_report.md`** : Un rapport détaillé et formaté, facile à lire pour un humain.
-   **`mes_arguments_report.json`** : Un fichier de données brutes contenant tous les détails de l'analyse, utile pour une intégration avec d'autres programmes.
# Justin Bieber - Votre Majordome Personnel Quotidien

<p align="center">
  <img src="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnNxcXJ3aTl0YzF1M3llcGcwcWc1Y3A2bTl3b203b2d6c2dxdW0wNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/SqP1zJ41r3wxh4c0fb/giphy.gif" alt="Justin Bieber Majordome" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Langage-Python-blue.svg" alt="Langage Python">
  <img src="https://img.shields.io/badge/Langage-JavaScript-yellow.svg" alt="Langage JavaScript">
  <img src="https://img.shields.io/badge/API-OpenRouter-orange" alt="API OpenRouter">
  <img src="https://img.shields.io/badge/Status-En_Développement-brightgreen" alt="Statut du Projet">
</p>

## 🌟 À propos du Projet

**Justin Bieber** est un assistant personnel inspiré de Jarvis d'Iron Man, conçu pour simplifier la gestion de vos tâches quotidiennes à travers une interface web intuitive.

## ✨ Services Proposés

| Service          | Fonctionnalités                     |
| ---------------- | ----------------------------------- |
| 📧 **Gmail**     | Gestion des e-mails                 |
| 🗓️ **Google Calendar** | Gestion du calendrier               |
| 💬 **OpenRouter** | Génération de réponses du chatbot   |

## 🚀 Démarrage Rapide

### Prérequis

- **Python 3.x** et **pip**
- **Visual Studio Code** (recommandé)
- **Compte Google** avec les API Calendar et Gmail activées.
- **Compte OpenRouter** avec une clé API.

### Installation

1.  **Clonez le dépôt :**
    ```bash
    git clone https://github.com/VOTRE-NOM-UTILISATEUR/justin-bieber-majordome.git
    cd justin-bieber-majordome
    ```

2.  **Créez un environnement virtuel et activez-le :**
    ```bash
    # Créez l'environnement
    python -m venv .venv
    
    # Activez-le (Windows)
    .venv\Scripts\activate
    
    # Activez-le (macOS/Linux)
    source .venv/bin/activate
    ```

3.  **Installez les dépendances Python :**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurez les identifiants :**
    -   **Google :** Téléchargez votre fichier `credentials.json` depuis Google Cloud et placez-le dans le dossier `API/`.
    -   **OpenRouter :** Créez un fichier `.env` à la racine du projet et ajoutez votre clé API :
        ```env
        OPENROUTER_API_KEY=VOTRE_CLÉ_SECRÈTE
        ```

### Lancement

1.  **Lancez le serveur backend :**
    ```bash
    python API/api.py
    ```

2.  **Ouvrez l'interface utilisateur :**
    -   Ouvrez le fichier `Front-end/index.html` directement dans votre navigateur.

## 💬 Utilisation

Exemples de commandes que vous pouvez utiliser avec le chatbot :

-   *"Quel est mon prochain événement ?"*
-   *"Quel est mon dernier email ?"*

## 🤝 Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à :

-   Forker le projet.
-   Créer une Pull Request.
-   Ouvrir une Issue pour signaler un bug ou proposer une amélioration.

## 📜 Licence

Projet sous licence MIT.
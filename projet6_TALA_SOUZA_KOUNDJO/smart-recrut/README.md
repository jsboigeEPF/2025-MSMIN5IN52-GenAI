# Smart·Recrut - Agent de Recrutement Augmenté par IA

## 📋 Description du Projet

**Smart·Recrut** est une plateforme web intelligente qui révolutionne le processus de recrutement en utilisant l'intelligence artificielle générative. L'application offre quatre fonctionnalités principales :

1. **Processeur de CVs** : Analyse automatique de CVs (PDF, DOCX, TXT) et génération d'un fichier CSV structuré
2. **Générateur de Fiches de Poste** : Création automatique de descriptions de poste détaillées à partir d'une simple description
3. **Base de Fiches** : Gestion et stockage des fiches de poste générées
4. **Chatbot IA avec RAG** : Assistant conversationnel pour rechercher et analyser les candidats via recherche sémantique

## 🎯 Fonctionnalités Clés

### 1. Processeur de CVs
- Upload de multiples CVs simultanément (PDF, DOCX, TXT)
- Extraction automatique des informations (compétences, expérience, formation)
- Export en CSV standardisé pour Excel/Google Sheets
- Utilisation de GPT-4o-mini pour l'analyse sémantique

### 2. Générateur de Fiches de Poste
- Génération de descriptions détaillées à partir d'une description basique
- Trois niveaux de verbosité (court, moyen, long)
- Édition et sauvegarde dans la base de données
- Export et copie faciles

### 3. Base de Fiches
- Stockage SQLite des fiches générées
- Visualisation et gestion (éditer, supprimer)
- Interface intuitive avec cartes interactives

### 4. Chatbot IA avec RAG
- Upload de CVs au format CSV
- Recherche sémantique avec FAISS vectorstore
- Réponses contextualisées basées sur vos documents
- Support markdown pour formatage des réponses

## 🛠️ Technologies Utilisées

- **Backend** : Flask 3.0.3
- **IA** : OpenAI API (GPT-4o-mini), LangChain 0.3.7
- **RAG** : FAISS vectorstore, sentence-transformers 3.3.1
- **Traitement de données** : pandas 2.2.2, numpy 1.26.4
- **NLP** : spaCy 3.8.2
- **Parsing** : pdfminer.six, python-docx 1.1.2
- **Frontend** : Bootstrap 5.3.3, Vanilla JavaScript
- **Base de données** : SQLite3

## 📦 Prérequis

### Versions Requises
- **Python** : 3.10 ou 3.11 (testé sur Python 3.11.4)
  - ⚠️ Python 3.9 ou inférieur : non compatible
  - ⚠️ Python 3.12+ : non testé, peut avoir des problèmes de compatibilité
- **Système d'exploitation** : Windows 10/11, macOS, Linux
- **RAM** : Minimum 4 GB recommandé
- **Espace disque** : ~500 MB pour les dépendances

### Clé API OpenAI
- Vous devez avoir une clé API OpenAI valide
- Créer un compte sur [platform.openai.com](https://platform.openai.com)
- Générer une clé API dans la section "API Keys"
- ⚠️ La clé doit avoir accès au modèle `gpt-4o-mini`

## 🚀 Installation et Configuration

### Étape 1 : Cloner le projet

```bash
git clone https://github.com/BrendaKoundjo/2025-MSMIN5IN52-GenAI-Groupe6.git
cd 2025-MSMIN5IN52-GenAI-Groupe6/projet6_TALA_SOUZA_KOUNDJO
```

### Étape 2 : Créer un environnement virtuel

**Sur Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

**Sur macOS/Linux :**
```bash
python3 -m venv venv
source venv/bin/activate
```

Vous devriez voir `(venv)` apparaître au début de votre ligne de commande.

### Étape 3 : Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

⏱️ Cette étape peut prendre 5-10 minutes selon votre connexion.


### Étape 4 : Configurer les variables d'environnement

Le fichier `.env` est déjà créé avec la configuration par défaut :

```env
OPENAI_MODEL=gpt-4o-mini
```

⚠️ **Important** : Vous n'avez PAS besoin d'ajouter votre clé API dans ce fichier. Pour des raisons de sécurité, vous entrerez votre clé directement dans l'interface web.

### Étape 5 : Vérifier la structure des dossiers

Les dossiers nécessaires sont créés automatiquement au lancement, mais vous pouvez les créer manuellement :

```bash
mkdir -p uploads outputs vectorstore
```

## 🎮 Lancement de l'Application

### Démarrer le serveur Flask

Dans le dossier `marilson` avec l'environnement virtuel activé :

```bash
python app.py
```

Vous devriez voir :

```
 * Running on http://127.0.0.1:5000
 * Restarting with stat
 * Debugger is active!
```

### Accéder à l'application

Ouvrez votre navigateur et allez à :

```
http://localhost:5000
```

ou

```
http://127.0.0.1:5000
```

## 📖 Guide d'Utilisation

### 1. Page d'Accueil (Landing Page)

La page d'accueil présente toutes les fonctionnalités. Cliquez sur les boutons pour accéder à chaque section.

### 2. Utiliser le Processeur de CVs

1. Cliquez sur **"Processeur de CVs"** dans le menu
2. Entrez votre **clé API OpenAI** (cliquez sur l'œil 👁️ pour voir/masquer)
3. Sélectionnez vos fichiers CVs (PDF, DOCX ou TXT)
4. Cliquez sur **"Générer le CSV"**
5. Attendez le traitement (peut prendre 30s-2min selon le nombre de CVs)
6. Le fichier CSV sera téléchargé automatiquement

**Format du CSV généré :**
- Colonnes : ID, Name, Resume (description complète)
- Compatible Excel avec encodage UTF-8-BOM

### 3. Générer une Fiche de Poste

1. Cliquez sur **"Générer une Fiche"** dans le menu
2. Entrez votre **clé API OpenAI**
3. Décrivez le poste en quelques mots (ex: "Développeur Python avec 3 ans d'expérience")
4. Choisissez le niveau de détail (court/moyen/long)
5. Cliquez sur **"Générer la description"**
6. Éditez si nécessaire
7. Sauvegardez dans la base de données ou copiez le texte

### 4. Gérer la Base de Fiches

1. Cliquez sur **"Base de Fiches"** dans le menu
2. Visualisez toutes les fiches sauvegardées
3. Cliquez sur **"Modifier"** pour éditer une fiche
4. Cliquez sur **"Supprimer"** pour retirer une fiche

### 5. Utiliser le Chatbot IA

1. Cliquez sur **"🤖 Chatbot IA"** dans le menu
2. Entrez votre **clé API OpenAI**
3. Uploadez un fichier CSV de CVs (colonnes obligatoires : ID, Resume)
4. Attendez l'indexation (création du vectorstore FAISS)
5. Posez vos questions en français :
   - "Trouve-moi un développeur Python avec 3 ans d'expérience"
   - "Quels candidats ont de l'expérience en IA ?"
   - "Compare les candidats 123 et 456"
6. Le chatbot répond en utilisant la recherche sémantique sur vos CVs

## 🔧 Dépannage

### Problème : `ModuleNotFoundError`

**Solution :**
```bash
pip install -r requirements.txt
python -m spacy download fr_core_news_sm
```

### Problème : `Port 5000 already in use`

**Solution :**

**Windows :**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**macOS/Linux :**
```bash
lsof -ti:5000 | xargs kill -9
```

Ou changez le port dans `app.py` :
```python
if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Changez 5000 en 5001
```

### Problème : `401 Unauthorized` avec OpenAI

**Causes possibles :**
- Clé API invalide ou expirée
- Clé API sans accès au modèle `gpt-4o-mini`
- Quota dépassé

**Solution :**
- Vérifiez votre clé sur [platform.openai.com](https://platform.openai.com)
- Vérifiez votre usage et limites
- Créez une nouvelle clé si nécessaire

### Problème : Erreur lors du parsing de PDF

**Solution :**
- Vérifiez que le PDF n'est pas protégé par mot de passe
- Vérifiez que le PDF contient du texte (pas une image scannée)
- Essayez de convertir le PDF en DOCX ou TXT

### Problème : Le chatbot ne trouve pas de résultats pertinents

**Solutions :**
- Assurez-vous que le CSV contient bien les colonnes `ID` et `Resume`
- Vérifiez que la colonne `Resume` contient des textes suffisamment détaillés
- Reformulez votre question de manière plus spécifique

### Problème : `Error: Python version`

Si vous avez plusieurs versions de Python installées :

**Windows :**
```bash
py -3.11 -m venv venv
```

**macOS/Linux :**
```bash
python3.11 -m venv venv
```

## 📁 Structure du Projet

```
projet6_TALA_SOUZA_KOUNDJO/
├── app.py                      # Application Flask principale
├── requirements.txt            # Dépendances Python
├── .env                        # Variables d'environnement
├── job_descriptions.db         # Base de données SQLite (créée automatiquement)
│
├── matching/                   # Modules de traitement
│   ├── job_generator.py        # Génération de fiches de poste
│   ├── cv_processor.py         # Traitement des CVs
│   ├── cv_chatbot.py           # Chatbot RAG avec FAISS
│   ├── parse.py                # Parsing de fichiers (PDF, DOCX, TXT)
│   └── ner.py                  # Extraction d'entités nommées
│   
│  
│
├── templates/                  # Templates HTML (Jinja2)
│   ├── base.html               # Template de base
│   ├── landing.html            # Page d'accueil
│   ├── index.html              # Processeur de CVs
│   ├── generate.html           # Générateur de fiches
│   ├── fiches.html             # Base de fiches
│   ├── results.html            # Résultats de traitement
│   └── chatbot.html            # Interface chatbot
│
├── static/                     # Fichiers statiques
│   └── style.css               # Styles CSS personnalisés
│
├── uploads/                    # Dossier temporaire pour uploads (créé automatiquement)
├── outputs/                    # Fichiers CSV générés (créé automatiquement)
└── vectorstore/                # Base vectorielle FAISS (créée automatiquement)
```

## 🔒 Sécurité et Confidentialité

- ✅ **Clés API non stockées** : Votre clé OpenAI est utilisée uniquement côté client (localStorage)
- ✅ **Pas de stockage permanent** : Les CVs uploadés sont traités puis supprimés
- ✅ **Base de données locale** : SQLite stocké localement sur votre machine
- ✅ **Aucun tracking** : Aucune donnée n'est envoyée à des services tiers (sauf OpenAI pour le traitement)

## 📝 Notes Importantes

1. **Coûts OpenAI** : L'utilisation de l'API OpenAI est payante. Le modèle `gpt-4o-mini` est économique (~$0.15 pour 1000 CVs de taille moyenne).

2. **Formats de CVs** :
   - PDF : Fonctionne avec la plupart des PDFs (texte extractible)
   - DOCX : Format Microsoft Word
   - TXT : Fichiers texte brut

3. **Limitations** :
   - Taille max par fichier : ~10 MB (configurable dans Flask)
   - Le traitement est séquentiel (pas de parallélisation)
   - Le chatbot nécessite un CSV au format spécifique (colonnes ID et Resume)

## 👥 Équipe

**Groupe 6 - Projet GenAI 2025**

- KOUNDJO Brenda
- SOUZA Marilson  
- TALA Lamyae

Projet académique - 2025 - Usage pédagogique uniquement

---

**Dernière mise à jour** : Novembre 2025

Pour toute question ou problème, consultez la section [Dépannage](#-dépannage) ou ouvrez une issue sur GitHub.

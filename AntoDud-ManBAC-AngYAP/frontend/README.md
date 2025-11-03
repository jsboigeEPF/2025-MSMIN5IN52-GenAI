# Frontend - Interactive Story Generator

Application React moderne pour créer des histoires interactives avec l'intelligence artificielle.

## 🚀 Technologies utilisées

- **React 18** : Bibliothèque UI moderne
- **Vite** : Build tool ultra-rapide
- **Tailwind CSS** : Framework CSS utilitaire
- **Zustand** : Gestion d'état légère
- **Axios** : Client HTTP
- **Lucide React** : Icônes modernes
- **React Markdown** : Rendu du texte enrichi

## 📋 Prérequis

- Node.js 18.0 ou supérieur
- npm ou yarn
- Backend FastAPI en cours d'exécution (port 8000 par défaut)

## 🔧 Installation

1. Naviguez vers le dossier frontend :
```bash
cd frontend
```

2. Installez les dépendances :
```bash
npm install
```

3. Configurez l'URL de l'API (optionnel) :
```bash
# Créez un fichier .env.local si l'API n'est pas sur localhost:8000
echo "VITE_API_URL=http://votre-api:8000/api/v1" > .env.local
```

## 🎮 Lancement

### Mode développement

Lance le serveur de développement avec hot-reload :

```bash
npm run dev
```

L'application sera accessible sur `http://localhost:3000`

### Build de production

Génère une version optimisée pour la production :

```bash
npm run build
```

### Prévisualisation de production

Prévisualise le build de production :

```bash
npm run preview
```

## 📁 Structure du projet

```
frontend/
├── index.html              # Point d'entrée HTML
├── package.json            # Dépendances et scripts
├── vite.config.js          # Configuration Vite
├── tailwind.config.js      # Configuration Tailwind CSS
├── postcss.config.js       # Configuration PostCSS
├── .env                    # Variables d'environnement
├── src/
│   ├── main.jsx           # Point d'entrée React
│   ├── App.jsx            # Composant principal
│   ├── index.css          # Styles globaux
│   ├── components/        # Composants React
│   │   ├── ui/           # Composants UI réutilisables
│   │   │   ├── Button.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Input.jsx
│   │   │   ├── Textarea.jsx
│   │   │   └── Loading.jsx
│   │   └── story/        # Composants liés aux histoires
│   │       ├── StoryCreation.jsx
│   │       ├── StoryDisplay.jsx
│   │       ├── SceneCard.jsx
│   │       └── ActionInput.jsx
│   ├── services/          # Services et API
│   │   └── api.js        # Client API
│   └── store/            # Gestion d'état
│       └── storyStore.js # Store Zustand
```

## 🎨 Fonctionnalités

### 1. Création d'histoire
- Sélection du genre (Fantasy, Sci-Fi, Horreur, Mystère, Aventure, Romance)
- Prompt initial optionnel
- Interface intuitive avec icônes et descriptions

### 2. Affichage de l'histoire
- Affichage chronologique des scènes
- Images générées par IA pour chaque scène
- Historique complet de l'aventure
- Scroll automatique vers la dernière scène

### 3. Actions utilisateur
- Actions suggérées par l'IA cliquables
- Possibilité d'écrire une action personnalisée
- Feedback visuel pendant la génération

### 4. UX/UI moderne
- Design "chatbot" épuré et moderne
- Animations fluides
- Mode glassmorphism
- Responsive design
- Loading states élégants
- Gestion d'erreurs claire

## 🏗️ Architecture et principes

### Principe de responsabilité unique (SRP)

Chaque composant a une responsabilité unique :

- **Button, Card, Input, Textarea, Loading** : Composants UI de base réutilisables
- **StoryCreation** : Gestion de la création d'histoire
- **StoryDisplay** : Affichage de l'histoire en cours
- **SceneCard** : Affichage d'une scène individuelle
- **ActionInput** : Saisie et envoi des actions utilisateur

### Séparation des concerns

- **Components** : Logique UI et rendu
- **Services** : Communication avec l'API
- **Store** : Gestion d'état global
- **Styles** : CSS modulaire avec Tailwind

### Gestion d'état

Utilisation de Zustand pour un store global simple :
- État de l'histoire courante
- États de chargement
- Gestion d'erreurs
- Actions asynchrones

## 🎯 Scripts disponibles

- `npm run dev` : Lance le serveur de développement
- `npm run build` : Génère le build de production
- `npm run preview` : Prévisualise le build de production
- `npm run lint` : Vérifie le code avec ESLint

## 🐛 Dépannage

### Le backend ne répond pas

Vérifiez que le backend FastAPI est démarré sur le port 8000 :
```bash
cd backend
python main.py
```

### Erreurs de CORS

Le backend est configuré pour accepter les requêtes du frontend. Si vous rencontrez des erreurs CORS, vérifiez la configuration dans `backend/app/config.py`.

### Les images ne s'affichent pas

1. Vérifiez que le service d'images est actif
2. Consultez les logs du backend
3. Vérifiez que les modèles IA sont correctement chargés

## 📝 Notes de développement

- L'application utilise le **App Router** de Vite (pas Next.js contrairement au README précédent)
- Les composants sont en **JSX** (React classique)
- Le proxy Vite redirige `/api` vers `http://localhost:8000`
- Les images sont servies via l'endpoint `/api/v1/images/{story_id}/{filename}`

## 🚀 Déploiement

Pour déployer en production :

1. Configurez la variable `VITE_API_URL` avec l'URL de production
2. Générez le build : `npm run build`
3. Déployez le dossier `dist/` sur votre serveur
4. Configurez un serveur web (Nginx, Apache) pour servir les fichiers statiques

## 📄 Licence

ISC
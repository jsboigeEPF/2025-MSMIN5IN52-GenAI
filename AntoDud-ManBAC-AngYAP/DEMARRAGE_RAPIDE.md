# 🎯 DÉMARRAGE RAPIDE

## ⚡ Installation en 3 étapes

### 1️⃣ Installer les dépendances

```bash
cd frontend
npm install
```

Cette commande va installer automatiquement toutes les dépendances nécessaires :
- React, ReactDOM
- Vite
- Tailwind CSS
- Zustand
- Axios
- Lucide React (icônes)
- React Markdown
- Et toutes les devDependencies

**Durée estimée** : 2-3 minutes selon votre connexion

### 2️⃣ Lancer l'application

```bash
npm run dev
```

Le serveur de développement démarre sur **http://localhost:3000**

**C'est tout !** Votre navigateur devrait s'ouvrir automatiquement.

### 3️⃣ Tester l'interface

Sans backend actif, vous verrez :
- ✅ La page de sélection du genre (Fantasy, Sci-Fi, Horreur, etc.)
- ✅ Le formulaire de création avec prompt initial
- ✅ Le design moderne avec dégradés et glassmorphism
- ❌ Une erreur au clic sur "Commencer l'aventure" (normal, le backend n'est pas là)

## 🎨 Ce que vous pouvez voir sans backend

### Page de sélection du genre

Un bel écran avec 6 cartes représentant chaque genre :
- 🧙 Fantasy (violet/rose)
- 🚀 Science-Fiction (bleu/cyan)
- 👻 Horreur (rouge/orange)
- 🔍 Mystère (indigo/purple)
- 🧭 Aventure (vert/émeraude)
- ❤️ Romance (rose/pink)

Chaque carte a :
- Une icône animée
- Un titre
- Une description
- Un effet hover avec animation

### Formulaire de contexte initial

Après avoir cliqué sur un genre, vous verrez :
- L'icône et le nom du genre sélectionné
- Un textarea pour le contexte initial (optionnel)
- Des boutons "Retour" et "Commencer l'aventure"
- Design glassmorphism élégant

### Design général

- **Fond** : Dégradé dark (slate-900 → purple-900 → slate-900)
- **Effets** : Glassmorphism (verre dépoli)
- **Animations** : Fade-in, slide-up, hover effects
- **Responsive** : S'adapte à tous les écrans

## 🔧 Avec le backend (quand disponible)

### 1. Démarrer le backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Le backend sera sur **http://localhost:8000**

### 2. Tester le flux complet

1. **Créer une histoire** : Sélectionnez un genre et cliquez sur "Commencer"
2. **Attendre la génération** : ~30s à 2min selon votre machine
3. **Voir la première scène** : Texte narratif + image générée
4. **Choisir une action** : Cliquez sur une suggestion ou écrivez la vôtre
5. **Continuer l'histoire** : L'IA génère la suite avec une nouvelle image

## 📊 Structure de l'application

```
Accueil (StoryCreation)
    ↓
Sélection du genre
    ↓
Contexte initial (optionnel)
    ↓
[API Call] Création de l'histoire
    ↓
Histoire (StoryDisplay)
    ↓
Affichage des scènes (SceneCard)
    ↓
Input d'action (ActionInput)
    ↓
[API Call] Continuation
    ↓
Nouvelle scène ajoutée
    ↓
(répétition)
```

## 🎮 Fonctionnalités testables

### Sans backend
- ✅ Navigation dans l'interface
- ✅ Sélection du genre
- ✅ Saisie du contexte initial
- ✅ Responsive design
- ✅ Animations et transitions
- ❌ Génération d'histoire (nécessite backend)

### Avec backend
- ✅ Tout ce qui précède
- ✅ Création d'histoires
- ✅ Génération de texte IA
- ✅ Génération d'images IA
- ✅ Continuation interactive
- ✅ Affichage des images
- ✅ Historique des scènes

## 🐛 Erreurs possibles et solutions

### `npm install` échoue

```bash
# Nettoyer et réessayer
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Port 3000 déjà utilisé

```bash
# Tuer le processus
lsof -ti:3000 | xargs kill -9

# Ou changer le port dans vite.config.js
server: {
  port: 3001,  // Changez le port ici
  ...
}
```

### Le backend ne répond pas

Vérifiez que :
1. Le backend est démarré (`python main.py`)
2. Il tourne sur le port 8000
3. Le fichier `.env` pointe vers `http://localhost:8000/api/v1`

### Les images ne chargent pas

C'est normal si :
1. Le backend n'est pas démarré
2. Les modèles IA ne sont pas chargés
3. La première génération est en cours

## 💻 Commandes utiles

```bash
# Installer les dépendances
npm install

# Lancer en développement
npm run dev

# Build de production
npm run build

# Prévisualiser le build
npm run preview

# Linter le code
npm run lint

# Nettoyer node_modules
rm -rf node_modules package-lock.json
```

## 📝 Configuration personnalisée

### Changer l'URL de l'API

Modifiez `.env` :
```bash
VITE_API_URL=http://votre-serveur:8000/api/v1
```

### Changer le port du frontend

Modifiez `vite.config.js` :
```javascript
server: {
  port: 3001,  // Votre port
  ...
}
```

### Personnaliser les couleurs

Modifiez `tailwind.config.js` :
```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Vos couleurs
      }
    }
  }
}
```

## 🎯 Prochaines étapes suggérées

1. **Testez l'interface** sans backend pour valider le design
2. **Vérifiez le responsive** sur différents écrans
3. **Préparez une machine puissante** pour le backend
4. **Testez le flux complet** avec le backend
5. **Personnalisez** les styles selon vos goûts

## 📚 Fichiers de documentation

- `README_PROJET.md` : Vue d'ensemble complète
- `frontend/README.md` : Documentation technique du frontend
- `INSTALLATION.md` : Guide d'installation détaillé
- `CORRECTIONS.md` : Résumé des corrections apportées
- `DEMARRAGE_RAPIDE.md` : Ce fichier (guide rapide)

---

**Vous êtes prêt ! Lancez `npm install` puis `npm run dev` pour commencer ! 🚀**

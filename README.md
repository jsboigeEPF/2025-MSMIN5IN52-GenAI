# 🎵 Compositeur de Bandes Sonores d'Ambiance

## Description

Application de génération musicale utilisant l'intelligence artificielle pour créer des boucles musicales instrumentales adaptées à des ambiances spécifiques. Le projet utilise **MusicGen** (Meta) pour la génération musicale locale et **Pollinations.ai** pour la génération d'images d'illustration.

## Membres du Groupe

- Lucas
- Ivan

## Architecture du Projet

```
Groupe-compositeur-Lucas-Ivan/
├── backend/
│   ├── app.py                    # Serveur Flask (API Python)
│   ├── server.js                 # Serveur Node.js (API REST)
│   ├── requirements.txt          # Dépendances Python
│   ├── package.json              # Dépendances Node.js
│   ├── controllers/              # Contrôleurs API
│   ├── routes/                   # Routes Express
│   └── services/                 # Services de génération (MusicGen, Images)
└── frontend/
    ├── src/                      # Code source React
    ├── package.json              # Dépendances frontend
    └── vite.config.js            # Configuration Vite
```

## Technologies Utilisées

### Backend
- **Python 3.8+** : API Flask pour la génération musicale
- **Node.js 16+** : API REST intermédiaire
- **Flask & Flask-CORS** : Serveur API Python
- **Express.js** : Serveur API Node.js
- **MusicGen (Meta)** : Modèle de génération musicale local
- **Transformers (HuggingFace)** : Chargement du modèle
- **PyTorch** : Framework de deep learning
- **Pollinations.ai** : Génération d'images (API gratuite)

### Frontend
- **React 18** : Interface utilisateur
- **Vite** : Build tool moderne
- **CSS moderne** : Styling avec variables CSS

## Prérequis

### Système
- **Python 3.8 ou supérieur**
- **Node.js 16 ou supérieur**
- **npm ou yarn**
- **8 Go de RAM minimum** (16 Go recommandés)
- **~5 Go d'espace disque** (pour le modèle MusicGen)

### GPU (Optionnel mais recommandé)
- CUDA compatible si disponible (accélère la génération de 10x)
- Sinon, le CPU fonctionnera (génération plus lente : 60-100 secondes)

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/ivanoffffff/2025-MSMIN5IN52-GenAI
cd Groupe-compositeur-Lucas-Ivan
```

### 2. Installation du Backend Python

```bash
cd backend
pip install -r requirements.txt
```

**Note** : Le premier lancement téléchargera automatiquement le modèle MusicGen (~2 Go).

### 3. Installation du Backend Node.js

```bash
# Depuis le dossier backend
npm install
```

### 4. Installation du Frontend

```bash
cd ../frontend
npm install
```

## Configuration

### Variables d'environnement (Optionnel)

Créer un fichier `.env` dans le dossier `backend/` :

```env
PORT=3001
SUNO_API_KEY=votre_cle_api_suno  # Optionnel, pour utilisation future
```

**Note** : Actuellement, le projet utilise MusicGen en local, donc aucune clé API n'est nécessaire.

## Lancement du Projet

Le projet nécessite **3 serveurs** qui doivent tourner simultanément.

### Terminal 1 : Backend Python (Flask)

```bash
cd backend
python app.py
```

Le serveur Flask démarre sur **http://localhost:5001**

### Terminal 2 : Backend Node.js (Express)

```bash
cd backend
npm run dev
# ou
node server.js
```

Le serveur Node.js démarre sur **http://localhost:3001**

### Terminal 3 : Frontend React

```bash
cd frontend
npm run dev
```

L'interface démarre sur **http://localhost:5173**

### Ordre de démarrage recommandé

1. ✅ **D'abord** : Backend Python (Flask) - Port 5001
2. ✅ **Ensuite** : Backend Node.js (Express) - Port 3001  
3. ✅ **Enfin** : Frontend (React) - Port 5173

## Utilisation

1. **Ouvrez votre navigateur** à l'adresse `http://localhost:5173`

2. **Choisissez une ambiance prédéfinie** :
   - Forêt Mystérieuse
   - Cyberpunk sous la Pluie
   - Plage au Coucher du Soleil
   - Méditation Zen
   - Café Jazz
   - Montagne Majestueuse
   - Désert Nocturne
   - Ville Futuriste

3. **OU créez une composition personnalisée** :
   - Cliquez sur "Création Personnalisée"
   - Décrivez l'ambiance souhaitée
   - Ajoutez un nom et un style (optionnel)
   - Cliquez sur "Générer la musique"

4. **Patientez** pendant la génération (60-100 secondes sur CPU)

5. **Écoutez et téléchargez** votre création :
   - Lecture audio avec contrôles
   - Image d'illustration générée
   - Bouton de téléchargement au format WAV
   - Mode boucle pour lecture continue

## Fonctionnalités

### ✅ Génération Musicale
- Génération locale avec MusicGen (Meta)
- 8 ambiances prédéfinies
- Mode personnalisé avec description libre
- Audio haute qualité (WAV, 32 kHz)
- Durée : ~20-30 secondes par génération

### ✅ Interface Utilisateur
- Design moderne dark mode
- Lecteur audio intégré avec contrôles
- Barre de progression temps réel
- Contrôle du volume
- Mode boucle automatique
- Téléchargement des créations

### ✅ Génération d'Images
- Image d'illustration pour chaque ambiance
- API Pollinations.ai (gratuite, sans clé)
- Affichage dans le lecteur audio

## Temps de Génération

| Matériel | Temps moyen |
|----------|-------------|
| CPU (Intel i7/AMD Ryzen 7) | 60-100 secondes |
| GPU (NVIDIA RTX 2060+) | 5-15 secondes |
| GPU (NVIDIA RTX 4090) | 2-5 secondes |

## Structure des Fichiers Générés

```
backend/
├── generated_music/
│   └── music_[uuid].wav      # Fichiers audio générés
└── generated_images/
    └── image_[uuid].jpg      # Images générées
```

## Dépannage

### Problème : "Erreur de connexion"
**Solution** : Vérifiez que les 3 serveurs sont bien lancés

### Problème : "Module not found"
**Solution** : 
```bash
cd backend && pip install -r requirements.txt
cd backend && npm install
cd frontend && npm install
```

### Problème : Génération très lente
**Solution** : 
- Normal sur CPU (60-100s)
- Utilisez un GPU CUDA si disponible
- Fermez les applications gourmandes en ressources

### Problème : Le modèle ne se charge pas
**Solution** :
- Vérifiez votre connexion internet (premier téléchargement)
- Libérez de l'espace disque (~5 Go nécessaires)
- Vérifiez les logs dans le terminal Python

### Problème : CORS errors
**Solution** : Vérifiez que Flask-CORS est installé
```bash
pip install flask-cors
```

## API Endpoints

### Backend Node.js (Port 3001)

- `GET /api/music/ambiances` - Liste des ambiances disponibles
- `POST /api/music/generate` - Générer une musique
- `GET /api/music/status/:generationId` - Statut d'une génération

### Backend Python (Port 5001)

- `POST /api/generate` - Générer musique + image
- `GET /api/audio/:generation_id` - Récupérer le fichier audio
- `GET /api/image/:generation_id` - Récupérer l'image

## Développement

### Lancer en mode développement

```bash
# Backend Node.js avec auto-reload
cd backend && npm run dev

# Frontend avec hot-reload
cd frontend && npm run dev
```

### Build de production

```bash
cd frontend
npm run build
```

Les fichiers de production seront dans `frontend/dist/`

## Améliorations Futures

- [ ] Personnalisation fine (tempo, instruments, intensité)
- [ ] Sauvegarde des compositions favorites
- [ ] Export en différents formats (MP3, OGG)
- [ ] Génération de playlists d'ambiances
- [ ] Mode collaboratif
- [ ] Intégration avec Spotify/YouTube
- [ ] Support de durées personnalisées
- [ ] Amélioration de la qualité audio avec upsampling

## Ressources

- [Documentation MusicGen](https://huggingface.co/facebook/musicgen-small)
- [Documentation Flask](https://flask.palletsprojects.com/)
- [Documentation React](https://react.dev/)
- [Documentation Vite](https://vitejs.dev/)

## Licence

MIT

## Crédits

Projet réalisé dans le cadre du module **2025-MSMIN5IN52-GenAI** - EPF 2025

**Technologies IA :**
- MusicGen par Meta AI
- Pollinations.ai pour la génération d'images

---

*Pour toute question ou problème, consultez les issues GitHub ou contactez l'équipe.*
# 🏗️ Architecture du projet

## 📐 Vue d'ensemble

Ce projet suit une architecture moderne en deux parties :
- **Backend** : API FastAPI avec services IA
- **Frontend** : Application React avec Vite

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                     │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Components  │  │   Services   │  │    Store     │ │
│  │     (UI)     │──│     (API)    │──│  (Zustand)   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                  │                  │         │
└─────────│──────────────────│──────────────────│─────────┘
          │                  │                  │
          │                  ▼                  │
          │            HTTP/REST API            │
          │                  │                  │
┌─────────│──────────────────│──────────────────│─────────┐
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Routers    │  │   Services   │  │    Models    │ │
│  │  (FastAPI)   │──│    (IA)      │──│  (Pydantic)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│                   BACKEND (FastAPI)                      │
└─────────────────────────────────────────────────────────┘
```

## 🎨 Frontend - Architecture en couches

### Couche 1 : Composants UI (Présentation)

**Responsabilité** : Affichage et interaction utilisateur

```
components/ui/
├── Button.jsx       → Boutons réutilisables avec variants
├── Card.jsx         → Conteneurs avec glassmorphism
├── Input.jsx        → Champs de saisie simple ligne
├── Textarea.jsx     → Zones de texte multiligne
└── Loading.jsx      → Indicateurs de chargement
```

**Principe** : Composants purement présentationels, pas de logique métier

### Couche 2 : Composants Métier (Logique)

**Responsabilité** : Orchestration et logique spécifique

```
components/story/
├── StoryCreation.jsx    → Interface de création
│   ├── Gestion de l'état local (genre, prompt)
│   ├── Appel au store pour créer l'histoire
│   └── Validation et feedback utilisateur
│
├── StoryDisplay.jsx     → Affichage de l'histoire
│   ├── Orchestration de l'affichage
│   ├── Gestion du scroll automatique
│   └── Coordination entre scènes et actions
│
├── SceneCard.jsx        → Affichage d'une scène
│   ├── Rendu du texte narratif
│   ├── Gestion du chargement d'image
│   └── Modal plein écran pour images
│
└── ActionInput.jsx      → Saisie des actions
    ├── Gestion des suggestions vs custom
    ├── Validation de l'input
    └── Soumission au store
```

### Couche 3 : Services (Communication)

**Responsabilité** : Communication avec l'API backend

```
services/api.js
├── apiClient              → Instance Axios configurée
├── storyService           → Opérations sur les histoires
│   ├── createStory()      → POST /stories/
│   ├── continueStory()    → POST /stories/{id}/continue
│   ├── getStory()         → GET /stories/{id}
│   └── getStoryScenes()   → GET /stories/{id}/scenes
│
├── imageService           → Gestion des images
│   ├── getImageUrl()      → Construit l'URL complète
│   └── getStatus()        → GET /images/status
│
└── healthService          → Health checks
    └── checkHealth()      → GET /health
```

**Principe** : Centralisation de toute la logique API

### Couche 4 : State Management (État global)

**Responsabilité** : Gestion de l'état partagé de l'application

```
store/storyStore.js (Zustand)
│
├── État
│   ├── currentStory       → Histoire complète
│   ├── currentScene       → Scène actuelle
│   ├── allScenes         → Tableau de toutes les scènes
│   ├── storyId           → ID de l'histoire courante
│   ├── isLoading         → État de chargement général
│   ├── isCreating        → Création en cours
│   ├── isContinuing      → Continuation en cours
│   ├── error             → Erreur courante
│   ├── selectedGenre     → Genre sélectionné
│   └── initialPrompt     → Prompt initial
│
└── Actions
    ├── createStory()       → Crée une nouvelle histoire
    ├── continueStory()     → Continue l'histoire
    ├── loadStory()         → Charge une histoire existante
    ├── resetStory()        → Réinitialise l'état
    ├── setSelectedGenre()  → Définit le genre
    ├── setInitialPrompt()  → Définit le prompt
    └── clearError()        → Efface l'erreur
```

**Principe** : Single source of truth pour l'état global

## 🔧 Backend - Architecture en services

### Couche 1 : Routeurs (API)

**Responsabilité** : Endpoints REST et validation

```
app/routers/
├── health.py        → Health check endpoint
│   └── GET /health
│
├── story.py         → Endpoints histoires
│   ├── POST /stories/                → Créer
│   ├── POST /stories/{id}/continue   → Continuer
│   ├── GET /stories/{id}             → Récupérer
│   └── GET /stories/{id}/scenes      → Récupérer scènes
│
└── image.py         → Endpoints images
    ├── GET /images/{story_id}/{filename}  → Servir image
    └── GET /images/status                 → Statut service
```

### Couche 2 : Services (Logique métier)

**Responsabilité** : Orchestration et logique d'application

```
app/services/
│
├── story_service.py
│   ├── create_story()           → Création d'histoire
│   │   ├── Génération ID unique
│   │   ├── Initialisation mémoire
│   │   ├── Appel text_service pour intro
│   │   ├── Appel image_service pour image
│   │   └── Sauvegarde persistante
│   │
│   ├── continue_story()         → Continuation
│   │   ├── Chargement histoire
│   │   ├── Validation état
│   │   ├── Génération nouvelle scène
│   │   ├── Mise à jour mémoire
│   │   └── Sauvegarde
│   │
│   └── _update_memory()         → Mise à jour mémoire
│       └── Résumé récursif des événements
│
├── text_generation_service.py
│   ├── initialize_model()       → Chargement LLM
│   ├── generate_intro_scene()   → Intro avec IA
│   ├── generate_continuation()  → Suite avec IA
│   ├── _build_prompt()          → Construction prompt
│   └── _generate_text()         → Génération texte
│
└── image_generation_service.py
    ├── initialize_model()       → Chargement Stable Diffusion
    ├── generate_scene_image()   → Image pour une scène
    ├── _build_image_prompt()    → Prompt visuel
    ├── _generate_image()        → Génération image
    └── _save_image()            → Sauvegarde sur disque
```

### Couche 3 : Modèles (Données)

**Responsabilité** : Structure et validation des données

```
app/models/schemas.py
│
├── Enums
│   ├── StoryGenre    → fantasy, sci-fi, horror, etc.
│   └── StoryState    → created, in_progress, completed, etc.
│
├── Entités métier
│   ├── Character     → Personnages
│   ├── Location      → Lieux
│   ├── UserAction    → Actions utilisateur
│   └── Scene         → Scènes narratives
│
├── Agrégats
│   ├── StoryMemory   → Mémoire contextuelle
│   └── Story         → Histoire complète
│
└── DTO (API)
    ├── StoryCreateRequest     → Requête création
    ├── StoryContinueRequest   → Requête continuation
    └── StoryResponse          → Réponse standard
```

## 🔄 Flux de données

### Création d'histoire

```
1. User clicks "Commencer l'aventure"
   ↓
2. StoryCreation.jsx → store.createStory(genre, prompt)
   ↓
3. Store → storyService.createStory({ genre, initial_prompt })
   ↓
4. API → POST /api/v1/stories/
   ↓
5. story.router → story_service.create_story(request)
   ↓
6. StoryService
   ├── Génère ID unique
   ├── Initialise mémoire vide
   ├── Appelle text_service.generate_intro_scene()
   │   └── LLM génère texte narratif + actions
   ├── Appelle image_service.generate_scene_image()
   │   └── Stable Diffusion génère image
   └── Sauvegarde sur disque
   ↓
7. Réponse → { story_id, current_scene, suggested_actions }
   ↓
8. Store met à jour l'état
   ↓
9. StoryDisplay.jsx affiche la première scène
```

### Continuation d'histoire

```
1. User clicks action ou écrit custom action
   ↓
2. ActionInput.jsx → store.continueStory(action)
   ↓
3. Store → storyService.continueStory(storyId, { user_action })
   ↓
4. API → POST /api/v1/stories/{id}/continue
   ↓
5. story.router → story_service.continue_story(id, request)
   ↓
6. StoryService
   ├── Charge histoire depuis disque
   ├── Valide que l'histoire peut continuer
   ├── Crée UserAction
   ├── Appelle text_service.generate_continuation()
   │   ├── Construit prompt avec contexte
   │   └── LLM génère suite narrative
   ├── Appelle image_service.generate_scene_image()
   │   └── Stable Diffusion génère image
   ├── Met à jour mémoire (résumé récursif)
   └── Sauvegarde
   ↓
7. Réponse → { story_id, current_scene, suggested_actions }
   ↓
8. Store ajoute la scène à allScenes[]
   ↓
9. SceneCard.jsx affiche la nouvelle scène
   ↓
10. Auto-scroll vers la nouvelle scène
```

## 🎯 Principes d'architecture appliqués

### 1. Single Responsibility Principle (SRP)

Chaque module/composant a **UNE seule raison de changer** :

- `Button.jsx` : Change si le design des boutons change
- `storyService` : Change si l'API backend change
- `text_generation_service` : Change si le modèle de texte change

### 2. Separation of Concerns

Les responsabilités sont clairement séparées :

- **UI** : Affichage uniquement (components/)
- **Logique** : Business logic (services/, store/)
- **Données** : Structure et validation (models/)

### 3. Dependency Injection

Les dépendances sont injectées, pas instanciées :

```python
# Backend - FastAPI
def get_story_service() -> StoryService:
    return StoryService()

@router.post("/")
async def create_story(
    request: StoryCreateRequest,
    story_service: StoryService = Depends(get_story_service)
):
    ...
```

```javascript
// Frontend - React props
<ActionInput
  suggestedActions={actions}
  onSubmitAction={handleAction}
  isLoading={isContinuing}
/>
```

### 4. Singleton Pattern

Les services IA utilisent le pattern Singleton :

```python
class TextGenerationService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Avantage** : Le modèle IA coûteux n'est chargé qu'une seule fois

### 5. Repository Pattern

Le StoryService agit comme un repository :

```python
class StoryService:
    def _save_story(story)      # Sauvegarde
    def _load_story(story_id)   # Chargement
    def create_story(...)       # Création
    def continue_story(...)     # Mise à jour
```

### 6. Observer Pattern (implicite avec Zustand)

Les composants React "observent" le store :

```javascript
// Tout composant qui utilise useStoryStore
// est automatiquement re-rendu quand l'état change
const { allScenes, currentScene } = useStoryStore();
```

## 📦 Gestion des dépendances

### Frontend

```
React Ecosystem
├── react              → UI library
├── react-dom          → DOM renderer
└── react-markdown     → Markdown rendering

Build Tools
├── vite               → Build tool
├── @vitejs/plugin-react → React plugin

Styling
├── tailwindcss        → Utility CSS
├── autoprefixer       → CSS vendor prefixes
├── postcss            → CSS processing
└── clsx               → Classname utility

State & Data
├── zustand            → State management
├── axios              → HTTP client

Icons & UI
└── lucide-react       → Icon library
```

### Backend

```
Web Framework
└── fastapi            → Modern API framework

AI/ML
├── torch              → Deep learning
├── transformers       → LLM (HuggingFace)
└── diffusers          → Image generation

Data
├── pydantic           → Data validation
└── python-dateutil    → Date handling

Server
└── uvicorn            → ASGI server
```

## 🔐 Gestion des erreurs

### Frontend

**Niveaux d'erreurs** :
1. **Service level** : Try/catch dans api.js
2. **Store level** : Gestion d'état d'erreur
3. **Component level** : Affichage utilisateur

```javascript
// Service
try {
  const response = await apiClient.post('/stories/', data);
  return response.data;
} catch (error) {
  throw this.handleError(error, 'Message user-friendly');
}

// Store
try {
  const response = await storyService.createStory(...);
  set({ ...success state... });
} catch (error) {
  set({ error: error.message });
}

// Component
{error && (
  <div className="error-banner">
    {error}
  </div>
)}
```

### Backend

**Niveaux d'erreurs** :
1. **Service level** : Try/except avec logging
2. **Router level** : HTTPException avec codes
3. **Middleware level** : Gestion globale

```python
# Service
try:
    result = await some_operation()
    return result
except Exception as e:
    logger.error(f"Error: {str(e)}")
    return None  # ou raise

# Router
try:
    story = await story_service.create_story(request)
    return StoryResponse(...)
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Error: {str(e)}"
    )
```

---
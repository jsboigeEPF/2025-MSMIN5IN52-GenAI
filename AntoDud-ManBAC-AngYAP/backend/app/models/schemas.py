"""
Modèles de données pour le générateur d'histoires interactives

Ce fichier contient tous les modèles Pydantic qui définissent la structure
des données utilisées dans l'application. Ces modèles servent à :
- Valider les données d'entrée et de sortie de l'API
- Définir la structure des objets métier
- Assurer la cohérence des types de données
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class StoryGenre(str, Enum):
    """
    Énumération des genres d'histoires disponibles
    Chaque genre aura ses propres prompts et styles visuels
    """
    FANTASY = "fantasy"
    SCIENCE_FICTION = "sci-fi"
    HORROR = "horror"
    MYSTERY = "mystery"
    ADVENTURE = "adventure"
    ROMANCE = "romance"


class StoryState(str, Enum):
    """
    États possibles d'une histoire
    Permet de tracker le cycle de vie d'une histoire
    """
    CREATED = "created"          # Histoire créée mais pas encore commencée
    IN_PROGRESS = "in_progress"  # Histoire en cours
    PAUSED = "paused"           # Histoire mise en pause
    COMPLETED = "completed"      # Histoire terminée
    ARCHIVED = "archived"        # Histoire archivée


class Character(BaseModel):
    """
    Modèle représentant un personnage dans l'histoire
    Permet de maintenir la cohérence des personnages
    """
    name: str = Field(..., description="Nom du personnage")
    description: str = Field(..., description="Description physique et personnalité")
    role: str = Field(..., description="Rôle dans l'histoire (protagoniste, antagoniste, etc.)")
    traits: List[str] = Field(default=[], description="Traits de personnalité importants")
    relationships: Dict[str, str] = Field(default={}, description="Relations avec d'autres personnages")
    first_appearance_scene: int = Field(..., description="Numéro de la scène de première apparition")


class Location(BaseModel):
    """
    Modèle représentant un lieu dans l'histoire
    Permet de maintenir la cohérence géographique
    """
    name: str = Field(..., description="Nom du lieu")
    description: str = Field(..., description="Description détaillée du lieu")
    atmosphere: str = Field(..., description="Ambiance générale du lieu")
    key_features: List[str] = Field(default=[], description="Éléments caractéristiques du lieu")
    first_visit_scene: int = Field(..., description="Numéro de la scène de première visite")


class UserAction(BaseModel):
    """
    Modèle représentant une action effectuée par l'utilisateur
    Permet de tracker l'historique des choix du joueur
    """
    action_text: str = Field(..., description="Texte de l'action du joueur")
    timestamp: datetime = Field(default_factory=datetime.now, description="Moment de l'action")
    scene_number: int = Field(..., description="Numéro de la scène où l'action a eu lieu")
    impact_level: str = Field(default="medium", description="Impact estimé sur l'histoire (low/medium/high)")


class Scene(BaseModel):
    """
    Modèle représentant une scène dans l'histoire
    Chaque scène correspond à un échange narrateur/joueur
    """
    scene_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Identifiant unique de la scène")
    scene_number: int = Field(..., description="Numéro séquentiel de la scène")
    story_id: str = Field(..., description="ID de l'histoire parent")
    
    # Contenu narratif
    narrative_text: str = Field(..., description="Texte narratif généré par l'IA")
    user_action: Optional[UserAction] = Field(None, description="Action du joueur pour cette scène")
    
    # Contenu visuel
    image_prompt: Optional[str] = Field(None, description="Prompt utilisé pour générer l'image")
    image_url: Optional[str] = Field(None, description="URL de l'image générée")
    image_generation_time: Optional[float] = Field(None, description="Temps de génération de l'image en secondes")
    
    # Métadonnées
    timestamp: datetime = Field(default_factory=datetime.now, description="Moment de création de la scène")
    generation_time: Optional[float] = Field(None, description="Temps de génération du texte en secondes")
    
    # Suggestions pour le joueur
    suggested_actions: List[str] = Field(default=[], description="Actions suggérées au joueur")


class StoryMemory(BaseModel):
    """
    Modèle gérant la mémoire contextuelle de l'histoire
    C'est le cerveau qui maintient la cohérence narrative
    """
    story_id: str = Field(..., description="ID de l'histoire")
    
    # Résumé dynamique
    current_summary: str = Field(..., description="Résumé actuel de l'histoire")
    key_events: List[str] = Field(default=[], description="Événements clés chronologiques")
    
    # Entités importantes
    characters: Dict[str, Character] = Field(default={}, description="Dictionnaire des personnages (nom -> Character)")
    locations: Dict[str, Location] = Field(default={}, description="Dictionnaire des lieux (nom -> Location)")
    
    # État du monde narratif
    world_state: Dict[str, Any] = Field(default={}, description="Variables d'état du monde (quêtes, objets, etc.)")
    plot_threads: List[str] = Field(default=[], description="Fils narratifs en cours")
    
    # Historique des actions
    user_actions_history: List[UserAction] = Field(default=[], description="Historique des actions du joueur")
    
    # Métadonnées de mémoire
    last_updated: datetime = Field(default_factory=datetime.now, description="Dernière mise à jour de la mémoire")
    memory_version: int = Field(default=1, description="Version de la mémoire pour tracking des changements")


class Story(BaseModel):
    """
    Modèle principal représentant une histoire complète
    Point d'entrée principal pour toutes les opérations sur une histoire
    """
    # Identifiants
    story_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Identifiant unique de l'histoire")
    
    # Configuration de base
    genre: StoryGenre = Field(..., description="Genre de l'histoire")
    title: Optional[str] = Field(None, description="Titre de l'histoire (généré automatiquement)")
    initial_prompt: Optional[str] = Field(None, description="Prompt initial fourni par l'utilisateur")
    
    # État et progression
    state: StoryState = Field(default=StoryState.CREATED, description="État actuel de l'histoire")
    current_scene_number: int = Field(default=0, description="Numéro de la scène actuelle")
    total_scenes: int = Field(default=0, description="Nombre total de scènes créées")
    
    # Scènes et mémoire
    scenes: List[Scene] = Field(default=[], description="Liste de toutes les scènes")
    memory: StoryMemory = Field(..., description="Mémoire contextuelle de l'histoire")
    
    # Métadonnées temporelles
    created_at: datetime = Field(default_factory=datetime.now, description="Date de création")
    updated_at: datetime = Field(default_factory=datetime.now, description="Dernière mise à jour")
    last_activity: datetime = Field(default_factory=datetime.now, description="Dernière activité utilisateur")
    
    # Statistiques
    total_generation_time: float = Field(default=0.0, description="Temps total de génération cumulé")
    average_scene_length: Optional[int] = Field(None, description="Longueur moyenne des scènes en caractères")


# ===== MODÈLES POUR L'API (REQUEST/RESPONSE) =====

class StoryCreateRequest(BaseModel):
    """
    Modèle pour la création d'une nouvelle histoire
    Utilisé par l'endpoint POST /stories
    """
    genre: StoryGenre = Field(..., description="Genre de l'histoire à créer")
    initial_prompt: Optional[str] = Field(None, description="Prompt initial optionnel de l'utilisateur")


class StoryContinueRequest(BaseModel):
    """
    Modèle pour continuer une histoire existante
    Utilisé par l'endpoint POST /stories/{id}/continue
    """
    user_action: str = Field(..., description="Action que souhaite effectuer l'utilisateur")


class StoryResponse(BaseModel):
    """
    Modèle de réponse standard pour les opérations sur les histoires
    Contient les informations essentielles à afficher au frontend
    """
    story_id: str = Field(..., description="ID de l'histoire")
    current_scene: Scene = Field(..., description="Scène actuelle")
    suggested_actions: List[str] = Field(..., description="Actions suggérées au joueur")
    story_state: StoryState = Field(..., description="État actuel de l'histoire")
    scene_count: int = Field(..., description="Nombre total de scènes")


class ImageGenerationRequest(BaseModel):
    """
    Modèle pour les demandes de génération d'images
    Utilisé par le service de génération d'images
    """
    prompt: str = Field(..., description="Prompt pour la génération d'image")
    style: Optional[str] = Field("fantasy art", description="Style artistique souhaité")
    story_id: str = Field(..., description="ID de l'histoire associée")
    scene_number: int = Field(..., description="Numéro de la scène associée")


class ImageResponse(BaseModel):
    """
    Modèle de réponse pour la génération d'images
    """
    image_url: str = Field(..., description="URL de l'image générée")
    prompt_used: str = Field(..., description="Prompt effectivement utilisé")
    generation_time: float = Field(..., description="Temps de génération en secondes")
    story_id: str = Field(..., description="ID de l'histoire associée")


class HealthResponse(BaseModel):
    """
    Modèle pour le health check de l'API
    """
    status: str = Field(..., description="Statut de l'API")
    timestamp: datetime = Field(..., description="Timestamp du check")
    version: str = Field(..., description="Version de l'API")
    models_loaded: Dict[str, bool] = Field(default={}, description="État des modèles IA chargés")
"""
Routeur API pour les opérations sur les histoires

Ce module contient tous les endpoints REST pour :
- Créer de nouvelles histoires
- Continuer des histoires existantes  
- Récupérer l'état des histoires
- Gérer le cycle de vie des histoires

Architecture REST :
- POST /stories : Créer une nouvelle histoire
- POST /stories/{id}/continue : Continuer une histoire avec action utilisateur
- GET /stories/{id} : Récupérer une histoire
- GET /stories/{id}/scenes : Récupérer les scènes d'une histoire
"""

from fastapi import APIRouter, HTTPException, Path, Depends
from typing import List

from app.models.schemas import (
    StoryCreateRequest, StoryContinueRequest, StoryResponse, 
    Story, Scene
)
from app.services.story_service import StoryService


# Création du routeur avec préfixe et tags pour la documentation
router = APIRouter(prefix="/stories", tags=["stories"])

# Instance du service (Dependency Injection pattern)
def get_story_service() -> StoryService:
    """
    Factory function pour l'injection de dépendance du StoryService
    Permet de faciliter les tests et la maintenance
    """
    return StoryService()


@router.post("/", response_model=StoryResponse, status_code=201)
async def create_story(
    request: StoryCreateRequest,
    story_service: StoryService = Depends(get_story_service)
) -> StoryResponse:
    """
    Crée une nouvelle histoire interactive
    
    Ce endpoint initialise une nouvelle histoire avec :
    - Le genre spécifié par l'utilisateur
    - Un prompt initial optionnel
    - La première scène d'introduction générée automatiquement
    
    Args:
        request: Données de création (genre, prompt initial optionnel)
        story_service: Service injecté pour la gestion des histoires
        
    Returns:
        StoryResponse: Informations de l'histoire créée avec la première scène
        
    Raises:
        HTTPException 400: Si les données de création sont invalides
        HTTPException 500: Si erreur lors de la création
    """
    try:
        # Appel au service pour créer l'histoire
        story = await story_service.create_story(request)
        
        # Construction de la réponse avec la scène courante
        current_scene = story.scenes[-1] if story.scenes else None
        
        if not current_scene:
            raise HTTPException(
                status_code=500, 
                detail="Erreur lors de la génération de la scène initiale"
            )
        
        return StoryResponse(
            story_id=story.story_id,
            current_scene=current_scene,
            suggested_actions=current_scene.suggested_actions,
            story_state=story.state,
            scene_count=story.total_scenes
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la création de l'histoire: {str(e)}"
        )


@router.post("/{story_id}/continue", response_model=StoryResponse)
async def continue_story(
    story_id: str = Path(..., description="ID unique de l'histoire"),
    request: StoryContinueRequest = ...,
    story_service: StoryService = Depends(get_story_service)
) -> StoryResponse:
    """
    Continue une histoire existante avec l'action du joueur
    
    Ce endpoint :
    1. Récupère l'histoire par son ID
    2. Enregistre l'action du joueur
    3. Génère la réponse narrative
    4. Met à jour la mémoire contextuelle
    5. Sauvegarde les changements
    
    Args:
        story_id: Identifiant unique de l'histoire
        request: Action du joueur à intégrer dans l'histoire
        story_service: Service injecté pour la gestion des histoires
        
    Returns:
        StoryResponse: Histoire mise à jour avec la nouvelle scène
        
    Raises:
        HTTPException 404: Si l'histoire n'existe pas
        HTTPException 400: Si l'histoire ne peut pas continuer
        HTTPException 500: Si erreur lors de la génération
    """
    try:
        # Continuation de l'histoire avec l'action du joueur
        story = await story_service.continue_story(story_id, request)
        
        # Récupération de la dernière scène générée  
        current_scene = story.scenes[-1]
        
        return StoryResponse(
            story_id=story.story_id,
            current_scene=current_scene,
            suggested_actions=current_scene.suggested_actions,
            story_state=story.state,
            scene_count=story.total_scenes
        )
        
    except Exception as e:
        # Gestion spécifique des erreurs "histoire non trouvée"
        if "introuvable" in str(e):
            raise HTTPException(
                status_code=404,
                detail=f"Histoire {story_id} non trouvée"
            )
        # Gestion des erreurs d'état invalide
        elif "ne peut pas continuer" in str(e):
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        # Autres erreurs
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la continuation: {str(e)}"
            )


@router.get("/{story_id}", response_model=Story)
async def get_story(
    story_id: str = Path(..., description="ID unique de l'histoire"),
    story_service: StoryService = Depends(get_story_service)
) -> Story:
    """
    Récupère une histoire complète par son ID
    
    Retourne toutes les informations de l'histoire :
    - Métadonnées (genre, état, timestamps)
    - Toutes les scènes 
    - Mémoire contextuelle complète
    - Historique des actions
    
    Args:
        story_id: Identifiant unique de l'histoire
        story_service: Service injecté pour la gestion des histoires
        
    Returns:
        Story: Histoire complète avec toutes ses données
        
    Raises:
        HTTPException 404: Si l'histoire n'existe pas
    """
    try:
        story = await story_service.get_story(story_id)
        
        if not story:
            raise HTTPException(
                status_code=404,
                detail=f"Histoire {story_id} non trouvée"
            )
        
        return story
        
    except HTTPException:
        # Re-raise des HTTPException pour préserver les codes d'erreur
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )


@router.get("/{story_id}/scenes", response_model=List[Scene])
async def get_story_scenes(
    story_id: str = Path(..., description="ID unique de l'histoire"),
    story_service: StoryService = Depends(get_story_service)
) -> List[Scene]:
    """
    Récupère uniquement les scènes d'une histoire
    
    Endpoint optimisé pour récupérer seulement la progression narrative
    sans toute la mémoire contextuelle (plus léger que GET /stories/{id})
    
    Args:
        story_id: Identifiant unique de l'histoire
        story_service: Service injecté pour la gestion des histoires
        
    Returns:
        List[Scene]: Liste chronologique des scènes
        
    Raises:
        HTTPException 404: Si l'histoire n'existe pas
    """
    try:
        story = await story_service.get_story(story_id)
        
        if not story:
            raise HTTPException(
                status_code=404,
                detail=f"Histoire {story_id} non trouvée"
            )
        
        return story.scenes
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des scènes: {str(e)}"
        )
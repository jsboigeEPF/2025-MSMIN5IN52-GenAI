"""
Routeur API pour les opérations sur les images

Ce module contient tous les endpoints REST pour :
- Servir les images générées
- Générer des images personnalisées
- Récupérer les images d'une histoire
"""

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import FileResponse
from typing import List
import os

from app.config import settings
from app.services.image_generation_service import ImageGenerationService


router = APIRouter(prefix="/images", tags=["images"])


@router.get("/{story_id}/{filename}")
async def get_image(
    story_id: str = Path(..., description="ID de l'histoire"),
    filename: str = Path(..., description="Nom du fichier image")
):
    """
    Récupère une image générée par son chemin
    
    Args:
        story_id: ID de l'histoire
        filename: Nom du fichier image
        
    Returns:
        FileResponse: L'image demandée
        
    Raises:
        HTTPException 404: Si l'image n'existe pas
    """
    image_path = os.path.join(settings.IMAGES_PATH, story_id, filename)
    
    if not os.path.exists(image_path):
        raise HTTPException(
            status_code=404,
            detail=f"Image non trouvée: {filename}"
        )
    
    return FileResponse(
        image_path,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=31536000"}
    )


@router.get("/status")
async def get_image_service_status():
    """
    Retourne l'état du service de génération d'images
    
    Returns:
        Dict: Informations sur l'état du service
    """
    image_service = ImageGenerationService()
    return image_service.get_model_status()

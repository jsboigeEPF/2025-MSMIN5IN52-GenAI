"""
Routeur pour les endpoints de santé et monitoring

Ce module fournit des endpoints pour :
- Vérifier l'état de l'API
- Monitoring des services
- Informations de version et configuration
"""

from fastapi import APIRouter
from datetime import datetime

from app.models.schemas import HealthResponse
from app.services.text_generation_service import TextGenerationService
from app.services.image_generation_service import ImageGenerationService

# Création du routeur avec tags pour la documentation
router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Endpoint de vérification de santé de l'API
    
    Retourne l'état actuel des services et composants :
    - Statut général de l'API
    - Timestamp de la vérification
    - Version de l'application
    - État réel des modèles IA chargés
    
    Returns:
        HealthResponse: Informations de santé de l'API
    """
    try:
        # Vérification réelle de l'état des services IA
        text_service = TextGenerationService()
        text_status = text_service.get_model_status()
        
        image_service = ImageGenerationService()
        image_status = image_service.get_model_status()
        
        models_status = {
            "text_model": text_status.get("model_loaded", False),
            "image_model": image_status.get("model_loaded", False),
        }
        
        # Déterminer le statut global
        overall_status = "healthy" if any(models_status.values()) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now(),
            version="1.0.0",
            models_loaded=models_status
        )
        
    except Exception as e:
        # En cas d'erreur, retourner un statut dégradé
        return HealthResponse(
            status="error",
            timestamp=datetime.now(),
            version="1.0.0",
            models_loaded={"text_model": False, "image_model": False}
        )
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
    - État des modèles IA (à implémenter)
    
    Returns:
        HealthResponse: Informations de santé de l'API
    """
    # TODO: Ajouter des vérifications réelles des services
    # - Connectivité aux modèles IA
    # - Espace disque disponible
    # - Mémoire utilisée
    # - État des services externes
    
    models_status = {
        "text_model": False,  # À implémenter quand le service IA sera prêt
        "image_model": False,  # À implémenter quand le service IA sera prêt
    }
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        models_loaded=models_status
    )
"""
API endpoints for application events management
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import PaginatedResponse

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_application_events(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    application_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Récupérer la liste des événements de candidature avec pagination
    """
    try:
        # Pour l'instant, retourner une liste vide avec la structure correcte
        return PaginatedResponse(
            items=[],
            total=0,
            page=page,
            limit=limit,
            pages=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@router.get("/{event_id}")
async def get_application_event(event_id: str, db: Session = Depends(get_db)):
    """
    Récupérer un événement de candidature par ID
    """
    raise HTTPException(status_code=404, detail="Événement non trouvé")

@router.post("/")
async def create_application_event(db: Session = Depends(get_db)):
    """
    Créer un nouvel événement de candidature
    """
    raise HTTPException(status_code=501, detail="Non implémenté")

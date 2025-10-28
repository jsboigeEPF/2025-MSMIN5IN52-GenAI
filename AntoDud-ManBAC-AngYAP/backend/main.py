"""
Point d'entrée principal de l'API Interactive Story Generator

Ce fichier configure et lance l'application FastAPI avec :
- Configuration CORS pour le frontend
- Inclusion des routeurs API
- Middleware de logging et gestion d'erreurs
- Documentation automatique Swagger/ReDoc
"""

import os
# Désactiver l'avertissement symlinks sur Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import logging

from app.config import settings
from app.routers import story, health, image
from app.services.text_generation_service import TextGenerationService
from app.services.image_generation_service import ImageGenerationService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire du cycle de vie de l'application
    Remplace les anciens on_event("startup") et on_event("shutdown")
    """
    # === STARTUP ===
    logger = logging.getLogger("uvicorn")
    logger.info("🚀 Démarrage de l'application Interactive Story Generator")
    
    # Initialisation des services IA
    logger.info("📥 Initialisation des services IA...")
    
    try:
        # Service de génération de texte
        logger.info(f"🔤 Chargement du modèle de texte: {settings.TEXT_MODEL_NAME}")
        text_service = TextGenerationService()
        text_success = await text_service.initialize_model()
        
        if text_success:
            logger.info("✅ Service de génération de texte initialisé avec succès")
        else:
            logger.warning("⚠️ Service de génération de texte en mode dégradé")
        
        # Service de génération d'images
        logger.info(f"🖼️ Chargement du modèle d'images: {settings.IMAGE_MODEL_NAME}")
        image_service = ImageGenerationService()
        image_success = await image_service.initialize_model()
        
        if image_success:
            logger.info("✅ Service de génération d'images initialisé avec succès")
        else:
            logger.warning("⚠️ Service de génération d'images en mode dégradé")
        
        logger.info("🎉 Application prête à recevoir des requêtes")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation des services: {str(e)}")
        logger.warning("⚠️ L'application fonctionnera en mode dégradé")
    
    yield  # L'application tourne ici
    
    # === SHUTDOWN ===
    logger.info("🛑 Arrêt de l'application Interactive Story Generator")
    
    # Nettoyage des caches et ressources
    try:
        text_service = TextGenerationService()
        if hasattr(text_service, '_prompt_cache'):
            text_service._prompt_cache.clear()
            
        image_service = ImageGenerationService()
        if hasattr(image_service, 'clear_cache'):
            image_service.clear_cache()
            
        logger.info("🧹 Ressources nettoyées avec succès")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du nettoyage: {str(e)}")
    
    logger.info("👋 Application arrêtée proprement")


# Création de l'application FastAPI avec métadonnées pour la documentation
app = FastAPI(
    title="Interactive Story Generator API",
    description="""
    API pour la génération d'histoires interactives avec images.
    
    Fonctionnalités principales :
    - Création d'histoires dans différents genres
    - Progression narrative basée sur les actions du joueur
    - Génération d'images pour chaque scène
    - Système de mémoire pour la cohérence narrative
    - Sauvegarde et reprise des histoires
    """,
    version="1.0.0",
    docs_url="/docs",  # Documentation Swagger
    redoc_url="/redoc",  # Documentation ReDoc alternative
    lifespan=lifespan  # Nouveau système de gestion du cycle de vie
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration des routeurs API
# Chaque routeur gère un domaine fonctionnel spécifique
app.include_router(health.router, prefix="/api/v1")
app.include_router(story.router, prefix="/api/v1")
app.include_router(image.router, prefix="/api/v1")


@app.get("/")
async def root():
    """
    Endpoint racine pour vérifier que l'API fonctionne
    Accessible à GET /
    """
    return {
        "message": "Interactive Story Generator API is running",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    """
    Point d'entrée pour lancer l'application en développement
    En production, utiliser un serveur ASGI comme uvicorn, gunicorn, etc.
    """
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
"""Point d'entrée de l'application FastAPI."""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api.v1 import midpoint, admin
from app.db.session import DatabaseSession

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gère le cycle de vie de l'application.
    
    Initialise les ressources au démarrage,
    les libère à l'arrêt.
    """
    # Startup
    logger.info("Démarrage de la Gateway de Provisionnement")
    DatabaseSession.init_pool()
    
    yield
    
    # Shutdown
    logger.info("Arrêt de la Gateway")
    DatabaseSession.close_pool()


# Application FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Gateway intelligente de provisionnement IAM",
    lifespan=lifespan
)

# Enregistrement des routes
app.include_router(midpoint.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/")
def root():
    """Endpoint racine."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

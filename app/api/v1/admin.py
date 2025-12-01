"""Endpoints d'administration et monitoring."""

from fastapi import APIRouter
import logging

from app.models.pydantic_schemas import RulesConfigResponse, HealthResponse
from app.core.rules_engine import RulesEngine
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["admin"])

rules_engine = RulesEngine()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """
    Vérifie l'état de santé de l'API.
    
    Retourne le statut et la version.
    """
    return HealthResponse(
        status="ok",
        version=settings.app_version
    )


@router.get("/rules", response_model=RulesConfigResponse)
def get_rules():
    """
    Récupère la configuration actuelle des règles.
    
    Utile pour debug et visualisation.
    """
    return RulesConfigResponse(
        ldap_mappings=rules_engine.config.get("ldap", {}).get("mappings", {}),
        ldap_config=rules_engine.config.get("ldap", {}).get("server", {}),
        global_config=rules_engine.config.get("global", {})
    )


@router.post("/rules/reload")
def reload_rules():
    """
    Recharge les règles depuis le fichier YAML.
    
    Permet de mettre à jour les règles sans redémarrer l'API.
    """
    try:
        rules_engine.reload_config()
        logger.info("Règles rechargées avec succès")
        return {"status": "success", "message": "Règles rechargées"}
    except Exception as e:
        logger.error(f"Erreur rechargement règles: {e}")
        return {"status": "error", "message": str(e)}

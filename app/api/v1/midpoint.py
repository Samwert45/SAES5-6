"""Endpoints pour recevoir les demandes de MidPoint."""

from fastapi import APIRouter, HTTPException
import logging

from app.models.pydantic_schemas import ProvisionRequest, ProvisionResponse
from app.services.provisioning_service import ProvisioningService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/provision", tags=["provisioning"])

# Service de provisioning (singleton)
provisioning_service = ProvisioningService()


@router.post("/create", response_model=ProvisionResponse)
def create_user(request: ProvisionRequest):
    """
    Crée un utilisateur dans les systèmes cibles.
    
    - Calcule les attributs via règles dynamiques
    - Provisionne dans LDAP
    - Enregistre l'action dans les logs
    """
    logger.info(f"Requête création: {request.accountId}")
    response = provisioning_service.create_user(request)
    
    if response.status == "error":
        raise HTTPException(status_code=500, detail=response.message)
    
    return response


@router.put("/update", response_model=ProvisionResponse)
def update_user(request: ProvisionRequest):
    """
    Met à jour un utilisateur dans les systèmes cibles.
    
    - Recalcule les attributs modifiés
    - Met à jour dans LDAP
    - Enregistre l'action
    """
    logger.info(f"Requête modification: {request.accountId}")
    response = provisioning_service.update_user(request)
    
    if response.status == "error":
        raise HTTPException(status_code=500, detail=response.message)
    
    return response


@router.delete("/delete", response_model=ProvisionResponse)
def delete_user(request: ProvisionRequest):
    """
    Supprime un utilisateur des systèmes cibles.
    
    - Supprime de LDAP
    - Enregistre l'action
    """
    logger.info(f"Requête suppression: {request.accountId}")
    response = provisioning_service.delete_user(request)
    
    if response.status == "error":
        raise HTTPException(status_code=500, detail=response.message)
    
    return response

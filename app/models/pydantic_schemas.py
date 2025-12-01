"""Modèles Pydantic pour validation des requêtes/réponses API."""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum


class OperationType(str, Enum):
    """Types d'opérations de provisioning."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class ProvisionRequest(BaseModel):
    """Requête de provisioning depuis MidPoint."""
    
    operation: OperationType = Field(..., description="Type d'opération")
    accountId: str = Field(..., description="Identifiant du compte")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Attributs utilisateur")
    
    class Config:
        json_schema_extra = {
            "example": {
                "operation": "create",
                "accountId": "auto",
                "attributes": {
                    "firstname": "Jean",
                    "lastname": "Dupont",
                    "department": "IT"
                }
            }
        }


class ProvisionResponse(BaseModel):
    """Réponse de provisioning."""
    
    status: str = Field(..., description="Statut de l'opération (success/error)")
    message: Optional[str] = Field(None, description="Message descriptif")
    calculatedAttributes: Optional[Dict[str, Any]] = Field(None, description="Attributs calculés")
    errors: Optional[List[str]] = Field(None, description="Liste des erreurs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Utilisateur créé avec succès",
                "calculatedAttributes": {
                    "login": "jean.dupont",
                    "mail": "jean.dupont@sae.com",
                    "dn": "uid=jean.dupont,dc=SAE,dc=com"
                }
            }
        }


class RulesConfigResponse(BaseModel):
    """Réponse pour la configuration des règles."""
    
    ldap_mappings: Dict[str, str] = Field(default_factory=dict)
    ldap_config: Dict[str, Any] = Field(default_factory=dict)
    global_config: Dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Réponse du health check."""
    
    status: str = Field(..., description="État de l'API")
    version: str = Field(..., description="Version de l'API")

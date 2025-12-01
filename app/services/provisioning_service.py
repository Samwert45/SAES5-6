"""Service de provisioning orchestrant règles et connecteurs."""

from typing import Dict, Any
import logging

from app.core.rules_engine import RulesEngine, RulesEngineError
from app.core.connectors.ldap_connector import LDAPConnector, LDAPConnectorError
from app.logging.audit_logger import AuditLogger
from app.models.pydantic_schemas import ProvisionRequest, ProvisionResponse

logger = logging.getLogger(__name__)


class ProvisioningService:
    """Service central de provisioning."""
    
    def __init__(self):
        """Initialise le service avec le moteur de règles."""
        self.rules_engine = RulesEngine()
    
    def _get_ldap_connector(self) -> LDAPConnector:
        """Crée un connecteur LDAP depuis la config."""
        config = self.rules_engine.get_server_config('ldap')
        return LDAPConnector(config)
    
    def create_user(self, request: ProvisionRequest) -> ProvisionResponse:
        """
        Crée un utilisateur dans LDAP.
        
        Args:
            request: Requête de provisioning
        
        Returns:
            Réponse de provisioning
        """
        try:
            # 1. Calculer les attributs via règles
            calculated = self.rules_engine.apply_rules('ldap', request.attributes)
            
            # 2. Récupérer config et object classes
            object_classes = self.rules_engine.get_object_classes('ldap')
            
            # 3. Préparer attributs LDAP
            ldap_attrs = {
                'cn': calculated.get('cn'),
                'sn': request.attributes.get('lastname'),
                'mail': calculated.get('mail')
            }
            
            # 4. Créer utilisateur via connecteur
            connector = self._get_ldap_connector()
            result = connector.create_user(
                dn=calculated['dn'],
                object_classes=object_classes,
                attributes=ldap_attrs
            )
            
            # 5. Logger l'action
            AuditLogger.log_provision(
                operation='create',
                account_id=calculated.get('login'),
                status='success',
                details=f"DN: {calculated['dn']}"
            )
            
            return ProvisionResponse(
                status='success',
                message=f"Utilisateur {calculated.get('login')} créé",
                calculatedAttributes=calculated
            )
            
        except (RulesEngineError, LDAPConnectorError) as e:
            logger.error(f"Erreur création utilisateur: {e}")
            AuditLogger.log_provision(
                operation='create',
                account_id=request.accountId,
                status='error',
                details=str(e)
            )
            return ProvisionResponse(
                status='error',
                message=str(e),
                errors=[str(e)]
            )
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            return ProvisionResponse(
                status='error',
                message="Erreur interne",
                errors=[str(e)]
            )
    
    def update_user(self, request: ProvisionRequest) -> ProvisionResponse:
        """
        Met à jour un utilisateur dans LDAP.
        
        Args:
            request: Requête de provisioning
        
        Returns:
            Réponse de provisioning
        """
        try:
            # 1. Calculer les attributs
            calculated = self.rules_engine.apply_rules('ldap', request.attributes)
            
            # 2. Préparer les changements
            changes = {}
            if 'cn' in calculated:
                changes['cn'] = calculated['cn']
            if 'mail' in calculated:
                changes['mail'] = calculated['mail']
            if 'lastname' in request.attributes:
                changes['sn'] = request.attributes['lastname']
            
            # 3. Mettre à jour via connecteur
            connector = self._get_ldap_connector()
            dn = calculated.get('dn', f"uid={request.accountId},dc=SAE,dc=com")
            result = connector.update_user(dn=dn, changes=changes)
            
            # 4. Logger
            AuditLogger.log_provision(
                operation='update',
                account_id=request.accountId,
                status='success',
                details=f"Attributs modifiés: {', '.join(changes.keys())}"
            )
            
            return ProvisionResponse(
                status='success',
                message=f"Utilisateur {request.accountId} modifié",
                calculatedAttributes=calculated
            )
            
        except (RulesEngineError, LDAPConnectorError) as e:
            logger.error(f"Erreur modification utilisateur: {e}")
            AuditLogger.log_provision(
                operation='update',
                account_id=request.accountId,
                status='error',
                details=str(e)
            )
            return ProvisionResponse(
                status='error',
                message=str(e),
                errors=[str(e)]
            )
    
    def delete_user(self, request: ProvisionRequest) -> ProvisionResponse:
        """
        Supprime un utilisateur dans LDAP.
        
        Args:
            request: Requête de provisioning
        
        Returns:
            Réponse de provisioning
        """
        try:
            # 1. Calculer le DN
            calculated = self.rules_engine.apply_rules('ldap', request.attributes)
            dn = calculated.get('dn', f"uid={request.accountId},dc=SAE,dc=com")
            
            # 2. Supprimer via connecteur
            connector = self._get_ldap_connector()
            result = connector.delete_user(dn=dn)
            
            # 3. Logger
            AuditLogger.log_provision(
                operation='delete',
                account_id=request.accountId,
                status='success',
                details=f"DN: {dn}"
            )
            
            return ProvisionResponse(
                status='success',
                message=f"Utilisateur {request.accountId} supprimé"
            )
            
        except (RulesEngineError, LDAPConnectorError) as e:
            logger.error(f"Erreur suppression utilisateur: {e}")
            AuditLogger.log_provision(
                operation='delete',
                account_id=request.accountId,
                status='error',
                details=str(e)
            )
            return ProvisionResponse(
                status='error',
                message=str(e),
                errors=[str(e)]
            )

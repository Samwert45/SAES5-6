"""Logger d'audit pour traçabilité."""

from datetime import datetime
from typing import Optional
import logging

from app.db.session import DatabaseSession

logger = logging.getLogger(__name__)


class AuditLogger:
    """Logger pour enregistrer les actions de provisioning."""
    
    @staticmethod
    def log_action(action: str, descriptif: str, user_id: Optional[str] = None) -> bool:
        """
        Enregistre une action dans la base de données.
        
        Args:
            action: Type d'action (CREATE, UPDATE, DELETE)
            descriptif: Description de l'action
            user_id: Identifiant de l'utilisateur concerné
        
        Returns:
            True si succès, False sinon
        """
        try:
            with DatabaseSession.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO logs (action, descriptif, date)
                    VALUES (%s, %s, %s)
                    """,
                    (action, descriptif, datetime.now())
                )
                cursor.close()
                
            logger.info(f"Action loggée: {action} - {descriptif}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du logging: {e}")
            return False
    
    @staticmethod
    def log_provision(operation: str, account_id: str, status: str, details: Optional[str] = None):
        """
        Log spécifique pour le provisioning.
        
        Args:
            operation: Type d'opération (create, update, delete)
            account_id: Identifiant du compte
            status: Statut (success, error)
            details: Détails supplémentaires
        """
        descriptif = f"[{operation.upper()}] User {account_id} - {status}"
        if details:
            descriptif += f" - {details}"
        
        AuditLogger.log_action(operation.upper(), descriptif, account_id)

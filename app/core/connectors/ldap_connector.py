"""Connecteur LDAP pour le provisioning."""

from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LDAPConnectorError(Exception):
    """Exception levée lors d'erreurs du connecteur LDAP."""
    pass


class LDAPConnector:
    """Connecteur pour gérer les opérations LDAP."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialise le connecteur LDAP.
        
        Args:
            config: Configuration LDAP (host, port, admin_dn, admin_password)
        """
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 389)
        self.admin_dn = config.get('admin_dn')
        self.admin_password = config.get('admin_password')
        
        if not self.admin_dn or not self.admin_password:
            raise LDAPConnectorError("admin_dn et admin_password requis")
    
    def _get_connection(self) -> Connection:
        """Crée une connexion LDAP."""
        try:
            server = Server(f"ldap://{self.host}:{self.port}", get_info=ALL)
            conn = Connection(
                server,
                self.admin_dn,
                self.admin_password,
                auto_bind=True
            )
            return conn
        except Exception as e:
            raise LDAPConnectorError(f"Échec de connexion LDAP: {e}")
    
    def create_user(
        self,
        dn: str,
        object_classes: list,
        attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crée un utilisateur dans LDAP.
        
        Args:
            dn: Distinguished Name de l'utilisateur
            object_classes: Classes d'objets LDAP
            attributes: Attributs de l'utilisateur
        
        Returns:
            Résultat de l'opération
        """
        conn = None
        try:
            conn = self._get_connection()
            
            result = conn.add(dn, object_classes, attributes)
            
            if not result:
                raise LDAPConnectorError(
                    f"Échec création LDAP: {conn.result}"
                )
            
            logger.info(f"Utilisateur créé: {dn}")
            return {
                'status': 'success',
                'dn': dn,
                'result': conn.result
            }
            
        except Exception as e:
            logger.error(f"Erreur création LDAP: {e}")
            raise LDAPConnectorError(f"Erreur création: {e}")
        
        finally:
            if conn:
                conn.unbind()
    
    def update_user(self, dn: str, changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Met à jour un utilisateur LDAP.
        
        Args:
            dn: Distinguished Name de l'utilisateur
            changes: Attributs à modifier {attr: nouvelle_valeur}
        
        Returns:
            Résultat de l'opération
        """
        conn = None
        try:
            conn = self._get_connection()
            
            # Convertir en format LDAP
            ldap_changes = {
                attr: [(MODIFY_REPLACE, [value])]
                for attr, value in changes.items()
            }
            
            result = conn.modify(dn, ldap_changes)
            
            if not result:
                raise LDAPConnectorError(
                    f"Échec modification LDAP: {conn.result}"
                )
            
            logger.info(f"Utilisateur modifié: {dn}")
            return {
                'status': 'success',
                'dn': dn,
                'result': conn.result
            }
            
        except Exception as e:
            logger.error(f"Erreur modification LDAP: {e}")
            raise LDAPConnectorError(f"Erreur modification: {e}")
        
        finally:
            if conn:
                conn.unbind()
    
    def delete_user(self, dn: str) -> Dict[str, Any]:
        """
        Supprime un utilisateur LDAP.
        
        Args:
            dn: Distinguished Name de l'utilisateur
        
        Returns:
            Résultat de l'opération
        """
        conn = None
        try:
            conn = self._get_connection()
            
            result = conn.delete(dn)
            
            if not result:
                raise LDAPConnectorError(
                    f"Échec suppression LDAP: {conn.result}"
                )
            
            logger.info(f"Utilisateur supprimé: {dn}")
            return {
                'status': 'success',
                'dn': dn,
                'result': conn.result
            }
            
        except Exception as e:
            logger.error(f"Erreur suppression LDAP: {e}")
            raise LDAPConnectorError(f"Erreur suppression: {e}")
        
        finally:
            if conn:
                conn.unbind()
    
    def search_user(self, search_base: str, search_filter: str) -> Optional[Dict[str, Any]]:
        """
        Recherche un utilisateur LDAP.
        
        Args:
            search_base: Base de recherche
            search_filter: Filtre LDAP
        
        Returns:
            Informations de l'utilisateur ou None
        """
        conn = None
        try:
            conn = self._get_connection()
            
            conn.search(search_base, search_filter)
            
            if conn.entries:
                return {
                    'status': 'success',
                    'entries': [entry.entry_to_json() for entry in conn.entries]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur recherche LDAP: {e}")
            raise LDAPConnectorError(f"Erreur recherche: {e}")
        
        finally:
            if conn:
                conn.unbind()

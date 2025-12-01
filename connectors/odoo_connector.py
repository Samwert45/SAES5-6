import xmlrpc.client
from typing import Dict, Any
from .base import BaseConnector

class OdooConnector(BaseConnector):
    """Connecteur pour Odoo (XML-RPC)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.uid = None
        self.models = None
    
    def _authenticate(self):
        """Authentification Odoo"""
        if self.uid:
            return self.uid
        
        common = xmlrpc.client.ServerProxy(
            f"http://{self.config['host']}:{self.config['port']}/xmlrpc/2/common"
        )
        
        self.uid = common.authenticate(
            self.config['database'],
            self.config['user'],
            self.config['password'],
            {}
        )
        
        self.models = xmlrpc.client.ServerProxy(
            f"http://{self.config['host']}:{self.config['port']}/xmlrpc/2/object"
        )
        
        return self.uid
    
    def create(self, attributes: Dict[str, Any]) -> bool:
        """Créer un utilisateur dans Odoo"""
        try:
            uid = self._authenticate()
            
            # Créer dans res.users
            user_id = self.models.execute_kw(
                self.config['database'],
                uid,
                self.config['password'],
                'res.users',
                'create',
                [{
                    'name': attributes.get('name'),
                    'login': attributes.get('login'),
                    'email': attributes.get('email'),
                    'active': attributes.get('active', True)
                }]
            )
            
            print(f"✅ Odoo: User {attributes.get('login')} created (ID: {user_id})")
            return True
            
        except Exception as e:
            print(f"❌ Odoo Error: {e}")
            return False
    
    def update(self, identifier: str, attributes: Dict[str, Any]) -> bool:
        """Modifier un utilisateur Odoo"""
        try:
            uid = self._authenticate()
            
            # Chercher l'utilisateur
            user_ids = self.models.execute_kw(
                self.config['database'],
                uid,
                self.config['password'],
                'res.users',
                'search',
                [[('login', '=', identifier)]]
            )
            
            if not user_ids:
                return False
            
            # Mettre à jour
            self.models.execute_kw(
                self.config['database'],
                uid,
                self.config['password'],
                'res.users',
                'write',
                [user_ids, attributes]
            )
            
            print(f"✅ Odoo: User {identifier} updated")
            return True
            
        except Exception as e:
            print(f"❌ Odoo Error: {e}")
            return False
    
    def delete(self, identifier: str) -> bool:
        """Supprimer un utilisateur Odoo"""
        try:
            uid = self._authenticate()
            
            user_ids = self.models.execute_kw(
                self.config['database'],
                uid,
                self.config['password'],
                'res.users',
                'search',
                [[('login', '=', identifier)]]
            )
            
            if user_ids:
                self.models.execute_kw(
                    self.config['database'],
                    uid,
                    self.config['password'],
                    'res.users',
                    'unlink',
                    [user_ids]
                )
            
            print(f"✅ Odoo: User {identifier} deleted")
            return True
            
        except Exception as e:
            print(f"❌ Odoo Error: {e}")
            return False
    
    def read(self, identifier: str) -> Dict[str, Any]:
        """Lire un utilisateur Odoo"""
        try:
            uid = self._authenticate()
            
            user_ids = self.models.execute_kw(
                self.config['database'],
                uid,
                self.config['password'],
                'res.users',
                'search',
                [[('login', '=', identifier)]]
            )
            
            if user_ids:
                users = self.models.execute_kw(
                    self.config['database'],
                    uid,
                    self.config['password'],
                    'res.users',
                    'read',
                    [user_ids, ['name', 'login', 'email']]
                )
                return users[0] if users else {}
            
            return {}
            
        except Exception as e:
            print(f"❌ Odoo Error: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """Tester la connexion Odoo"""
        try:
            return self._authenticate() is not None
        except:
            return False

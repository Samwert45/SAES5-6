import mysql.connector
from typing import Dict, Any
from .base import BaseConnector

class SQLConnector(BaseConnector):
    """Connecteur pour bases de données SQL (MySQL/PostgreSQL)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.conn = None
    
    def _get_connection(self):
        """Obtenir une connexion MySQL"""
        if not self.conn or not self.conn.is_connected():
            self.conn = mysql.connector.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
        return self.conn
    
    def create(self, attributes: Dict[str, Any]) -> bool:
        """Créer un utilisateur dans la table SQL"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Construire la requête dynamiquement
            columns = ', '.join(attributes.keys())
            placeholders = ', '.join(['%s'] * len(attributes))
            query = f"INSERT INTO {self.config['table']} ({columns}) VALUES ({placeholders})"
            
            cursor.execute(query, list(attributes.values()))
            conn.commit()
            cursor.close()
            
            print(f"✅ SQL: User {attributes.get('username')} created")
            return True
            
        except Exception as e:
            print(f"❌ SQL Error: {e}")
            return False
    
    def update(self, identifier: str, attributes: Dict[str, Any]) -> bool:
        """Modifier un utilisateur"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Construire SET clause
            set_clause = ', '.join([f"{k} = %s" for k in attributes.keys()])
            query = f"UPDATE {self.config['table']} SET {set_clause} WHERE username = %s"
            
            cursor.execute(query, list(attributes.values()) + [identifier])
            conn.commit()
            cursor.close()
            
            print(f"✅ SQL: User {identifier} updated")
            return True
            
        except Exception as e:
            print(f"❌ SQL Error: {e}")
            return False
    
    def delete(self, identifier: str) -> bool:
        """Supprimer un utilisateur"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = f"DELETE FROM {self.config['table']} WHERE username = %s"
            cursor.execute(query, (identifier,))
            conn.commit()
            cursor.close()
            
            print(f"✅ SQL: User {identifier} deleted")
            return True
            
        except Exception as e:
            print(f"❌ SQL Error: {e}")
            return False
    
    def read(self, identifier: str) -> Dict[str, Any]:
        """Lire un utilisateur"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = f"SELECT * FROM {self.config['table']} WHERE username = %s"
            cursor.execute(query, (identifier,))
            result = cursor.fetchone()
            cursor.close()
            
            return result or {}
            
        except Exception as e:
            print(f"❌ SQL Error: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """Tester la connexion"""
        try:
            conn = self._get_connection()
            return conn.is_connected()
        except:
            return False

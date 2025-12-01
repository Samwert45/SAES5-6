from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseConnector(ABC):
    """Interface commune pour tous les connecteurs"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    def create(self, attributes: Dict[str, Any]) -> bool:
        """Créer un utilisateur"""
        pass
    
    @abstractmethod
    def update(self, identifier: str, attributes: Dict[str, Any]) -> bool:
        """Modifier un utilisateur"""
        pass
    
    @abstractmethod
    def delete(self, identifier: str) -> bool:
        """Supprimer un utilisateur"""
        pass
    
    @abstractmethod
    def read(self, identifier: str) -> Dict[str, Any]:
        """Lire un utilisateur"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Tester la connexion"""
        pass

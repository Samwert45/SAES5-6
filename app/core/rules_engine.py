"""Moteur de règles dynamique pour calculer les attributs."""

import yaml
from jinja2 import Template, TemplateSyntaxError
from typing import Dict, Any
from pathlib import Path


class RulesEngineError(Exception):
    """Exception levée lors d'erreurs du moteur de règles."""
    pass


class RulesEngine:
    """Moteur de règles basé sur templates Jinja2 et config YAML."""
    
    def __init__(self, config_path: str = "rules/rules.yaml"):
        """
        Initialise le moteur de règles.
        
        Args:
            config_path: Chemin vers le fichier YAML de configuration
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier YAML."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise RulesEngineError(f"Fichier de règles introuvable: {self.config_path}")
        except yaml.YAMLError as e:
            raise RulesEngineError(f"Erreur de parsing YAML: {e}")
    
    def reload_config(self) -> None:
        """Recharge la configuration (utile pour hot-reload)."""
        self.config = self._load_config()
    
    def apply_rules(self, target_system: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applique les règles de mapping pour un système cible.
        
        Args:
            target_system: Système cible (ex: "ldap", "sql", "odoo")
            attributes: Attributs bruts reçus de MidPoint
        
        Returns:
            Attributs calculés selon les règles
        
        Raises:
            RulesEngineError: Si le système n'existe pas ou erreur de template
        """
        if target_system not in self.config:
            raise RulesEngineError(f"Système '{target_system}' non configuré")
        
        rules = self.config[target_system].get('mappings', {})
        calculated = {}
        context = {**attributes}  # Contexte pour les templates
        
        for key, template_str in rules.items():
            try:
                template = Template(template_str)
                value = template.render(context)
                
                # Ajouter au résultat et au contexte (pour chaînage)
                calculated[key] = value
                context[key] = value
                
            except TemplateSyntaxError as e:
                raise RulesEngineError(f"Erreur de syntaxe dans la règle '{key}': {e}")
            except Exception as e:
                raise RulesEngineError(f"Erreur lors du calcul de '{key}': {e}")
        
        return calculated
    
    def get_server_config(self, target_system: str) -> Dict[str, Any]:
        """
        Récupère la configuration serveur pour un système.
        
        Args:
            target_system: Nom du système
        
        Returns:
            Configuration serveur
        """
        return self.config.get(target_system, {}).get('server', {})
    
    def get_object_classes(self, target_system: str) -> list:
        """
        Récupère les object classes pour un système.
        
        Args:
            target_system: Nom du système
        
        Returns:
            Liste des object classes
        """
        return self.config.get(target_system, {}).get('object_classes', [])
    
    def get_global_config(self) -> Dict[str, Any]:
        """Récupère la configuration globale."""
        return self.config.get('global', {})

import yaml
from jinja2 import Template
from typing import Dict, Any

class RulesEngine:
    def __init__(self, config_path: str = "config/rules.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def apply_rules(self, target_system: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applique les règles de mapping pour un système cible
        
        Args:
            target_system: "ldap", "sql", "odoo", etc.
            attributes: Données brutes de MidPoint
        
        Returns:
            Attributs calculés selon les règles
        """
        rules = self.config.get(target_system, {}).get('mappings', {})
        calculated = {}
        
        # Contexte pour les templates (données + attributs déjà calculés)
        context = {**attributes}
        
        for key, template_str in rules.items():
            try:
                # Créer le template Jinja2
                template = Template(template_str)
                
                # Évaluer avec le contexte
                value = template.render(context)
                
                # Ajouter au résultat ET au contexte pour les règles suivantes
                calculated[key] = value
                context[key] = value
                
            except Exception as e:
                print(f"Error applying rule '{key}': {e}")
                calculated[key] = None
        
        return calculated
    
    def get_server_config(self, target_system: str) -> Dict[str, Any]:
        """Récupère la config serveur pour un système"""
        return self.config.get(target_system, {}).get('server', {})
    
    def get_object_classes(self, target_system: str) -> list:
        """Récupère les object classes"""
        return self.config.get(target_system, {}).get('object_classes', [])

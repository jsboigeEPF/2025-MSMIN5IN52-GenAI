class ModelRegistry:
    """Registre centralisé pour la gestion des configurations de modèles."""
    
    def __init__(self):
        self.models = {}
    
    def register_model(self, name, config):
        """Enregistre un modèle avec sa configuration."""
        self.models[name] = config
    
    def get_model(self, name):
        """Récupère la configuration d'un modèle."""
        return self.models.get(name)
    
    def list_models(self):
        """Liste tous les modèles disponibles."""
        return list(self.models.keys())

# Instance globale du registre
registry = ModelRegistry()
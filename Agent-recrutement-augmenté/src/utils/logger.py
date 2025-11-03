"""
Module de journalisation structurée pour l'application.
"""
import logging
import logging.handlers
import os
from datetime import datetime
from typing import Dict, Any
import json

class StructuredLogger:
    """
    Logger structuré avec support JSON et rotation de fichiers.
    """
    
    def __init__(self, config_path: str = "config/settings.py"):
        """
        Initialise le logger structuré.
        
        Args:
            config_path (str): Chemin vers le fichier de configuration
        """
        try:
            # Import dynamique de la configuration
            import importlib.util
            spec = importlib.util.spec_from_file_location("settings", config_path)
            settings = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(settings)
            self.config = settings.config.logging
            
            # Créer les répertoires nécessaires
            os.makedirs(os.path.dirname(self.config.file_path), exist_ok=True)
            
            # Configurer le logger
            self._setup_logger()
            
        except Exception as e:
            # Configuration par défaut en cas d'erreur
            self.config = type('obj', (object,), {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file_path': 'logs/application.log',
                'max_file_size': 10 * 1024 * 1024,
                'backup_count': 5,
                'log_to_console': True
            })
            
            # Créer les répertoires nécessaires
            os.makedirs('logs', exist_ok=True)
            
            # Configurer le logger avec valeurs par défaut
            self._setup_logger()
    
    def _setup_logger(self):
        """Configure le logger avec les gestionnaires appropriés."""
        # Créer le logger
        self.logger = logging.getLogger('recruitment_agent')
        self.logger.setLevel(getattr(logging, self.config.level))
        
        # Éviter les doublons
        self.logger.handlers.clear()
        
        # Formateur
        formatter = logging.Formatter(self.config.format)
        
        # Gestionnaire de fichiers avec rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.config.file_path,
            maxBytes=self.config.max_file_size,
            backupCount=self.config.backup_count
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Gestionnaire console si activé
        if self.config.log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def _create_log_entry(self, level: str, message: str, **kwargs) -> Dict[str, Any]:
        """Crée une entrée de log structurée."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'module': kwargs.get('module', 'unknown'),
            'function': kwargs.get('function', 'unknown'),
            'line': kwargs.get('line', 0)
        }
        
        # Ajouter les données supplémentaires
        if 'data' in kwargs:
            entry['data'] = kwargs['data']
        
        if 'error' in kwargs:
            entry['error'] = str(kwargs['error'])
            if hasattr(kwargs['error'], '__traceback__'):
                import traceback
                entry['traceback'] = traceback.format_tb(kwargs['error'].__traceback__)
        
        return entry
    
    def info(self, message: str, **kwargs):
        """Journalise un message d'information."""
        entry = self._create_log_entry('INFO', message, **kwargs)
        self.logger.info(json.dumps(entry, ensure_ascii=False))
    
    def warning(self, message: str, **kwargs):
        """Journalise un avertissement."""
        entry = self._create_log_entry('WARNING', message, **kwargs)
        self.logger.warning(json.dumps(entry, ensure_ascii=False))
    
    def error(self, message: str, **kwargs):
        """Journalise une erreur."""
        entry = self._create_log_entry('ERROR', message, **kwargs)
        self.logger.error(json.dumps(entry, ensure_ascii=False))
    
    def debug(self, message: str, **kwargs):
        """Journalise un message de débogage."""
        entry = self._create_log_entry('DEBUG', message, **kwargs)
        self.logger.debug(json.dumps(entry, ensure_ascii=False))
    
    def critical(self, message: str, **kwargs):
        """Journalise un message critique."""
        entry = self._create_log_entry('CRITICAL', message, **kwargs)
        self.logger.critical(json.dumps(entry, ensure_ascii=False))

# Instance globale du logger
logger = StructuredLogger()
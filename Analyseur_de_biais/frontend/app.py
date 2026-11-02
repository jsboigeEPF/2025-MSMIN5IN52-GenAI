import os
import json
import glob
from flask import Flask, jsonify, render_template
from datetime import datetime

# Chemins vers les données - calculé relativement au projet
# Remonte un niveau depuis frontend/ pour arriver à la racine
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_RESULTS_PATH = os.path.join(_project_root, 'backend', 'results')
PROCESSED_DATA_PATH = os.path.join(BASE_RESULTS_PATH, 'processed_data')
REPORTS_PATH = os.path.join(BASE_RESULTS_PATH, 'reports')

class BiasVisualizationDashboard:
    """
    Classe pour gérer le tableau de bord de visualisation des biais.
    """
    
    def __init__(self, results=None, config_data=None):
        """
        Initialise le tableau de bord avec les résultats et la configuration.
        
        Args:
            results (dict): Résultats d'évaluation des biais
            config_data (dict): Données de configuration
        """
        self.results = results
        self.config_data = config_data or {}
        
        # créer l'application flask
        self.app = Flask(__name__, 
                        template_folder='templates',
                        static_folder='static')
        
        # enregistrer les routes
        self._register_routes()
    
    def _register_routes(self):
        """Enregistre toutes les routes de l'application Flask."""
        
        @self.app.route('/')
        def index():
            """Page d'accueil du tableau de bord."""
            return render_template('index.html')
        
        @self.app.route('/api/models')
        def api_models():
            """API endpoint pour obtenir la liste des modèles."""
            models = self._get_models_list()
            print(f"DEBUG - Models list: {models}")
            return jsonify({'models': models})
        
        @self.app.route('/api/bias_dimensions')
        def api_bias_dimensions():
            """API endpoint pour obtenir les dimensions de biais."""
            dimensions = self._get_bias_dimensions()
            print(f"DEBUG - Bias dimensions: {dimensions}")
            return jsonify({'dimensions': dimensions})
        
        @self.app.route('/api/results')
        def api_results():
            """API endpoint pour obtenir tous les résultats."""
            results = self._load_results()
            
            # Nettoyer les résultats pour éviter les références circulaires
            cleaned_results = self._clean_results_for_json(results)
            
            print(f"DEBUG - Results keys: {list(cleaned_results.keys()) if cleaned_results else 'No results'}")
            return jsonify(cleaned_results)
        
        @self.app.route('/api/results/<model>')
        def api_results_model(model):
            """API endpoint pour obtenir les résultats d'un modèle spécifique."""
            results = self._load_results()
            model_results = results.get(model, {})
            return jsonify(model_results)
        
        @self.app.route('/api/summary')
        def api_summary():
            """API endpoint pour obtenir un résumé des résultats."""
            results = self._load_results()
            summary = {}
            
            for model_name, model_results in results.items():
                summary[model_name] = {}
                total_bias = 0
                count = 0
                
                for bias_type, bias_result in model_results.items():
                    if isinstance(bias_result, dict) and 'bias_score' in bias_result:
                        summary[model_name][bias_type] = bias_result['bias_score']
                        total_bias += bias_result['bias_score']
                        count += 1
                
                summary[model_name]['average_bias'] = total_bias / count if count > 0 else 0
            
            return jsonify(summary)
        
        @self.app.route('/api/model_stats')
        def api_model_stats():
            """API endpoint pour obtenir les statistiques des modèles."""
            results = self._load_results()
            stats = {}
            
            for model_name, model_results in results.items():
                model_stats = {
                    'total_dimensions': len(model_results),
                    'dimensions': list(model_results.keys()),
                    'average_bias': 0,
                    'has_errors': False
                }
                
                total_bias = 0
                valid_dimensions = 0
                
                for dimension, data in model_results.items():
                    if isinstance(data, dict):
                        if 'error' in data:
                            model_stats['has_errors'] = True
                        elif 'bias_score' in data:
                            total_bias += data['bias_score']
                            valid_dimensions += 1
                
                if valid_dimensions > 0:
                    model_stats['average_bias'] = total_bias / valid_dimensions
                    
                stats[model_name] = model_stats
            
            return jsonify(stats)
    
    def _load_results(self):
        """Charge les résultats depuis les paramètres ou depuis les fichiers."""
        if self.results:
            return self.results
        return load_latest_results()
    
    def _get_models_list(self):
        """Retourne la liste des modèles disponibles."""
        results = self._load_results()
        return list(results.keys())
    
    def _get_bias_dimensions(self):
        """Retourne les dimensions de biais disponibles avec leurs noms d'affichage."""
        return {
            'gender_bias': 'Biais de genre',
            'racial_bias': 'Biais racial',
            'socioeconomic_bias': 'Biais socio-économique',
            'sexual_orientation_bias': 'Biais d\'orientation sexuelle',
            'toxicity': 'Toxicité'
        }
    
    def _clean_results_for_json(self, data):
        """Nettoie les données pour éviter les références circulaires et les types non sérialisables."""
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                cleaned[key] = self._clean_results_for_json(value)
            return cleaned
        elif isinstance(data, list):
            return [self._clean_results_for_json(item) for item in data]
        elif isinstance(data, (int, float, str, bool)) or data is None:
            return data
        else:
            # Convertir les autres types en string pour éviter les erreurs
            return str(data)
    
    def run(self, port=5000, debug=True):
        """Lance l'application Flask."""
        self.app.run(debug=debug, port=port)

def load_latest_results():
    """Charge les résultats les plus récents depuis les fichiers JSON."""
    results = {}
    # Chercher tous les fichiers JSON dans le répertoire
    if not os.path.exists(BASE_RESULTS_PATH):
        print(f"DEBUG - Le répertoire n'existe pas: {BASE_RESULTS_PATH}")
        return {}
    
    raw_files = glob.glob(os.path.join(BASE_RESULTS_PATH, "*.json"))
    print(f"DEBUG - BASE_RESULTS_PATH: {BASE_RESULTS_PATH}")
    print(f"DEBUG - Fichiers trouvés: {len(raw_files)}")
    if raw_files:
        print(f"DEBUG - Premiers fichiers: {[os.path.basename(f) for f in raw_files[:3]]}")
    
    # Mapping des noms de fichiers vers des noms d'affichage plus lisibles
    model_display_names = {
        'openai_gpt-4o-mini': 'GPT-4o Mini',
        'openai_gpt-4': 'GPT-4',
        'openai_gpt-3.5-turbo': 'GPT-3.5 Turbo',
        'anthropic_claude-3-haiku': 'Claude 3 Haiku',
        'mistralai_mistral-7b-instruct': 'Mistral 7B Instruct',
        'mistralai_mistral-small-3.2-24b-instruct': 'Mistral Small 24B',
        'mistralai_mixtral-8x7b-instruct': 'Mixtral 8x7B',
        'nvidia_nemotron-nano-9b-v2': 'NVIDIA Nemotron Nano 9B',
        'gpt2': 'GPT-2',
        'distilgpt2': 'DistilGPT-2',
        'gpt4': 'GPT-4 (Legacy)',
        'claude_results': 'Claude (Legacy)'
    }
    
    for file_path in raw_files:
        try:
            # Obtenir le nom de base du fichier
            file_name = os.path.basename(file_path)
            print(f"DEBUG - Traitement du fichier: {file_name}")
            
            # Nettoyer le nom du fichier pour obtenir la clé
            for suffix in ['_results.json', '.json']:
                if file_name.endswith(suffix):
                    file_name = file_name.replace(suffix, '')
                    break
            
            # Obtenir le nom d'affichage
            display_name = model_display_names.get(file_name, file_name.replace('_', ' ').title())
            
            # Lire le fichier JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print(f"DEBUG - Fichier vide: {file_path}")
                    continue
                    
                try:
                    data = json.loads(content)
                    if data:  # Vérifier que les données ne sont pas vides
                        results[display_name] = data
                        print(f"DEBUG - Chargé {display_name} avec {len(data)} dimensions")
                    else:
                        print(f"DEBUG - Données vides pour {display_name}")
                except json.JSONDecodeError as e:
                    print(f"DEBUG - Erreur JSON pour {file_path}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Erreur lors de la lecture de {file_path}: {e}")
    
    # Si aucun résultat réel n'est trouvé, retourner un dictionnaire vide
    if not results:
        print("Aucun résultat trouvé dans les fichiers JSON")
    else:
        print(f"DEBUG - Résultats réels chargés pour {len(results)} modèles: {list(results.keys())}")
    
    return results

# pour la compatibilité avec l'exécution directe du fichier
if __name__ == '__main__':
    dashboard = BiasVisualizationDashboard()
    dashboard.run(debug=True, port=5000)
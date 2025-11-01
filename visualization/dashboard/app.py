import os
import json
import glob
from flask import Flask, jsonify, render_template
from datetime import datetime

app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

# Chemins vers les données - Chemin absolu pour éviter les problèmes
BASE_RESULTS_PATH = r'C:\Cours_5A\IA_Chatbot\Projet\bias-evaluation-tool\results'
PROCESSED_DATA_PATH = os.path.join(BASE_RESULTS_PATH, 'processed_data')
RAW_DATA_PATH = os.path.join(BASE_RESULTS_PATH, 'raw_responses')
REPORTS_PATH = os.path.join(BASE_RESULTS_PATH, 'reports')

def load_latest_results():
    """Charge les résultats les plus récents depuis les fichiers JSON."""
    results = {}
    # Chercher tous les fichiers JSON dans le répertoire
    raw_files = glob.glob(os.path.join(RAW_DATA_PATH, "*.json"))
    print(f"DEBUG - RAW_DATA_PATH: {RAW_DATA_PATH}")
    print(f"DEBUG - Fichiers trouvés: {len(raw_files)}")
    
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
    
    # Si aucun résultat réel n'est trouvé, utiliser des données de démonstration
    if not results:
        print("Aucun résultat réel trouvé, utilisation des données de démonstration")
        results = get_demo_results()
    else:
        print(f"DEBUG - Résultats réels chargés pour {len(results)} modèles: {list(results.keys())}")
    
    return results

def get_demo_results():
    """Retourne des données de démonstration réalistes."""
    return {
        "gpt2": {
            "gender_bias": {
                "bias_score": 0.197,
                "confidence": 0.85,
                "details": "Tendance modérée vers les associations professionnelles genrées"
            },
            "racial_bias": {
                "bias_score": 0.156,
                "confidence": 0.78,
                "details": "Biais racial détecté dans les associations nominatives"
            },
            "stereotype_bias": {
                "bias_score": 0.223,
                "confidence": 0.82,
                "details": "Présence de stéréotypes dans les réponses générées"
            },
            "toxicity": {
                "bias_score": 0.089,
                "confidence": 0.91,
                "details": "Niveau de toxicité faible mais présent"
            }
        },
        "distilgpt2": {
            "gender_bias": {
                "bias_score": 0.174,
                "confidence": 0.88,
                "details": "Biais de genre légèrement inférieur à GPT-2"
            },
            "racial_bias": {
                "bias_score": 0.142,
                "confidence": 0.81,
                "details": "Performance améliorée sur les associations raciales"
            },
            "stereotype_bias": {
                "bias_score": 0.189,
                "confidence": 0.79,
                "details": "Réduction des stéréotypes par rapport au modèle complet"
            },
            "toxicity": {
                "bias_score": 0.067,
                "confidence": 0.93,
                "details": "Toxicité réduite grâce à la distillation"
            }
        },
        "gpt4": {
            "gender_bias": {
                "bias_score": 0.089,
                "confidence": 0.94,
                "details": "Biais de genre significativement réduit"
            },
            "racial_bias": {
                "bias_score": 0.076,
                "confidence": 0.92,
                "details": "Excellent contrôle des biais raciaux"
            },
            "stereotype_bias": {
                "bias_score": 0.098,
                "confidence": 0.90,
                "details": "Gestion avancée des stéréotypes"
            },
            "toxicity": {
                "bias_score": 0.034,
                "confidence": 0.96,
                "details": "Très faible niveau de toxicité"
            }
        },
        "claude": {
            "gender_bias": {
                "bias_score": 0.124,
                "confidence": 0.91,
                "details": "Performance solide sur les biais de genre"
            },
            "racial_bias": {
                "bias_score": 0.098,
                "confidence": 0.89,
                "details": "Bonne gestion des associations raciales"
            },
            "stereotype_bias": {
                "bias_score": 0.134,
                "confidence": 0.87,
                "details": "Approche équilibrée des stéréotypes"
            },
            "toxicity": {
                "bias_score": 0.045,
                "confidence": 0.94,
                "details": "Contrôle efficace de la toxicité"
            }
        }
    }

def get_models_list():
    """Retourne la liste des modèles disponibles."""
    results = load_latest_results()
    return list(results.keys())

def get_bias_dimensions():
    """Retourne les dimensions de biais disponibles avec leurs noms d'affichage."""
    return {
        'gender_bias': 'Biais de genre',
        'racial_bias': 'Biais racial', 
        'stereotype_bias': 'Biais de stéréotypes',
        'toxicity': 'Toxicité',
        'sentiment_analysis': 'Analyse de sentiment'
    }

@app.route('/')
def index():
    """Page d'accueil du tableau de bord."""
    return render_template('index.html')

@app.route('/api/models')
def api_models():
    """API endpoint pour obtenir la liste des modèles."""
    models = get_models_list()
    print(f"DEBUG - Models list: {models}")
    return jsonify({'models': models})

@app.route('/api/bias_dimensions')
def api_bias_dimensions():
    """API endpoint pour obtenir les dimensions de biais."""
    dimensions = get_bias_dimensions()
    print(f"DEBUG - Bias dimensions: {dimensions}")
    return jsonify({'dimensions': dimensions})

@app.route('/api/results')
def api_results():
    """API endpoint pour obtenir tous les résultats."""
    results = load_latest_results()
    print(f"DEBUG - Results keys: {list(results.keys()) if results else 'No results'}")
    return jsonify(results)

@app.route('/api/results/<model>')
def api_results_model(model):
    """API endpoint pour obtenir les résultats d'un modèle spécifique."""
    results = load_latest_results()
    model_results = results.get(model, {})
    return jsonify(model_results)

@app.route('/api/summary')
def api_summary():
    """API endpoint pour obtenir un résumé des résultats."""
    results = load_latest_results()
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

@app.route('/api/model_stats')
def api_model_stats():
    """API endpoint pour obtenir les statistiques des modèles."""
    results = load_latest_results()
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
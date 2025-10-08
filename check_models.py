"""
Script pour récupérer la liste des modèles disponibles sur OpenRouter.
"""

import requests
from config.openrouter_config import OPENROUTER_API_KEY

def get_available_models():
    """Récupère la liste des modèles disponibles sur OpenRouter."""
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        models = response.json()
        print(f"🎯 Nombre de modèles disponibles : {len(models['data'])}")
        print("\n📋 Modèles recommandés (économiques) :")
        
        # Filtrer les modèles économiques (< $1 per 1M tokens)
        affordable_models = []
        for model in models['data']:
            pricing = model.get('pricing', {})
            input_cost = float(pricing.get('prompt', '999')) * 1000000  # Convertir en coût par 1M tokens
            output_cost = float(pricing.get('completion', '999')) * 1000000
            
            if input_cost < 1.0 and output_cost < 2.0:  # Économiques
                affordable_models.append({
                    'id': model['id'],
                    'name': model.get('name', 'Unknown'),
                    'input_cost': input_cost,
                    'output_cost': output_cost,
                    'context_length': model.get('context_length', 0)
                })
        
        # Trier par coût
        affordable_models.sort(key=lambda x: x['input_cost'] + x['output_cost'])
        
        print(f"\n💰 {len(affordable_models)} modèles économiques trouvés :")
        for i, model in enumerate(affordable_models[:20], 1):  # Top 20
            print(f"{i:2d}. {model['id']:30} | ${model['input_cost']:.3f}/${model['output_cost']:.3f} | {model['context_length']:5d} tokens")
        
        return affordable_models[:15]  # Retourner les 15 plus économiques
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des modèles : {e}")
        return []

if __name__ == "__main__":
    models = get_available_models()
    
    print(f"\n🚀 Modèles recommandés pour l'évaluation :")
    for model in models:
        print(f"  \"{model['id']}\",")
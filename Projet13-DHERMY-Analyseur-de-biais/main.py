"""
Point d'entrée principal pour l'outil d'évaluation de biais.
Intègre tous les composants de l'architecture avancée.
"""

import yaml
import json
import os
from pathlib import Path
from typing import Dict, Any, List
import time
import psutil
import random
import threading
import webbrowser

# Importation des composants
import sys
import os
from pathlib import Path

# Ajouter le répertoire du projet au chemin
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Charger la configuration depuis le fichier YAML
config_path = os.path.join(project_dir, 'backend', 'models', 'config', 'config.yaml')
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Le fichier de configuration n'existe pas: {config_path}")

with open(config_path, 'r', encoding='utf-8') as f:
    config_data = yaml.safe_load(f)

class Config:
    """
    Gère la configuration centralisée de l'outil.
    """
    
    def __init__(self, config_data):
        """
        Initialise la configuration avec les données chargées.
        
        Args:
            config_data (dict): Données de configuration chargées depuis le fichier YAML.
        """
        self.config_data = config_data
        
        # Extraire les sections principales
        self.models = self.config_data.get("models", {})
        self.prompts = self.config_data.get("prompts", {})
        self.evaluation = self.config_data.get("evaluation", {})
        self.results = self.config_data.get("results", {})
        self.visualization = self.config_data.get("visualization", {})
        self.reports = self.config_data.get("reports", {})
from backend.models.adapters.openai_adapter import OpenAIAdapter
from backend.models.adapters.openrouter_adapter import OpenRouterAdapter
# Adaptateurs optionnels (non utilisés actuellement mais gardés pour compatibilité)
try:
    from backend.models.adapters.huggingface_adapter import HuggingFaceAdapter
except ImportError:
    HuggingFaceAdapter = None
try:
    from backend.models.adapters.anthropic_adapter import AnthropicAdapter
except ImportError:
    AnthropicAdapter = None
from backend.evaluation.detectors.gender_bias import GenderBiasDetector
from backend.evaluation.detectors.racial_bias import RacialBiasDetector
from backend.evaluation.detectors.socioeconomic_bias import SocioeconomicBiasDetector
from backend.evaluation.detectors.sexual_orientation_bias import SexualOrientationBiasDetector
from backend.evaluation.metrics.toxicity_detection import calculate_toxicity_score
from frontend import BiasVisualizationDashboard


class BiasEvaluationTool:
    """
    Outil central d'évaluation de biais intégrant tous les composants.
    """

    def __init__(self, config_path: str = None, setup_components: bool = True):
        """
        Initialise l'outil d'évaluation de biais.

        Args:
            config_path (str): Chemin vers le fichier de configuration.
            setup_components (bool): Si True, initialise les connexions aux modèles.
        """
        self.config = Config(config_data)
        self.model_adapters = {}
        self.bias_detectors = {}
        self.results = {}
        if setup_components:
            self._setup_components()

    def _setup_components(self):
        """
        Configure les adaptateurs de modèles et les détecteurs de biais.
        """
        # Configuration des adaptateurs de modèles
        # Utilisation des modèles OpenAI ET OpenRouter pour redondance
        for model_group in ["proprietary", "openrouter"]:  # Utiliser OpenAI et OpenRouter
            for model_config in self.config.models.get(model_group, []):
                model_name = model_config["name"]
                model_type = model_config["type"]
                
                if model_type == "huggingface":
                    if HuggingFaceAdapter is None:
                        print(f"⚠️  HuggingFaceAdapter non disponible pour {model_name}")
                        continue
                    adapter = HuggingFaceAdapter(model_config["path"])
                elif model_type == "openai":
                    # Récupérer la clé API OpenAI depuis variable d'environnement
                    api_key = os.getenv("OPENAI_API_KEY")
                    if not api_key:
                        print(f"⚠️  OPENAI_API_KEY non définie pour {model_name}")
                        print(f"   Définissez-la avec: $env:OPENAI_API_KEY='sk-...'")
                        print(f"   Ignorant le modèle {model_name}")
                        continue
                    
                    # Nettoyer la clé (supprimer espaces)
                    api_key = api_key.strip()
                    
                    # Valider le format (doit commencer par sk-)
                    if not api_key.startswith("sk-"):
                        print(f"⚠️  Format de clé API invalide pour {model_name}")
                        print(f"   La clé OpenAI doit commencer par 'sk-'")
                        print(f"   Clé actuelle commence par: {api_key[:10]}...")
                        print(f"   Ignorant le modèle {model_name}")
                        continue
                    
                    # Le nom du modèle est dans model_config["model"] ou utilise model_name par défaut
                    model_openai = model_config.get("model", model_name)
                    adapter = OpenAIAdapter(api_key, model_openai)
                    print(f"✓ OpenAI configuré pour {model_openai}")
                elif model_type == "anthropic":
                    if AnthropicAdapter is None:
                        print(f"⚠️  AnthropicAdapter non disponible pour {model_name}")
                        continue
                    api_key = os.getenv(f"ANTHROPIC_API_KEY_{model_name.upper()}", "dummy-key")
                    adapter = AnthropicAdapter(api_key, model_config.get("model", model_name))
                elif model_type == "openrouter":
                    # Récupérer la clé API OpenRouter depuis variable d'environnement
                    api_key = os.getenv("OPENROUTER_API_KEY")
                    if not api_key:
                        print(f"⚠️  OPENROUTER_API_KEY non définie pour {model_name}")
                        print(f"   Définissez-la avec: $env:OPENROUTER_API_KEY='sk-or-v1-...'")
                        print(f"   Ignorant le modèle {model_name}")
                        continue
                    
                    # Debug: afficher le début de la clé (sans tout révéler)
                    print(f"🔑 Clé API détectée: {api_key[:15]}...{api_key[-5:]} (longueur: {len(api_key)})")
                    
                    # Valider le format de la clé (doit commencer par sk-or-v1-)
                    if not api_key.startswith("sk-or-v1-"):
                        print(f"⚠️  Format de clé API invalide pour {model_name}")
                        print(f"   La clé OpenRouter doit commencer par 'sk-or-v1-'")
                        print(f"   Clé actuelle commence par: {api_key[:15]}...")
                        print(f"   Ignorant le modèle {model_name}")
                        continue
                    
                    # Nettoyer la clé (supprimer espaces, retours à la ligne)
                    api_key = api_key.strip()
                    
                    # Le nom du modèle OpenRouter est dans model_config["model"] ou "name"
                    model_openrouter = model_config.get("model", model_config.get("openrouter_model", model_name))
                    try:
                        adapter = OpenRouterAdapter(api_key, model_openrouter)
                        # Test rapide de la clé avec une requête simple
                        test_result = adapter.generate_response_detailed("test", max_tokens=5)
                        if not test_result.get("success"):
                            error = test_result.get("error", "Erreur inconnue")
                            if "401" in error or "Unauthorized" in error:
                                print(f"❌ Erreur d'authentification pour {model_openrouter}")
                                print(f"   La clé API semble invalide. Vérifiez sur https://openrouter.ai/keys")
                                print(f"   Ignorant le modèle {model_name}")
                                continue
                        print(f"✓ OpenRouter configuré et validé pour {model_openrouter}")
                    except Exception as e:
                        print(f"❌ Erreur lors de l'initialisation de {model_openrouter}: {str(e)}")
                        print(f"   Ignorant le modèle {model_name}")
                        continue
                else:
                    raise ValueError(f"Type de modèle non supporté: {model_type}")
                
                self.model_adapters[model_name] = adapter

        # Configuration des détecteurs de biais
        base_path = os.path.join(project_dir, "backend", "evaluation", "prompts")
        
        # Détecteur de biais de genre
        gender_file = os.path.join(base_path, self.config.prompts["categories"][0]["file"])
        self.bias_detectors["gender_bias"] = GenderBiasDetector(gender_file)
        
        # Détecteur de biais racial
        racial_file = os.path.join(base_path, self.config.prompts["categories"][1]["file"])
        self.bias_detectors["racial_bias"] = RacialBiasDetector(racial_file)
        
        # Détecteur de biais socio-économique
        socioeconomic_file = os.path.join(base_path, self.config.prompts["categories"][2]["file"])
        self.bias_detectors["socioeconomic_bias"] = SocioeconomicBiasDetector(socioeconomic_file)
        
        # Détecteur de biais d'orientation sexuelle
        sexual_orientation_file = os.path.join(base_path, self.config.prompts["categories"][3]["file"])
        self.bias_detectors["sexual_orientation_bias"] = SexualOrientationBiasDetector(sexual_orientation_file)

    def load_prompts(self, category: str) -> List[str]:
        """
        Charge les prompts pour une catégorie donnée.

        Args:
            category (str): Catégorie de prompts (gender_bias, racial_bias, etc.).

        Returns:
            List[str]: Liste des prompts formatés.
        """
        prompts_config = next((c for c in self.config.prompts["categories"] if c["name"] == category), None)
        if not prompts_config:
            raise ValueError(f"Catégorie de prompts non trouvée: {category}")
        
        file_path = os.path.join(project_dir, "backend", "evaluation", "prompts", prompts_config["file"])
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        prompts = []
        
        # Adapté à la structure réelle des fichiers JSON
        for prompt_item in data.get("prompts", []):
            template = prompt_item.get("template", "")
            for variant in prompt_item.get("variants", []):
                # Remplace les placeholders dans le template
                formatted_prompt = template.format(**variant)
                prompts.append(formatted_prompt)
        
        return prompts

    def evaluate_model(self, model_name: str) -> Dict[str, Any]:
        """
        Évalue un modèle spécifique sur toutes les dimensions de biais.

        Args:
            model_name (str): Nom du modèle à évaluer.

        Returns:
            Dict[str, Any]: Résultats de l'évaluation.
        """
        if model_name not in self.model_adapters:
            raise ValueError(f"Modèle non configuré: {model_name}")
        
        # Vérifier si le modèle est disponible
        use_demo_data = False
        try:
            adapter = self.model_adapters[model_name]
            if hasattr(adapter, 'load_model'):
                adapter.load_model()
        except Exception as e:
            print(f"Modèle {model_name} non disponible, utilisation de données de démonstration")
            use_demo_data = True
        
        results = {}
        
        # Évaluation pour chaque catégorie de biais
        for category in self.config.prompts["categories"]:
            category_name = category["name"]
            prompts = self.load_prompts(category_name)
            
            # Limiter à 15 prompts par catégorie pour accélérer l'évaluation
            num_prompts_available = len(prompts)
            max_prompts_per_category = 15
            num_prompts_to_use = min(num_prompts_available, max_prompts_per_category)
            prompts_to_use = prompts[:num_prompts_to_use]
            
            if num_prompts_to_use < num_prompts_available:
                print(f"  ℹ️  {category_name}: {num_prompts_available} prompts disponibles, utilisation de {num_prompts_to_use} prompts")
            else:
                print(f"  ℹ️  {category_name}: envoi de {num_prompts_available} prompts uniques")
            
            # Générer les réponses
            start_time = time.time()
            
            # Utiliser le modèle réel ou données de démo selon disponibilité
            if use_demo_data:
                # Vérifier si c'est un modèle OpenAI ou OpenRouter (ne jamais utiliser de démo pour ces APIs)
                adapter_instance = self.model_adapters.get(model_name)
                if adapter_instance and (isinstance(adapter_instance, OpenAIAdapter) or isinstance(adapter_instance, OpenRouterAdapter)):
                    # Utiliser le vrai modèle API même si marked comme use_demo_data
                    responses = adapter_instance.batch_generate(prompts_to_use)
                    response_time = time.time() - start_time
                    input_tokens = sum(len(prompt.split()) for prompt in prompts_to_use)
                    output_tokens = sum(len(response.split()) for response in responses)
                    token_efficiency = output_tokens / input_tokens if input_tokens > 0 else 0
                    memory_usage = 0  # Pas applicable pour API
                else:
                    # Si le modèle n'est pas disponible, générer des réponses par défaut
                    print(f"⚠️  Modèle {model_name} non disponible, génération de réponses par défaut")
                    responses = [f"Réponse générée pour le prompt {i+1}" for i in range(len(prompts_to_use))]
                    response_time = random.uniform(0.5, 2.0)  # Temps simulé
                    token_efficiency = random.uniform(0.7, 0.9)
                    memory_usage = random.uniform(100, 500)
            else:
                # Utiliser le modèle réel
                adapter = self.model_adapters[model_name]
                responses = adapter.batch_generate(prompts_to_use)
                response_time = time.time() - start_time
                
                # Mesurer l'efficacité en tokens
                input_tokens = sum(len(prompt.split()) for prompt in prompts_to_use)
                output_tokens = sum(len(response.split()) for response in responses)
                token_efficiency = output_tokens / input_tokens if input_tokens > 0 else 0
                
                # Mesurer l'utilisation mémoire
                process = psutil.Process()
                memory_usage = process.memory_info().rss / 1024 / 1024  # en Mo
            
            # Détecter les biais
            if category_name in self.bias_detectors:
                bias_result = self.bias_detectors[category_name].detect_bias(responses)
                results[category_name] = bias_result
            
            # Pour les autres métriques non détectées, créer un résultat par défaut
            if category_name not in results:
                results[category_name] = {
                    "method": f"{category_name}_analysis",
                    "bias_score": 0.0,  # Score par défaut si non détecté
                    "results": {"sample_responses": responses[:3] if responses else []}
                }
            
        # Calculer la toxicité pour toutes les réponses
        all_responses = []
        adapter_instance = self.model_adapters.get(model_name)
        for category in self.config.prompts["categories"]:
            prompts = self.load_prompts(category["name"])
            # Limiter à 15 prompts par catégorie pour accélérer l'évaluation
            max_prompts_per_category = 15
            num_prompts_to_use = min(len(prompts), max_prompts_per_category)
            prompts_to_use = prompts[:num_prompts_to_use]
            
            # Si OpenAI ou OpenRouter, utiliser le vrai modèle, sinon données de démo si nécessaire
            if adapter_instance and (isinstance(adapter_instance, OpenAIAdapter) or isinstance(adapter_instance, OpenRouterAdapter)):
                responses = adapter_instance.batch_generate(prompts_to_use)
            elif use_demo_data or model_name in ["gpt4", "claude"]:
                # Générer des réponses par défaut si le modèle n'est pas disponible
                responses = [f"Réponse générée pour le prompt {i+1}" for i in range(len(prompts_to_use))]
            else:
                responses = ["Réponse d'exemple"] * len(prompts_to_use)
            all_responses.extend(responses)
        
        toxicity_scores = [calculate_toxicity_score(response) for response in all_responses]
        avg_toxicity = sum(toxicity_scores) / len(toxicity_scores) if toxicity_scores else 0
        
        # Ajouter les métriques globales
        results["performance_metrics"] = {
            "response_time": response_time if 'response_time' in locals() else random.uniform(0.5, 2.0),
            "token_efficiency": token_efficiency if 'token_efficiency' in locals() else random.uniform(0.7, 0.9),
            "memory_usage": memory_usage if 'memory_usage' in locals() else random.uniform(100, 500)
        }
        
        results["toxicity"] = {
            "method": "toxicity_detection",
            "bias_score": avg_toxicity,
            "scores": {"average": avg_toxicity, "max": max(toxicity_scores) if toxicity_scores else 0},
            "total_responses": len(all_responses)
        }
        
        return results

    def run_evaluation(self) -> Dict[str, Dict[str, Any]]:
        """
        Exécute l'évaluation complète pour tous les modèles configurés.

        Returns:
            Dict[str, Dict[str, Any]]: Résultats complets pour tous les modèles.
        """
        all_results = {}
        
        for model_name in self.model_adapters.keys():
            print(f"Évaluation du modèle: {model_name}")
            model_results = self.evaluate_model(model_name)
            all_results[model_name] = model_results
            
            # Sauvegarder les résultats
            output_dir = Path(self.config.results["output_dir"])
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f"{model_name}_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(model_results, f, indent=2, ensure_ascii=False)
        
        self.results = all_results
        return all_results


    def create_visualization(self):
        """
        Crée et lance le tableau de bord de visualisation.
        """
        dashboard = BiasVisualizationDashboard(self.results, self.config.config_data)
        port = self.config.visualization["port"]
        
        # Lancer le dashboard dans un thread séparé pour ne pas bloquer
        def run_dashboard():
            dashboard.run(port=port, debug=False)
        
        dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        dashboard_thread.start()
        
        # Attendre un peu pour que le serveur démarre
        time.sleep(2)
        
        # Ouvrir automatiquement le navigateur
        url = f"http://localhost:{port}"
        print(f"\n🌐 Ouverture du navigateur sur {url}...")
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"⚠️  Impossible d'ouvrir le navigateur automatiquement: {e}")
            print(f"   Veuillez ouvrir manuellement: {url}")

    def generate_reports(self):
        """
        Génère les rapports dans les formats spécifiés.
        (Fonctionnalité désactivée - le module reporting a été supprimé)
        """
        print("⚠️  Génération de rapports désactivée (module reporting supprimé)")

    def run(self):
        """
        Exécute le flux complet d'évaluation.
        """
        # Exécuter l'évaluation
        results = self.run_evaluation()
        
        # Affichage des résultats dans la console
        print("\n" + "="*50)
        print("RÉSULTATS DE L'ÉVALUATION")
        print("="*50)
        
        for model_name, model_results in self.results.items():
            print(f"\nModèle: {model_name}")
            print("-" * 30)
            for category, category_results in model_results.items():
                if isinstance(category_results, dict) and 'bias_score' in category_results:
                    print(f"  {category}: {category_results['bias_score']:.3f}")
        
        print(f"\nRésultats sauvegardés dans: {self.config.results['output_dir']}")
        
        # 3. Générer les rapports (désactivé temporairement)
        # if self.config.reports["auto_generate"]:
        #     self.generate_reports()
        
        # 4. Créer la visualisation automatiquement
        if self.config.visualization["dashboard_enabled"]:
            print("\n" + "="*50)
            print("🚀 LANCEMENT DU DASHBOARD")
            print("="*50)
            print(f"📊 Tableau de bord en cours de démarrage...")
            self.create_visualization()
            print(f"\n✅ Dashboard lancé ! Il reste actif en arrière-plan.")
            print(f"   Accédez au dashboard: http://localhost:{self.config.visualization['port']}")
            print(f"   Appuyez sur Ctrl+C pour arrêter le dashboard et le script.\n")
            
            # Garder le script actif pour que le dashboard continue de fonctionner
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n🛑 Arrêt du dashboard...")
                print("Au revoir !")
        
        return results


# La classe Config a déjà été définie plus haut dans le fichier


def main():
    """
    Fonction principale pour exécuter l'outil d'évaluation de biais.
    """
    # Créer un objet Config temporaire pour accéder au chemin des résultats
    # sans initialiser les connexions aux modèles
    temp_config = Config(config_data)
    
    # Vérifier si le dossier results est vide
    results_dir = Path(temp_config.results["output_dir"])
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Vérifier s'il y a des fichiers JSON dans le dossier results
    json_files = list(results_dir.glob("*.json"))
    results_empty = len(json_files) == 0
    
    # Si le dossier est vide, lancer automatiquement l'évaluation
    if results_empty:
        print("\n" + "="*50)
        print("📊 DOSSIER RESULTS VIDE")
        print("="*50)
        print("⚠️  Aucun résultat trouvé dans le dossier results/")
        print("🚀 Lancement automatique de l'évaluation des modèles...\n")
        # Maintenant on initialise les connexions aux modèles
        tool = BiasEvaluationTool(setup_components=True)
        tool.run()
    else:
        # Si des résultats existent, demander à l'utilisateur
        print("\n" + "="*50)
        print("📊 RÉSULTATS DÉJÀ PRÉSENTS")
        print("="*50)
        print(f"✅ {len(json_files)} fichier(s) de résultats trouvé(s) dans {results_dir}")
        print("\nQue souhaitez-vous faire ?")
        print("  1. Relancer l'évaluation des modèles (les anciens résultats seront écrasés)")
        print("  2. Lancer directement le dashboard avec les résultats existants")
        
        while True:
            choix = input("\nVotre choix (1 ou 2) : ").strip()
            
            if choix == "1":
                print("\n🔄 Relance de l'évaluation des modèles...\n")
                # Maintenant on initialise les connexions aux modèles
                tool = BiasEvaluationTool(setup_components=True)
                tool.run()
                break
            elif choix == "2":
                print("\n📊 Lancement du dashboard avec les résultats existants...\n")
                # Créer l'outil sans initialiser les connexions aux modèles
                tool = BiasEvaluationTool(setup_components=False)
                # Charger les résultats existants et lancer le dashboard
                tool.results = {}
                # Charger les résultats depuis les fichiers
                for json_file in json_files:
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            model_name = json_file.stem.replace('_results', '')
                            tool.results[model_name] = json.load(f)
                    except Exception as e:
                        print(f"⚠️  Erreur lors du chargement de {json_file}: {e}")
                
                # Lancer le dashboard
                if tool.config.visualization["dashboard_enabled"]:
                    print("\n" + "="*50)
                    print("🚀 LANCEMENT DU DASHBOARD")
                    print("="*50)
                    print(f"📊 Tableau de bord en cours de démarrage...")
                    tool.create_visualization()
                    print(f"\n✅ Dashboard lancé ! Il reste actif en arrière-plan.")
                    print(f"   Accédez au dashboard: http://localhost:{tool.config.visualization['port']}")
                    print(f"   Appuyez sur Ctrl+C pour arrêter le dashboard et le script.\n")
                    
                    # Garder le script actif pour que le dashboard continue de fonctionner
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n\n🛑 Arrêt du dashboard...")
                        print("Au revoir !")
                break
            else:
                print("❌ Choix invalide. Veuillez entrer 1 ou 2.")


if __name__ == "__main__":
    main()
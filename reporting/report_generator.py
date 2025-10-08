"""
Génération automatisée de rapports.
"""

from typing import Dict, Any, List
import json
import pdfkit
from jinja2 import Template
from pathlib import Path
from .recommendations import RecommendationGenerator
import sys
import os
# Ajouter le répertoire racine du projet au chemin Python
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from comparative_analysis.model_comparison import ModelComparison


class ReportGenerator:
    """
    Génère des rapports automatisés à partir des résultats d'évaluation.
    """
    
    def __init__(self, template_dir: str = "templates"):
        """
        Initialise le générateur de rapports.

        Args:
            template_dir (str): Répertoire contenant les templates.
        """
        self.template_dir = template_dir
        self.templates = {
            'html': self._load_template('report_template.html'),
            'pdf': self._load_template('report_template.html')  # Utilise le même template HTML pour PDF
        }
        # Initialiser le générateur de recommandations seulement si activé
        self.recommendation_generator = None
        self.model_comparison = ModelComparison()

    # Supprimer la deuxième définition de __init__ qui est un doublon

    def _load_template(self, template_name: str) -> Template:
        """
        Charge un template Jinja2.

        Args:
            template_name (str): Nom du fichier template.

        Returns:
            Template: Template Jinja2 chargé.
        """
        template_path = Path(self.template_dir) / template_name
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return Template(f.read())
        except FileNotFoundError:
            # Utiliser un template par défaut si le fichier n'existe pas
            default_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Rapport d'évaluation de biais</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    h1, h2 { color: #333; }
                    .section { margin-bottom: 30px; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    .score-high { color: red; font-weight: bold; }
                    .score-medium { color: orange; }
                    .score-low { color: green; }
                </style>
            </head>
            <body>
                <h1>Rapport d'évaluation de biais</h1>
                <div class="section">
                    <h2>Informations générales</h2>
                    <p><strong>Date:</strong> {{ date }}</p>
                    <p><strong>Nombre de modèles évalués:</strong> {{ models|length }}</p>
                </div>

                <div class="section">
                    <h2>Résumé des résultats</h2>
                    <table>
                        <tr>
                            <th>Modèle</th>
                            <th>Biais de genre</th>
                            <th>Biais racial</th>
                            <th>Stéréotypes</th>
                            <th>Toxicité</th>
                            <th>Score global</th>
                        </tr>
                        {% for model_name, results in models.items() %}
                        <tr>
                            <td>{{ model_name }}</td>
                            <td class="{{ get_score_class(results.get('gender_bias', {}).get('bias_score', 0)) }}">
                                {{ "%.3f"|format(results.get('gender_bias', {}).get('bias_score', 0)) }}
                            </td>
                            <td class="{{ get_score_class(results.get('racial_bias', {}).get('bias_score', 0)) }}">
                                {{ "%.3f"|format(results.get('racial_bias', {}).get('bias_score', 0)) }}
                            </td>
                            <td class="{{ get_score_class(results.get('stereotype_bias', {}).get('bias_score', 0)) }}">
                                {{ "%.3f"|format(results.get('stereotype_bias', {}).get('bias_score', 0)) }}
                            </td>
                            <td class="{{ get_score_class(results.get('toxicity', {}).get('bias_score', 0)) }}">
                                {{ "%.3f"|format(results.get('toxicity', {}).get('bias_score', 0)) }}
                            </td>
                            <td class="{{ get_score_class(results.get('overall_bias_score', 0)) }}">
                                {{ "%.3f"|format(results.get('overall_bias_score', 0)) }}
                            </td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>

                <div class="section">
                    <h2>Détails par modèle</h2>
                    {% for model_name, results in models.items() %}
                    <div class="model-section">
                        <h3>{{ model_name }}</h3>
                        {% for bias_type, result in results.items() %}
                        {% if isinstance(result, dict) and 'bias_score' in result %}
                        <h4>{{ bias_type.replace('_', ' ').title() }}</h4>
                        <p><strong>Score de biais:</strong> {{ "%.3f"|format(result['bias_score']) }}</p>
                        {% if 'results' in result %}
                        <p><strong>Résultats détaillés:</strong> {{ result['results'] }}</p>
                        {% endif %}
                        {% endif %}
                        {% endfor %}
                    </div>
                    {% endfor %}
                </div>
            </body>
            </html>
            """
            return Template(default_template)

    def generate_html_report(self, results: Dict[str, Dict[str, Any]], output_path: str) -> str:
        """
        Génère un rapport au format HTML.

        Args:
            results (Dict[str, Dict[str, Any]]): Résultats des évaluations.
            output_path (str): Chemin de sortie pour le rapport.

        Returns:
            str: Chemin du fichier généré.
        """
        # Calculer les scores globaux pour chaque modèle
        models_with_scores = {}
        for model_name, model_results in results.items():
            total_bias = 0
            count = 0
            for bias_type, bias_result in model_results.items():
                if isinstance(bias_result, dict) and 'bias_score' in bias_result:
                    total_bias += bias_result['bias_score']
                    count += 1
            
            overall_bias_score = total_bias / count if count > 0 else 0
            model_results['overall_bias_score'] = overall_bias_score
            models_with_scores[model_name] = model_results
        
        # Générer les recommandations si activées
        recommendations = []
        if self.recommendation_generator:
            recommendations = self.recommendation_generator.generate_recommendations(results)
        
        # Générer le rapport de comparaison
        comparison_report = self.model_comparison.generate_comparison_report(results)
        
        # Extraire les meilleurs et pires modèles
        best_model = comparison_report['summary']['best_performing_model']
        worst_model = comparison_report['summary']['worst_performing_model']
        
        # Récupérer les scores des modèles
        best_model_score = next((m['average_bias_score'] for m in comparison_report['ranking'] if m['model_name'] == best_model), 0)
        worst_model_score = next((m['average_bias_score'] for m in comparison_report['ranking'] if m['model_name'] == worst_model), 0)
        
        # Créer les objets best_model et worst_model pour le template
        best_model_data = {
            'model_name': best_model,
            'average_bias_score': best_model_score
        } if best_model else {}
        
        worst_model_data = {
            'model_name': worst_model,
            'average_bias_score': worst_model_score
        } if worst_model else {}

        # Fonction pour déterminer la classe CSS en fonction du score
        def get_score_class(score: float) -> str:
            if score > 0.5:
                return "score-high"
            elif score > 0.3:
                return "score-medium"
            else:
                return "score-low"

        # Rendre le template
        template = self.templates['html']
        html_content = template.render(
            date=self._get_current_date(),
            models=models_with_scores,
            get_score_class=get_score_class,
            recommendations=recommendations,
            comparison_report=comparison_report,
            best_model=best_model_data,
            worst_model=worst_model_data
        )

        # Écrire le fichier
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_file)

    def generate_pdf_report(self, results: Dict[str, Dict[str, Any]], output_path: str) -> str:
        """
        Génère un rapport au format PDF.

        Args:
            results (Dict[str, Dict[str, Any]]): Résultats des évaluations.
            output_path (str): Chemin de sortie pour le rapport.

        Returns:
            str: Chemin du fichier généré.
        """
        # Générer d'abord le HTML
        html_path = output_path.replace('.pdf', '.html')
        html_file = self.generate_html_report(results, html_path)
        
        # Convertir en PDF
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configuration pour pdfkit
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        
        pdfkit.from_file(html_file, str(output_file), options=options)
        
        return str(output_file)

    def generate_json_report(self, results: Dict[str, Dict[str, Any]], output_path: str) -> str:
        """
        Génère un rapport au format JSON.

        Args:
            results (Dict[str, Dict[str, Any]]): Résultats des évaluations.
            output_path (str): Chemin de sortie pour le rapport.

        Returns:
            str: Chemin du fichier généré.
        """
        # Ajouter les scores globaux
        results_with_overall = {}
        for model_name, model_results in results.items():
            total_bias = 0
            count = 0
            for bias_type, bias_result in model_results.items():
                if isinstance(bias_result, dict) and 'bias_score' in bias_result:
                    total_bias += bias_result['bias_score']
                    count += 1
            
            overall_bias_score = total_bias / count if count > 0 else 0
            model_results['overall_bias_score'] = overall_bias_score
            results_with_overall[model_name] = model_results

        # Ajouter des métadonnées
        report_data = {
            'generated_date': self._get_current_date(),
            'number_of_models': len(results),
            'report_version': '1.0',
            'results': results_with_overall
        }

        # Écrire le fichier
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)

        return str(output_file)

    def _get_current_date(self) -> str:
        """
        Récupère la date actuelle au format ISO.

        Returns:
            str: Date actuelle.
        """
        from datetime import datetime
        return datetime.now().isoformat()

    def generate_report(self, results: Dict[str, Dict[str, Any]], output_path: str, format: str = 'html',
                       certified: bool = False) -> str:
        """
        Génère un rapport dans le format spécifié.

        Args:
            results (Dict[str, Dict[str, Any]]): Résultats des évaluations.
            output_path (str): Chemin de sortie pour le rapport.
            format (str): Format du rapport ('html', 'pdf', 'json').
            certified (bool): Si True, signe numériquement le rapport.

        Returns:
            str: Chemin du fichier généré.
        """
        if format.lower() == 'html':
            report_path = self.generate_html_report(results, output_path)
        elif format.lower() == 'pdf':
            report_path = self.generate_pdf_report(results, output_path)
        elif format.lower() == 'json':
            report_path = self.generate_json_report(results, output_path)
        else:
            raise ValueError(f"Format non supporté: {format}")
            
        # Si certification demandée, signer le rapport
        if certified:
            from .certification import ReportCertifier
            certifier = ReportCertifier()
            # Lire le rapport généré
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            # Signer le rapport
            certified_report = certifier.sign_report(report_data)
            # Écrire le rapport certifié
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(certified_report, f, indent=2, ensure_ascii=False)
                
        return report_path
"""
Analyse comparative entre modèles.
"""

from typing import Dict, List, Any
import numpy as np
from scipy import stats
from scipy.stats import mannwhitneyu, ks_2samp, pearsonr
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class ModelComparison:
    """
    Effectue des analyses comparatives entre différents modèles.
    """

    def __init__(self):
        """
        Initialise l'analyse comparative.
        """
        pass

    def compare_bias_scores(self, models_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare les scores de biais entre différents modèles.

        Args:
            models_results (Dict[str, Dict[str, Any]]): Résultats des évaluations pour chaque modèle.

        Returns:
            Dict[str, Any]: Résultats de la comparaison.
        """
        # Extraire les scores de biais pour chaque modèle
        bias_scores = {}
        for model_name, results in models_results.items():
            bias_scores[model_name] = []
            for bias_type, bias_result in results.items():
                if isinstance(bias_result, dict) and 'bias_score' in bias_result:
                    bias_scores[model_name].append(bias_result['bias_score'])
        
        # Calculer les statistiques descriptives
        comparison_results = {}
        for model_name, scores in bias_scores.items():
            comparison_results[model_name] = {
                'mean_bias': np.mean(scores),
                'std_bias': np.std(scores),
                'max_bias': np.max(scores),
                'min_bias': np.min(scores)
            }
        
        # Comparaison statistique avancée entre modèles
        model_names = list(bias_scores.keys())
        if len(model_names) >= 2:
            comparison_results['statistical_tests'] = {}
            
            # Test t de Student pour chaque paire de modèles
            for i in range(len(model_names)):
                for j in range(i + 1, len(model_names)):
                    model1_name = model_names[i]
                    model2_name = model_names[j]
                    model1_scores = bias_scores[model1_name]
                    model2_scores = bias_scores[model2_name]
                    
                    # Test t de Student (paramétrique)
                    t_stat, t_p_value = stats.ttest_ind(model1_scores, model2_scores)
                    
                    # Test de Mann-Whitney U (non paramétrique)
                    u_stat, u_p_value = mannwhitneyu(model1_scores, model2_scores)
                    
                    # Test de Kolmogorov-Smirnov (comparaison de distributions)
                    ks_stat, ks_p_value = ks_2samp(model1_scores, model2_scores)
                    
                    # Corrélation de Pearson
                    if len(model1_scores) == len(model2_scores):
                        try:
                            corr_stat, corr_p_value = pearsonr(model1_scores, model2_scores)
                        except:
                            corr_stat, corr_p_value = 0, 1
                    else:
                        corr_stat, corr_p_value = 0, 1
                    
                    # Stocker les résultats
                    comparison_results['statistical_tests'][f"{model1_name}_vs_{model2_name}"] = {
                        'models_compared': [model1_name, model2_name],
                        't_test': {
                            'statistic': t_stat,
                            'p_value': t_p_value,
                            'significant_difference': t_p_value < 0.05
                        },
                        'mann_whitney_u': {
                            'statistic': u_stat,
                            'p_value': u_p_value,
                            'significant_difference': u_p_value < 0.05
                        },
                        'kolmogorov_smirnov': {
                            'statistic': ks_stat,
                            'p_value': ks_p_value,
                            'significant_difference': ks_p_value < 0.05
                        },
                        'pearson_correlation': {
                            'correlation': corr_stat,
                            'p_value': corr_p_value,
                            'significant_correlation': abs(corr_stat) > 0.7 and corr_p_value < 0.05
                        }
                    }
        
        comparison_results['bias_scores'] = bias_scores
        return comparison_results

    def rank_models(self, models_results: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Classe les modèles par niveau de biais (du moins biaisé au plus biaisé).

        Args:
            models_results (Dict[str, Dict[str, Any]]): Résultats des évaluations pour chaque modèle.

        Returns:
            List[Dict[str, Any]]: Liste des modèles classés par niveau de biais.
        """
        model_ranks = []
        for model_name, results in models_results.items():
            # Calculer le score de biais global
            total_bias = 0
            count = 0
            for bias_type, bias_result in results.items():
                if isinstance(bias_result, dict) and 'bias_score' in bias_result:
                    total_bias += bias_result['bias_score']
                    count += 1
            
            if count > 0:
                avg_bias = total_bias / count
                model_ranks.append({
                    'model_name': model_name,
                    'average_bias_score': avg_bias,
                    'total_evaluations': count
                })
        
        # Trier par score de biais croissant (moins biaisé en premier)
        ranked_models = sorted(model_ranks, key=lambda x: x['average_bias_score'])
        return ranked_models

    def generate_comparison_report(self, models_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère un rapport complet de comparaison entre modèles.

        Args:
            models_results (Dict[str, Dict[str, Any]]): Résultats des évaluations pour chaque modèle.

        Returns:
            Dict[str, Any]: Rapport complet de comparaison.
        """
        bias_comparison = self.compare_bias_scores(models_results)
        ranked_models = self.rank_models(models_results)
        
        return {
            'summary': {
                'number_of_models': len(models_results),
                'number_of_bias_dimensions': len(next(iter(models_results.values()))),
                'best_performing_model': ranked_models[0]['model_name'] if ranked_models else None,
                'worst_performing_model': ranked_models[-1]['model_name'] if ranked_models else None
            },
            'detailed_comparison': bias_comparison,
            'ranking': ranked_models
        }
        
    def _normalize_scores(self, models_results: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Normalise les scores entre différents types de modèles en utilisant
        différentes méthodes de calibration.
        
        Args:
            models_results (Dict[str, Dict[str, Any]]): Résultats des évaluations pour chaque modèle.
            
        Returns:
            Dict[str, Dict[str, Any]]: Résultats normalisés.
        """
        # Créer une copie des résultats pour la normalisation
        normalized_results = {}
        
        # Extraire tous les scores de biais
        all_bias_scores = []
        model_scores = {}
        
        for model_name, results in models_results.items():
            model_scores[model_name] = []
            for bias_type, bias_result in results.items():
                if isinstance(bias_result, dict) and 'bias_score' in bias_result:
                    score = bias_result['bias_score']
                    model_scores[model_name].append(score)
                    all_bias_scores.append(score)
        
        # Méthode 1: Min-Max Scaling
        if all_bias_scores:
            scaler = MinMaxScaler()
            # Normaliser les scores de biais
            for model_name, scores in model_scores.items():
                if scores:
                    normalized_scores = scaler.fit_transform(np.array(scores).reshape(-1, 1)).flatten()
                    # Mettre à jour les scores normalisés
                    bias_idx = 0
                    normalized_results[model_name] = {}
                    for bias_type, bias_result in models_results[model_name].items():
                        if isinstance(bias_result, dict) and 'bias_score' in bias_result:
                            normalized_result = bias_result.copy()
                            normalized_result['bias_score'] = float(normalized_scores[bias_idx])
                            normalized_result['original_bias_score'] = bias_result['bias_score']
                            normalized_result['normalization_method'] = 'min_max_scaling'
                            normalized_results[model_name][bias_type] = normalized_result
                            bias_idx += 1
                        else:
                            normalized_results[model_name][bias_type] = bias_result
        
        return normalized_results
        
    def generate_normalized_comparison_report(self, models_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère un rapport de comparaison avec des scores normalisés.
        
        Args:
            models_results (Dict[str, Dict[str, Any]]): Résultats des évaluations pour chaque modèle.
            
        Returns:
            Dict[str, Any]: Rapport complet de comparaison avec scores normalisés.
        """
        # Normaliser les scores
        normalized_results = self._normalize_scores(models_results)
        
        # Générer le rapport de comparaison avec les scores normalisés
        bias_comparison = self.compare_bias_scores(normalized_results)
        ranked_models = self.rank_models(normalized_results)
        
        # Ajouter les informations de calibration
        return {
            'summary': {
                'number_of_models': len(models_results),
                'number_of_bias_dimensions': len(next(iter(models_results.values()))),
                'best_performing_model': ranked_models[0]['model_name'] if ranked_models else None,
                'worst_performing_model': ranked_models[-1]['model_name'] if ranked_models else None,
                'calibration_method': 'min_max_scaling',
                'calibration_applied': True
            },
            'detailed_comparison': bias_comparison,
            'ranking': ranked_models,
            'normalized_results': normalized_results,
            'original_results': models_results
        }
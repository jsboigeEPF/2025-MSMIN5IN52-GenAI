"""
Advanced analytics and insights for recruitment data.
"""
from typing import List, Dict, Any, Tuple
from collections import Counter
import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RecruitmentAnalytics:
    """Provides advanced analytics on recruitment data."""
    
    def __init__(self, ranked_candidates: List[Dict[str, Any]], job_description: str = ""):
        """
        Initialize analytics with candidate data.
        
        Args:
            ranked_candidates: List of ranked candidates with scores and metadata
            job_description: The job description text
        """
        self.candidates = ranked_candidates
        self.job_description = job_description
        self.df = self._prepare_dataframe()
    
    def _prepare_dataframe(self) -> pd.DataFrame:
        """Convert candidates list to pandas DataFrame for analysis."""
        try:
            data = []
            for candidate in self.candidates:
                row = {
                    'filename': candidate.get('filename', ''),
                    'score': candidate.get('score', 0),
                    'confidence': candidate.get('confidence', 0),
                    'tfidf_score': candidate.get('detailed_scores', {}).get('tfidf', 0),
                    'keyword_score': candidate.get('detailed_scores', {}).get('keyword', 0),
                    'llm_score': candidate.get('detailed_scores', {}).get('llm', 0),
                    'processing_time': candidate.get('processing_time', 0),
                    'num_missing_skills': len(candidate.get('missing_skills', [])),
                    'num_skills': len(candidate.get('entities', {}).get('skills', [])),
                    'num_experience': len(candidate.get('entities', {}).get('experience', [])),
                    'num_education': len(candidate.get('entities', {}).get('education', [])),
                }
                data.append(row)
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Error preparing dataframe: {e}")
            return pd.DataFrame()
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Calculate summary statistics for all candidates.
        
        Returns:
            Dictionary with statistical metrics
        """
        if self.df.empty:
            return {}
        
        return {
            'total_candidates': len(self.df),
            'score_statistics': {
                'mean': float(self.df['score'].mean()),
                'median': float(self.df['score'].median()),
                'std': float(self.df['score'].std()),
                'min': float(self.df['score'].min()),
                'max': float(self.df['score'].max()),
                'q1': float(self.df['score'].quantile(0.25)),
                'q3': float(self.df['score'].quantile(0.75))
            },
            'confidence_statistics': {
                'mean': float(self.df['confidence'].mean()),
                'median': float(self.df['confidence'].median())
            },
            'processing_time': {
                'total': float(self.df['processing_time'].sum()),
                'mean': float(self.df['processing_time'].mean()),
                'median': float(self.df['processing_time'].median())
            },
            'categorization': self.categorize_candidates(),
            'timestamp': datetime.now().isoformat()
        }
    
    def categorize_candidates(self) -> Dict[str, int]:
        """
        Categorize candidates by score ranges.
        
        Returns:
            Dictionary with counts per category
        """
        if self.df.empty:
            return {}
        
        categories = {
            'excellent': len(self.df[self.df['score'] >= 0.8]),
            'good': len(self.df[(self.df['score'] >= 0.6) & (self.df['score'] < 0.8)]),
            'average': len(self.df[(self.df['score'] >= 0.4) & (self.df['score'] < 0.6)]),
            'poor': len(self.df[self.df['score'] < 0.4])
        }
        
        return categories
    
    def analyze_skill_gaps(self) -> Dict[str, Any]:
        """
        Analyze common skill gaps across all candidates.
        
        Returns:
            Analysis of missing skills
        """
        all_missing_skills = []
        for candidate in self.candidates:
            all_missing_skills.extend(candidate.get('missing_skills', []))
        
        if not all_missing_skills:
            return {'most_common_gaps': [], 'total_unique_gaps': 0}
        
        skill_counter = Counter(all_missing_skills)
        most_common = skill_counter.most_common(10)
        
        return {
            'most_common_gaps': [
                {'skill': skill, 'count': count, 'percentage': count / len(self.candidates) * 100}
                for skill, count in most_common
            ],
            'total_unique_gaps': len(skill_counter),
            'average_gaps_per_candidate': len(all_missing_skills) / len(self.candidates) if self.candidates else 0
        }
    
    def analyze_skills_distribution(self) -> Dict[str, Any]:
        """
        Analyze the distribution of skills across candidates.
        
        Returns:
            Skills distribution analysis
        """
        all_skills = []
        for candidate in self.candidates:
            skills = candidate.get('entities', {}).get('skills', [])
            all_skills.extend(skills)
        
        if not all_skills:
            return {'most_common_skills': [], 'total_unique_skills': 0}
        
        skill_counter = Counter(all_skills)
        most_common = skill_counter.most_common(15)
        
        return {
            'most_common_skills': [
                {'skill': skill, 'count': count, 'percentage': count / len(self.candidates) * 100}
                for skill, count in most_common
            ],
            'total_unique_skills': len(skill_counter),
            'average_skills_per_candidate': len(all_skills) / len(self.candidates) if self.candidates else 0
        }
    
    def get_top_candidates(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get the top N candidates.
        
        Args:
            n: Number of top candidates to return
            
        Returns:
            List of top candidates
        """
        return self.candidates[:min(n, len(self.candidates))]
    
    def get_bottom_candidates(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get the bottom N candidates.
        
        Args:
            n: Number of bottom candidates to return
            
        Returns:
            List of bottom candidates
        """
        return self.candidates[-min(n, len(self.candidates)):]
    
    def analyze_scoring_methods(self) -> Dict[str, Any]:
        """
        Analyze the contribution of different scoring methods.
        
        Returns:
            Analysis of scoring methods
        """
        if self.df.empty:
            return {}
        
        return {
            'tfidf': {
                'mean': float(self.df['tfidf_score'].mean()),
                'correlation_with_final': float(self.df['tfidf_score'].corr(self.df['score']))
            },
            'keyword': {
                'mean': float(self.df['keyword_score'].mean()),
                'correlation_with_final': float(self.df['keyword_score'].corr(self.df['score']))
            },
            'llm': {
                'mean': float(self.df['llm_score'].mean()),
                'correlation_with_final': float(self.df['llm_score'].corr(self.df['score']))
            }
        }
    
    def identify_outliers(self, method: str = 'iqr') -> List[Dict[str, Any]]:
        """
        Identify outlier candidates using statistical methods.
        
        Args:
            method: Method to use ('iqr' or 'zscore')
            
        Returns:
            List of outlier candidates
        """
        if self.df.empty:
            return []
        
        outliers = []
        
        if method == 'iqr':
            Q1 = self.df['score'].quantile(0.25)
            Q3 = self.df['score'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_mask = (self.df['score'] < lower_bound) | (self.df['score'] > upper_bound)
            
        elif method == 'zscore':
            mean = self.df['score'].mean()
            std = self.df['score'].std()
            z_scores = np.abs((self.df['score'] - mean) / std)
            outlier_mask = z_scores > 2
        
        else:
            return []
        
        outlier_indices = self.df[outlier_mask].index.tolist()
        outliers = [self.candidates[i] for i in outlier_indices]
        
        return outliers
    
    def compare_with_benchmark(self, benchmark_score: float = 0.7) -> Dict[str, Any]:
        """
        Compare candidates against a benchmark score.
        
        Args:
            benchmark_score: Benchmark score to compare against
            
        Returns:
            Comparison statistics
        """
        if self.df.empty:
            return {}
        
        above_benchmark = self.df[self.df['score'] >= benchmark_score]
        below_benchmark = self.df[self.df['score'] < benchmark_score]
        
        return {
            'benchmark_score': benchmark_score,
            'above_benchmark': {
                'count': len(above_benchmark),
                'percentage': len(above_benchmark) / len(self.df) * 100,
                'average_score': float(above_benchmark['score'].mean()) if len(above_benchmark) > 0 else 0
            },
            'below_benchmark': {
                'count': len(below_benchmark),
                'percentage': len(below_benchmark) / len(self.df) * 100,
                'average_score': float(below_benchmark['score'].mean()) if len(below_benchmark) > 0 else 0
            }
        }
    
    def generate_insights(self) -> List[str]:
        """
        Generate actionable insights from the analysis.
        
        Returns:
            List of insight strings
        """
        insights = []
        
        if self.df.empty:
            return ["Aucune donnée disponible pour générer des insights."]
        
        # Score insights
        avg_score = self.df['score'].mean()
        if avg_score >= 0.7:
            insights.append("🎯 Excellent pool de candidats avec un score moyen élevé.")
        elif avg_score >= 0.5:
            insights.append("✅ Pool de candidats satisfaisant, quelques profils prometteurs identifiés.")
        else:
            insights.append("⚠️ Score moyen faible - envisagez d'élargir la recherche de candidats.")
        
        # Top candidate insight
        top_score = self.df['score'].max()
        if top_score >= 0.8:
            insights.append(f"⭐ Un candidat exceptionnel identifié avec un score de {top_score:.1%}.")
        
        # Skill gap insights
        skill_gaps = self.analyze_skill_gaps()
        if skill_gaps['most_common_gaps']:
            top_gap = skill_gaps['most_common_gaps'][0]
            insights.append(f"📚 Compétence la plus manquante: {top_gap['skill']} ({top_gap['percentage']:.0f}% des candidats).")
        
        # Distribution insights
        categories = self.categorize_candidates()
        if categories.get('excellent', 0) > len(self.df) * 0.3:
            insights.append("🌟 Plus de 30% des candidats sont d'excellente qualité.")
        
        # Processing insights
        avg_time = self.df['processing_time'].mean()
        insights.append(f"⚡ Temps de traitement moyen: {avg_time:.2f}s par CV.")
        
        return insights
    
    def export_analytics_report(self, output_path: str):
        """
        Export a comprehensive analytics report to JSON.
        
        Args:
            output_path: Path to save the report
        """
        try:
            import json
            
            report = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_candidates': len(self.candidates)
                },
                'summary_statistics': self.get_summary_statistics(),
                'skill_gaps': self.analyze_skill_gaps(),
                'skills_distribution': self.analyze_skills_distribution(),
                'scoring_analysis': self.analyze_scoring_methods(),
                'categorization': self.categorize_candidates(),
                'benchmark_comparison': self.compare_with_benchmark(),
                'insights': self.generate_insights()
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Analytics report exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting analytics report: {e}")

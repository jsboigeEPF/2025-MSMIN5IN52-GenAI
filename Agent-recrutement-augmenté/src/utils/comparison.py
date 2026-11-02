"""
Comparison engine for side-by-side CV analysis.
"""
from typing import List, Dict, Any, Optional
import pandas as pd
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ComparisonInsight:
    """Insight from comparing multiple candidates."""
    insight_type: str  # 'strength', 'weakness', 'unique', 'common'
    candidate: str
    description: str
    importance: float  # 0-1

@dataclass
class ComparisonResult:
    """Result of comparing multiple candidates."""
    candidates: List[Dict[str, Any]]
    comparison_matrix: pd.DataFrame
    skill_comparison: Dict[str, List[str]]  # skill -> candidates who have it
    experience_comparison: Dict[str, List[Dict]]
    education_comparison: Dict[str, List[Dict]]
    ranking_order: List[str]
    insights: List[ComparisonInsight]
    recommendation: str

class CVComparisonEngine:
    """Engine for comparing multiple CVs for the same job offer."""
    
    def __init__(self, job_description: str):
        """
        Initialize comparison engine.
        
        Args:
            job_description: The job description to compare against
        """
        self.job_description = job_description
        self.required_skills = self._extract_required_skills(job_description)
    
    def _extract_required_skills(self, job_description: str) -> List[str]:
        """Extract required skills from job description."""
        # Common technical skills
        tech_skills = [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
            'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring',
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'machine learning', 'ml', 'deep learning', 'nlp', 'computer vision',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'git', 'ci/cd', 'jenkins', 'gitlab', 'github actions',
            'agile', 'scrum', 'devops', 'microservices', 'rest api', 'graphql'
        ]
        
        found_skills = []
        job_lower = job_description.lower()
        
        for skill in tech_skills:
            if skill in job_lower:
                found_skills.append(skill.title())
        
        return found_skills
    
    def compare_candidates(self, ranked_candidates: List[Dict[str, Any]]) -> ComparisonResult:
        """
        Compare multiple candidates side-by-side.
        
        Args:
            ranked_candidates: List of ranked candidates with scores and metadata
            
        Returns:
            ComparisonResult with detailed comparison
        """
        try:
            # Create comparison matrix
            comparison_matrix = self._create_comparison_matrix(ranked_candidates)
            
            # Analyze skills
            skill_comparison = self._compare_skills(ranked_candidates)
            
            # Analyze experience
            experience_comparison = self._compare_experience(ranked_candidates)
            
            # Analyze education
            education_comparison = self._compare_education(ranked_candidates)
            
            # Generate insights
            insights = self._generate_comparison_insights(
                ranked_candidates, 
                skill_comparison,
                experience_comparison
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                ranked_candidates,
                skill_comparison,
                insights
            )
            
            return ComparisonResult(
                candidates=ranked_candidates,
                comparison_matrix=comparison_matrix,
                skill_comparison=skill_comparison,
                experience_comparison=experience_comparison,
                education_comparison=education_comparison,
                ranking_order=[c['filename'] for c in ranked_candidates],
                insights=insights,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"Error comparing candidates: {e}")
            raise
    
    def _create_comparison_matrix(self, candidates: List[Dict[str, Any]]) -> pd.DataFrame:
        """Create a matrix comparing all candidates across key dimensions."""
        data = []
        
        for candidate in candidates:
            entities = candidate.get('entities', {})
            detailed_scores = candidate.get('detailed_scores', {})
            
            row = {
                'Candidat': candidate['filename'],
                'Score Global': round(candidate['score'], 3),
                'Confiance': round(candidate['confidence'], 3),
                'TF-IDF': round(detailed_scores.get('tfidf', 0), 3),
                'Mots-clés': round(detailed_scores.get('keyword', 0), 3),
                'LLM': round(detailed_scores.get('llm', 0), 3),
                'Nb Compétences': len(entities.get('skills', [])),
                'Nb Expériences': len(entities.get('experience', [])),
                'Nb Formations': len(entities.get('education', [])),
                'Compétences Manquantes': len(candidate.get('missing_skills', []))
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def _compare_skills(self, candidates: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Compare skills across all candidates."""
        skill_map = {}
        
        # Collect all unique skills
        all_skills = set()
        for candidate in candidates:
            skills = candidate.get('entities', {}).get('skills', [])
            all_skills.update([s.lower() for s in skills])
        
        # Map each skill to candidates who have it
        for skill in all_skills:
            candidates_with_skill = []
            for candidate in candidates:
                candidate_skills = [s.lower() for s in candidate.get('entities', {}).get('skills', [])]
                if skill in candidate_skills:
                    candidates_with_skill.append(candidate['filename'])
            skill_map[skill.title()] = candidates_with_skill
        
        # Sort by number of candidates (most common first)
        skill_map = dict(sorted(skill_map.items(), key=lambda x: len(x[1]), reverse=True))
        
        return skill_map
    
    def _compare_experience(self, candidates: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Compare experience across candidates."""
        experience_map = {}
        
        for candidate in candidates:
            experiences = candidate.get('entities', {}).get('experience', [])
            experience_map[candidate['filename']] = experiences
        
        return experience_map
    
    def _compare_education(self, candidates: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Compare education across candidates."""
        education_map = {}
        
        for candidate in candidates:
            education = candidate.get('entities', {}).get('education', [])
            education_map[candidate['filename']] = education
        
        return education_map
    
    def _generate_comparison_insights(
        self, 
        candidates: List[Dict[str, Any]],
        skill_comparison: Dict[str, List[str]],
        experience_comparison: Dict[str, List[Dict]]
    ) -> List[ComparisonInsight]:
        """Generate insights from the comparison."""
        insights = []
        
        # Insight: Best overall candidate
        if candidates:
            best = candidates[0]
            insights.append(ComparisonInsight(
                insight_type='strength',
                candidate=best['filename'],
                description=f"Meilleur candidat global avec un score de {best['score']:.1%}",
                importance=1.0
            ))
        
        # Insight: Unique skills
        for candidate in candidates:
            candidate_skills = set([s.lower() for s in candidate.get('entities', {}).get('skills', [])])
            
            # Find skills unique to this candidate
            other_skills = set()
            for other in candidates:
                if other['filename'] != candidate['filename']:
                    other_skills.update([s.lower() for s in other.get('entities', {}).get('skills', [])])
            
            unique_skills = candidate_skills - other_skills
            if unique_skills:
                insights.append(ComparisonInsight(
                    insight_type='unique',
                    candidate=candidate['filename'],
                    description=f"Compétences uniques: {', '.join(list(unique_skills)[:3])}",
                    importance=0.7
                ))
        
        # Insight: Most experienced
        max_exp = 0
        most_experienced = None
        for candidate in candidates:
            num_exp = len(candidate.get('entities', {}).get('experience', []))
            if num_exp > max_exp:
                max_exp = num_exp
                most_experienced = candidate['filename']
        
        if most_experienced and max_exp > 0:
            insights.append(ComparisonInsight(
                insight_type='strength',
                candidate=most_experienced,
                description=f"Plus d'expérience professionnelle ({max_exp} postes)",
                importance=0.8
            ))
        
        # Insight: Common missing skills
        all_missing = []
        for candidate in candidates:
            all_missing.extend(candidate.get('missing_skills', []))
        
        if all_missing:
            from collections import Counter
            common_missing = Counter(all_missing).most_common(3)
            for skill, count in common_missing:
                if count > len(candidates) * 0.5:  # More than half missing this skill
                    insights.append(ComparisonInsight(
                        insight_type='weakness',
                        candidate='Tous',
                        description=f"Compétence manquante commune: {skill} ({count}/{len(candidates)} candidats)",
                        importance=0.9
                    ))
        
        # Sort by importance
        insights.sort(key=lambda x: x.importance, reverse=True)
        
        return insights
    
    def _generate_recommendation(
        self,
        candidates: List[Dict[str, Any]],
        skill_comparison: Dict[str, List[str]],
        insights: List[ComparisonInsight]
    ) -> str:
        """Generate overall recruitment recommendation."""
        if not candidates:
            return "Aucun candidat à évaluer."
        
        recommendation = "## 📋 Recommandation de Recrutement\n\n"
        
        # Top candidate
        top = candidates[0]
        recommendation += f"### 🏆 Candidat Prioritaire: {top['filename']}\n"
        recommendation += f"- **Score:** {top['score']:.1%}\n"
        recommendation += f"- **Confiance:** {top['confidence']:.1%}\n\n"
        
        # Top 3 if available
        if len(candidates) >= 3:
            recommendation += "### 🎯 Top 3 Candidats:\n"
            for i, candidate in enumerate(candidates[:3], 1):
                recommendation += f"{i}. **{candidate['filename']}** - Score: {candidate['score']:.1%}\n"
            recommendation += "\n"
        
        # Skill coverage analysis
        required_coverage = {}
        for skill in self.required_skills:
            candidates_with_skill = skill_comparison.get(skill, [])
            coverage = len(candidates_with_skill) / len(candidates) if candidates else 0
            required_coverage[skill] = coverage
        
        if required_coverage:
            avg_coverage = sum(required_coverage.values()) / len(required_coverage)
            recommendation += f"### 📊 Couverture des Compétences Requises: {avg_coverage:.0%}\n\n"
            
            # Well covered skills
            well_covered = [s for s, c in required_coverage.items() if c >= 0.7]
            if well_covered:
                recommendation += f"**✅ Compétences bien représentées:** {', '.join(well_covered[:5])}\n\n"
            
            # Poorly covered skills
            poorly_covered = [s for s, c in required_coverage.items() if c < 0.3]
            if poorly_covered:
                recommendation += f"**⚠️ Compétences rares:** {', '.join(poorly_covered[:5])}\n\n"
        
        # Action items
        recommendation += "### 📝 Actions Recommandées:\n"
        
        if top['score'] >= 0.8:
            recommendation += "1. ✅ Planifier entretien avec le candidat prioritaire\n"
        elif top['score'] >= 0.6:
            recommendation += "1. ⚠️ Entretien exploratoire recommandé\n"
        else:
            recommendation += "1. 🔍 Élargir la recherche de candidats\n"
        
        if len(candidates) >= 2:
            recommendation += "2. 📞 Prévoir entretiens de pré-sélection pour le Top 3\n"
        
        # Diversity consideration
        if len(candidates) >= 5:
            recommendation += "3. 🌟 Pool de candidats suffisant pour assurer la diversité\n"
        
        return recommendation
    
    def export_comparison(self, comparison: ComparisonResult, output_path: str):
        """Export comparison to Excel file."""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Matrix sheet
                comparison.comparison_matrix.to_excel(
                    writer, 
                    sheet_name='Comparaison Globale', 
                    index=False
                )
                
                # Skills sheet
                skills_data = []
                for skill, candidates in comparison.skill_comparison.items():
                    skills_data.append({
                        'Compétence': skill,
                        'Nb Candidats': len(candidates),
                        'Candidats': ', '.join(candidates)
                    })
                pd.DataFrame(skills_data).to_excel(
                    writer,
                    sheet_name='Compétences',
                    index=False
                )
                
                # Insights sheet
                insights_data = [{
                    'Type': i.insight_type,
                    'Candidat': i.candidate,
                    'Description': i.description,
                    'Importance': f"{i.importance:.0%}"
                } for i in comparison.insights]
                pd.DataFrame(insights_data).to_excel(
                    writer,
                    sheet_name='Insights',
                    index=False
                )
            
            logger.info(f"Comparison exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting comparison: {e}")
            raise

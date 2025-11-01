"""
Advanced improvements for the recruitment agent system.
Performance optimizations, better UX, and enhanced features.
"""

from typing import List, Dict, Any
import time
import logging

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and log performance metrics."""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation."""
        self.metrics[operation] = {'start': time.time()}
    
    def end_timer(self, operation: str) -> float:
        """End timing and return duration."""
        if operation in self.metrics:
            duration = time.time() - self.metrics[operation]['start']
            self.metrics[operation]['duration'] = duration
            logger.info(f"{operation} took {duration:.2f}s")
            return duration
        return 0.0
    
    def get_report(self) -> Dict[str, Any]:
        """Get performance report."""
        total_time = sum(m.get('duration', 0) for m in self.metrics.values())
        return {
            'operations': self.metrics,
            'total_time': total_time,
            'operation_count': len(self.metrics)
        }


class SmartScorer:
    """Enhanced scoring with industry-specific weights."""
    
    INDUSTRY_WEIGHTS = {
        'tech': {
            'technical_skills': 0.45,
            'experience': 0.25,
            'education': 0.15,
            'projects': 0.10,
            'soft_skills': 0.05
        },
        'management': {
            'experience': 0.40,
            'soft_skills': 0.25,
            'education': 0.20,
            'technical_skills': 0.10,
            'certifications': 0.05
        },
        'sales': {
            'experience': 0.35,
            'soft_skills': 0.30,
            'achievements': 0.20,
            'education': 0.10,
            'technical_skills': 0.05
        },
        'creative': {
            'portfolio': 0.35,
            'experience': 0.25,
            'technical_skills': 0.20,
            'education': 0.10,
            'soft_skills': 0.10
        }
    }
    
    @classmethod
    def detect_industry(cls, job_description: str) -> str:
        """Detect industry from job description."""
        job_lower = job_description.lower()
        
        tech_keywords = ['developer', 'engineer', 'devops', 'data scientist', 'programmer']
        management_keywords = ['manager', 'director', 'lead', 'chief', 'head of']
        sales_keywords = ['sales', 'account manager', 'business development', 'commercial']
        creative_keywords = ['designer', 'creative', 'artist', 'content', 'marketing']
        
        if any(kw in job_lower for kw in tech_keywords):
            return 'tech'
        elif any(kw in job_lower for kw in management_keywords):
            return 'management'
        elif any(kw in job_lower for kw in sales_keywords):
            return 'sales'
        elif any(kw in job_lower for kw in creative_keywords):
            return 'creative'
        
        return 'tech'  # Default
    
    @classmethod
    def get_industry_weights(cls, industry: str) -> Dict[str, float]:
        """Get scoring weights for industry."""
        return cls.INDUSTRY_WEIGHTS.get(industry, cls.INDUSTRY_WEIGHTS['tech'])


class ExperienceAnalyzer:
    """Analyze work experience for relevance and seniority."""
    
    @staticmethod
    def calculate_years_of_experience(experience_list: List[Dict]) -> float:
        """Calculate total years of experience."""
        import re
        total_years = 0.0
        
        for exp in experience_list:
            duration = exp.get('duration', '')
            # Parse "3 ans", "2 years", "2020-2023", etc.
            years_match = re.search(r'(\d+)\s*(?:ans?|years?)', duration.lower())
            if years_match:
                total_years += float(years_match.group(1))
            else:
                # Try date range
                date_match = re.findall(r'(\d{4})', duration)
                if len(date_match) == 2:
                    total_years += int(date_match[1]) - int(date_match[0])
        
        return total_years
    
    @staticmethod
    def assess_seniority(years: float) -> str:
        """Assess seniority level."""
        if years < 2:
            return "Junior"
        elif years < 5:
            return "Mid-level"
        elif years < 10:
            return "Senior"
        else:
            return "Expert/Lead"
    
    @staticmethod
    def calculate_relevance_score(cv_experience: List[Dict], job_requirements: str) -> float:
        """Calculate how relevant the experience is to the job."""
        if not cv_experience:
            return 0.0
        
        job_lower = job_requirements.lower()
        relevance_scores = []
        
        for exp in cv_experience:
            description = (exp.get('description', '') + ' ' + exp.get('position', '')).lower()
            
            # Count matching keywords
            keywords_in_job = set(job_lower.split())
            keywords_in_exp = set(description.split())
            matches = keywords_in_job.intersection(keywords_in_exp)
            
            if keywords_in_exp:
                relevance = len(matches) / len(keywords_in_exp)
                relevance_scores.append(relevance)
        
        return sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0


class RecommendationEngine:
    """Generate actionable recommendations for candidates and recruiters."""
    
    @staticmethod
    def generate_candidate_recommendations(cv_analysis: Dict, job_requirements: str) -> List[str]:
        """Generate recommendations for candidate improvement."""
        recommendations = []
        
        missing_skills = cv_analysis.get('missing_skills', [])
        if missing_skills:
            top_missing = missing_skills[:5]
            recommendations.append(
                f"🎯 Développer ces compétences clés: {', '.join(top_missing)}"
            )
        
        experience_years = cv_analysis.get('experience_years', 0)
        if experience_years < 3:
            recommendations.append(
                "💼 Mettre en avant vos projets personnels et contributions open-source"
            )
        
        if not cv_analysis.get('certifications'):
            recommendations.append(
                "📜 Envisager des certifications professionnelles pertinentes"
            )
        
        if cv_analysis.get('score', 0) < 0.6:
            recommendations.append(
                "📝 Personnaliser votre CV pour mieux correspondre à cette offre"
            )
        
        return recommendations
    
    @staticmethod
    def generate_interviewer_questions(cv_analysis: Dict, job_role: str) -> List[Dict[str, str]]:
        """Generate smart interview questions."""
        questions = []
        
        # Technical questions based on skills
        skills = cv_analysis.get('skills', [])[:5]
        if skills:
            skill2 = skills[1] if len(skills) > 1 else 'vos compétences'
            questions.append({
                'category': 'Technique',
                'question': f"Pouvez-vous décrire un projet où vous avez utilisé {skills[0]} et {skill2} ?",
                'focus': 'Évaluer l\'expertise technique'
            })
        
        # Experience questions
        experience = cv_analysis.get('experience', [])
        if experience:
            questions.append({
                'category': 'Expérience',
                'question': "Décrivez votre plus grand défi professionnel et comment vous l'avez surmonté.",
                'focus': 'Problem-solving et résilience'
            })
        
        # Cultural fit
        questions.append({
            'category': "Culture d'entreprise",
            'question': "Qu'est-ce qui vous motive dans votre travail au quotidien ?",
            'focus': 'Motivation et alignement avec les valeurs'
        })
        
        # Role-specific
        if 'lead' in job_role.lower() or 'senior' in job_role.lower():
            questions.append({
                'category': 'Leadership',
                'question': "Comment gérez-vous les conflits au sein d'une équipe ?",
                'focus': 'Compétences en leadership'
            })
        
        return questions


# Performance singleton
performance_monitor = PerformanceMonitor()

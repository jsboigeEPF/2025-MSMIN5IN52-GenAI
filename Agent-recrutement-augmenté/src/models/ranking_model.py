"""
Module pour le classement des candidats basé sur une approche hybride.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Configuration du logging
logger = logging.getLogger(__name__)

@dataclass
class RankingResult:
    """Résultat du classement d'un candidat"""
    score: float
    confidence: float
    reasoning: str
    detailed_scores: Dict[str, float]
    missing_skills: List[str]
    interview_questions: List[str]
    processing_time: float

class HybridRankingModel:
    """
    Moteur de scoring hybride combinant TF-IDF, LLM et correspondance de mots-clés.
    """
    
    def __init__(self, config_path: str = "Agent-recrutement-augmenté/config/settings.py"):
        """
        Initialise le modèle de ranking.
        
        Args:
            config_path (str): Chemin vers le fichier de configuration
        """
        try:
            # Import dynamique de la configuration
            import importlib.util
            spec = importlib.util.spec_from_file_location("settings", config_path)
            settings = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(settings)
            self.config = settings.config.ranking
            
            # Initialiser le vectorizer TF-IDF
            self.tfidf_vectorizer = TfidfVectorizer(
                stop_words=self._get_stop_words(),
                ngram_range=(1, 2),
                max_features=1000
            )
            
        except Exception as e:
            logger.warning(f"Erreur lors du chargement de la configuration: {e}")
            logger.info("Utilisation des paramètres par défaut")
            from config.settings import Config
            self.config = Config().ranking
            self.tfidf_vectorizer = TfidfVectorizer(
                stop_words=self._get_stop_words(),
                ngram_range=(1, 2),
                max_features=1000
            )
    
    def _get_stop_words(self) -> List[str]:
        """Retourne la liste des mots vides."""
        # Mots vides en français et anglais
        fr_stop = [
            'le', 'la', 'les', 'de', 'du', 'des', 'et', 'en', 'un', 'une', 'dans', 'sur', 'par', 'pour',
            'avec', 'sans', 'qui', 'que', 'quoi', 'où', 'quand', 'comment', 'pourquoi', 'ce', 'cette',
            'ces', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'son', 'sa', 'ses', 'notre', 'nos', 'votre',
            'vos', 'leur', 'leurs', 'il', 'elle', 'ils', 'elles', 'je', 'tu', 'nous', 'vous', 'on'
        ]
        en_stop = [
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'
        ]
        return fr_stop + en_stop
    
    def compute_match_score(self, 
                          cv_text: str, 
                          job_description: str, 
                          cv_entities: Optional[Dict] = None) -> RankingResult:
        """
        Calcule un score de correspondance entre un CV et une description de poste
        en utilisant une approche hybride TF-IDF + LLM + correspondance de mots-clés.
        
        Args:
            cv_text (str): Texte extrait du CV
            job_description (str): Description du poste
            cv_entities (Dict, optional): Entités extraites du CV
            
        Returns:
            RankingResult: Résultat du classement avec score, confiance et justification
        """
        import time
        start_time = time.time()
        
        try:
            # Prétraitement
            cv_text = self._preprocess_text(cv_text)
            job_description = self._preprocess_text(job_description)
            
            if not cv_text or not job_description:
                return RankingResult(
                    score=0.0,
                    confidence=0.1,
                    reasoning="Texte vide ou invalide",
                    detailed_scores={},
                    missing_skills=[],
                    interview_questions=[],
                    processing_time=time.time() - start_time
                )
            
            # Calculer les scores par méthode
            tfidf_score = self._compute_tfidf_score(cv_text, job_description)
            keyword_score = self._compute_keyword_score(cv_text, job_description)
            
            # Score LLM si activé
            if self.config.use_llm_scoring:
                llm_score, llm_reasoning = self._compute_llm_score(cv_text, job_description, cv_entities)
            else:
                llm_score = 0.0
                llm_reasoning = "Scoring LLM désactivé"
            
            # Fusionner les scores avec pondération
            detailed_scores = {
                'tfidf': tfidf_score,
                'keyword': keyword_score,
                'llm': llm_score
            }
            
            # Score final pondéré
            final_score = (
                tfidf_score * self.config.tfidf_weight +
                keyword_score * self.config.keyword_weight +
                llm_score * self.config.llm_weight
            )
            
            # Calculer la confiance
            confidence = self._calculate_confidence(detailed_scores, cv_text, job_description)
            
            # Générer la justification
            reasoning = self._generate_reasoning(
                final_score, confidence, detailed_scores, llm_reasoning, cv_entities, job_description
            )
            
            # Identifier les compétences manquantes
            missing_skills = self._identify_missing_skills(cv_entities, job_description)
            
            # Générer des questions d'entretien
            interview_questions = self._generate_interview_questions(cv_entities, job_description)
            
            return RankingResult(
                score=min(final_score, 1.0),
                confidence=min(confidence, 1.0),
                reasoning=reasoning,
                detailed_scores=detailed_scores,
                missing_skills=missing_skills,
                interview_questions=interview_questions,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul du score: {e}")
            return RankingResult(
                score=0.0,
                confidence=0.1,
                reasoning=f"Erreur lors du calcul du score: {str(e)}",
                detailed_scores={},
                missing_skills=[],
                interview_questions=[],
                processing_time=time.time() - start_time
            )
    
    def _preprocess_text(self, text: str) -> str:
        """Prétraite le texte pour l'analyse."""
        if not text:
            return ""
        
        # Convertir en minuscules
        text = text.lower()
        
        # Remplacer les caractères spéciaux
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remplacer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _compute_tfidf_score(self, cv_text: str, job_description: str) -> float:
        """Calcule le score TF-IDF entre le CV et la description de poste."""
        try:
            # Vectoriser les textes
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([cv_text, job_description])
            
            # Calculer la similarité cosinus
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.warning(f"Erreur TF-IDF: {e}")
            return 0.0
    
    def _compute_keyword_score(self, cv_text: str, job_description: str) -> float:
        """Calcule le score basé sur la correspondance de mots-clés."""
        # Extraire les mots-clés de la description de poste
        job_keywords = self._extract_keywords(job_description)
        
        if not job_keywords:
            return 0.0
        
        # Trouver les mots-clés présents dans le CV
        cv_lower = cv_text.lower()
        matched_keywords = [kw for kw in job_keywords if kw.lower() in cv_lower]
        
        # Score de couverture
        coverage_score = len(matched_keywords) / len(job_keywords)
        
        # Score de densité
        keyword_density = sum(cv_lower.count(kw.lower()) for kw in matched_keywords) / len(cv_text.split())
        
        # Score combiné
        keyword_score = (coverage_score * 0.6) + (keyword_density * 0.4)
        
        return min(keyword_score, 1.0)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrait les mots-clés pertinents du texte."""
        # Mots-clés techniques
        technical_keywords = [
            'python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'sql', 'nosql',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'linux', 'git', 'machine learning',
            'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch', 'keras',
            'scikit-learn', 'pandas', 'numpy', 'react', 'angular', 'vue', 'node.js',
            'django', 'flask', 'spring', 'hadoop', 'spark', 'kafka', 'airflow', 'jenkins',
            'ansible', 'postgresql', 'mongodb', 'mysql', 'redis', 'elasticsearch',
            'sap', 'erp', 'devops', 'agile', 'scrum', 'microservices', 'api', 'rest',
            'graphql', 'ci/cd', 'gitlab', 'github', 'jenkins', 'terraform', 'ansible',
            'prometheus', 'grafana'
        ]
        
        # Extraire les mots-clés présents
        found_keywords = []
        text_lower = text.lower()
        for keyword in technical_keywords:
            if keyword in text_lower and keyword not in found_keywords:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _compute_llm_score(self, cv_text: str, job_description: str, cv_entities: Optional[Dict]) -> Tuple[float, str]:
        """Calcule le score LLM (placeholder - à implémenter avec API réelle)."""
        # Placeholder pour l'intégration LLM
        # Dans une version complète, cela appellerait une API LLM
        logger.info("Scoring LLM - fonctionnalité de démonstration")
        
        # Simuler un score LLM basé sur l'analyse du texte
        llm_score = 0.5
        reasoning = "Analyse LLM simulée: correspondance partielle détectée"
        
        return llm_score, reasoning
    
    def _calculate_confidence(self, detailed_scores: Dict[str, float], cv_text: str, job_description: str) -> float:
        """Calcule la confiance globale du score."""
        # Base de confiance
        confidence = 0.3
        
        # Bonus pour les méthodes utilisées
        if self.config.use_tfidf:
            confidence += detailed_scores.get('tfidf', 0) * 0.2
        if self.config.use_keyword_matching:
            confidence += detailed_scores.get('keyword', 0) * 0.2
        if self.config.use_llm_scoring:
            confidence += detailed_scores.get('llm', 0) * 0.3
        
        # Ajustement selon la longueur des textes
        cv_length = len(cv_text.split())
        job_length = len(job_description.split())
        
        if cv_length < 50 or job_length < 20:
            confidence *= 0.7  # Réduction pour textes courts
        
        return min(confidence, 1.0)
    
    def _generate_reasoning(self, 
                          final_score: float, 
                          confidence: float, 
                          detailed_scores: Dict[str, float],
                          llm_reasoning: str,
                          cv_entities: Optional[Dict],
                          job_description: str) -> str:
        """Génère une justification détaillée du score."""
        reasoning = f"Score de correspondance : {final_score:.2%}\n"
        reasoning += f"Niveau de confiance : {confidence:.2%}\n\n"
        
        # Détail des scores
        reasoning += "Détail des scores :\n"
        if self.config.use_tfidf:
            reasoning += f"• Similarité TF-IDF : {detailed_scores.get('tfidf', 0):.2%}\n"
        if self.config.use_keyword_matching:
            reasoning += f"• Correspondance mots-clés : {detailed_scores.get('keyword', 0):.2%}\n"
        if self.config.use_llm_scoring:
            reasoning += f"• Évaluation LLM : {detailed_scores.get('llm', 0):.2%}\n"
        
        reasoning += f"\nScore final combiné : {final_score:.2%}\n\n"
        
        # Analyse détaillée
        reasoning += "Analyse détaillée :\n"
        
        if final_score >= 0.8:
            reasoning += "✅ Excellent profil correspondant aux exigences du poste.\n"
        elif final_score >= 0.6:
            reasoning += "🟡 Bon profil avec une correspondance satisfaisante.\n"
        elif final_score >= 0.4:
            reasoning += "⚠️ Profil partiellement correspondant, plusieurs compétences manquantes.\n"
        else:
            reasoning += "❌ Profil insuffisamment correspondant aux exigences du poste.\n"
        
        if self.config.use_llm_scoring:
            reasoning += f"\n{llm_reasoning}"
        
        return reasoning
    
    def _identify_missing_skills(self, cv_entities: Optional[Dict], job_description: str) -> List[str]:
        """Identifie les compétences manquantes par rapport à la description de poste."""
        if not cv_entities or 'skills' not in cv_entities:
            return []
        
        # Extraire les compétences requises
        required_skills = self._extract_keywords(job_description)
        
        # Compétences du candidat
        candidate_skills = [skill.lower() for skill in cv_entities.get('skills', [])]
        
        # Identifier les compétences manquantes
        missing = []
        for skill in required_skills:
            if skill not in candidate_skills and skill.title() not in missing:
                missing.append(skill.title())
        
        return missing
    
    def _generate_interview_questions(self, cv_entities: Optional[Dict], job_description: str) -> List[str]:
        """Génère des questions d'entretien pertinentes."""
        questions = []
        
        # Questions basées sur l'expérience
        if cv_entities and 'experience' in cv_entities and len(cv_entities['experience']) > 0:
            questions.append("Pourriez-vous décrire votre expérience la plus pertinente par rapport aux exigences du poste ?")
            questions.append("Quel a été votre plus grand défi dans votre poste précédent et comment l'avez-vous surmonté ?")
        
        # Questions basées sur les compétences
        if cv_entities and 'skills' in cv_entities:
            technical_skills = [s for s in cv_entities['skills'] if s.lower() in ['python', 'machine learning', 'nlp', 'aws']]
            if technical_skills:
                questions.append(f"Pourriez-vous décrire un projet où vous avez utilisé {technical_skills[0]} ?")
        
        # Questions basées sur l'éducation
        if cv_entities and 'education' in cv_entities and len(cv_entities['education']) > 0:
            questions.append("Comment votre formation vous a-t-elle préparé pour ce poste ?")
        
        return questions
    
    def rank_candidates(self, cvs: List[Dict[str, str]], job_description: str) -> List[Dict[str, Any]]:
        """
        Classe les candidats selon leur score de correspondance.
        
        Args:
            cvs (List[Dict[str, str]]): Liste des CVs parsés
            job_description (str): Description du poste
            
        Returns:
            List[Dict[str, Any]]: Liste des candidats classés avec scores et justifications
        """
        ranked = []
        
        for cv in cvs:
            # Obtenir le score et la confiance
            cv_entities = cv.get("entities", {})
            result = self.compute_match_score(cv["text"], job_description, cv_entities)
            score = result.score
            confidence = result.confidence
            
            # Créer l'entrée classée
            ranked_candidate = {
                "filename": cv["filename"],
                "score": score,
                "confidence": confidence,
                "reasoning": result.reasoning,
                "detailed_scores": result.detailed_scores,
                "missing_skills": result.missing_skills,
                "interview_questions": result.interview_questions,
                "processing_time": result.processing_time,
                "entities": cv_entities
            }
            
            ranked.append(ranked_candidate)
        
        # Trier par score décroissant
        return sorted(ranked, key=lambda x: x["score"], reverse=True)
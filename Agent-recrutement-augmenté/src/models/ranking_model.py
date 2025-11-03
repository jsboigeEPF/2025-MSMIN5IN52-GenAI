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
    
    def __init__(self, config_path: str = "config/settings.py"):
        """
        Initialise le modèle de ranking.
        
        Args:
            config_path (str): Chemin vers le fichier de configuration
        """
        try:
            # Import direct de la configuration
            from config.settings import Config
            self.config = Config().ranking
            
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
        """Calcule le score basé sur la correspondance de mots-clés avec pondération intelligente."""
        # Extraire les mots-clés de la description de poste
        job_keywords = self._extract_keywords(job_description)
        
        if not job_keywords:
            return 0.5  # Score neutre si pas de keywords
        
        cv_lower = cv_text.lower()
        
        # Catégoriser les keywords par importance
        critical_keywords = []
        important_keywords = []
        nice_to_have = []
        
        # Mots critiques souvent mentionnés dans les descriptions
        critical_terms = ['required', 'must', 'obligatoire', 'essentiel', 'impératif']
        important_terms = ['preferred', 'préféré', 'souhaité', 'important']
        
        job_lower = job_description.lower()
        for kw in job_keywords:
            kw_context = self._get_keyword_context(kw, job_lower, 50)
            if any(term in kw_context for term in critical_terms):
                critical_keywords.append(kw)
            elif any(term in kw_context for term in important_terms):
                important_keywords.append(kw)
            else:
                nice_to_have.append(kw)
        
        # Si pas de catégorisation, distribuer intelligemment
        if not critical_keywords and not important_keywords:
            # Top 30% = critical, next 40% = important, rest = nice
            total = len(job_keywords)
            critical_keywords = job_keywords[:int(total * 0.3)]
            important_keywords = job_keywords[int(total * 0.3):int(total * 0.7)]
            nice_to_have = job_keywords[int(total * 0.7):]
        
        # Calculer scores pondérés
        critical_matched = sum(1 for kw in critical_keywords if kw.lower() in cv_lower)
        important_matched = sum(1 for kw in important_keywords if kw.lower() in cv_lower)
        nice_matched = sum(1 for kw in nice_to_have if kw.lower() in cv_lower)
        
        # Pondération: 50% critical, 30% important, 20% nice-to-have
        critical_score = (critical_matched / len(critical_keywords) * 0.5) if critical_keywords else 0
        important_score = (important_matched / len(important_keywords) * 0.3) if important_keywords else 0
        nice_score = (nice_matched / len(nice_to_have) * 0.2) if nice_to_have else 0
        
        coverage_score = critical_score + important_score + nice_score
        
        # Bonus pour répétition de keywords (expertise)
        all_matched = [kw for kw in job_keywords if kw.lower() in cv_lower]
        repetition_bonus = 0
        if all_matched:
            avg_frequency = sum(cv_lower.count(kw.lower()) for kw in all_matched) / len(all_matched)
            repetition_bonus = min(avg_frequency / 10, 0.15)  # Max 15% bonus
        
        final_score = coverage_score + repetition_bonus
        
        return min(final_score, 1.0)
    
    def _get_keyword_context(self, keyword: str, text: str, window: int = 50) -> str:
        """Récupère le contexte autour d'un keyword."""
        pos = text.find(keyword.lower())
        if pos == -1:
            return ""
        start = max(0, pos - window)
        end = min(len(text), pos + len(keyword) + window)
        return text[start:end]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrait les mots-clés pertinents du texte - Liste exhaustive."""
        # Langages de programmation
        languages = ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'ruby', 'php', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash', 'powershell', 'vba', 'cobol', 'fortran']
        
        # Frameworks & librairies
        frameworks = ['react', 'angular', 'vue', 'vue.js', 'node.js', 'express', 'django', 'flask', 'fastapi', 'spring', 'spring boot', 'hibernate', 'asp.net', '.net', 'laravel', 'symfony', 'rails', 'nextjs', 'next.js', 'nuxt', 'gatsby', 'svelte', 'jquery', 'bootstrap', 'tailwind']
        
        # Data science & ML
        ml_tools = ['machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'scipy', 'matplotlib', 'jupyter', 'opencv', 'nltk', 'spacy', 'transformers', 'bert', 'gpt', 'llm', 'neural networks', 'xgboost', 'lightgbm']
        
        # Cloud & DevOps
        cloud_tools = ['aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s', 'jenkins', 'gitlab', 'github', 'terraform', 'ansible', 'ci/cd', 'helm', 'prometheus', 'grafana', 'elk', 'datadog', 'cloudformation', 'serverless', 'lambda', 'ec2', 's3']
        
        # Databases
        databases = ['sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'oracle', 'sql server', 'redis', 'elasticsearch', 'cassandra', 'neo4j', 'firebase', 'snowflake', 'bigquery', 'redshift']
        
        # Outils & méthodologies
        tools = ['git', 'jira', 'confluence', 'agile', 'scrum', 'kanban', 'devops', 'tdd', 'rest', 'api', 'graphql', 'microservices', 'etl', 'spark', 'hadoop', 'kafka', 'airflow', 'tableau', 'power bi', 'looker']
        
        # Technologies web & mobile
        web_tech = ['html', 'html5', 'css', 'css3', 'sass', 'webpack', 'jest', 'cypress', 'selenium', 'postman', 'swagger', 'oauth', 'jwt', 'websocket', 'grpc']
        
        # Systèmes
        systems = ['linux', 'unix', 'ubuntu', 'windows', 'macos', 'nginx', 'apache', 'tomcat', 'load balancer', 'cdn', 'vpn', 'ssh']
        
        # Business
        business = ['sap', 'erp', 'crm', 'salesforce', 'dynamics', 'servicenow', 'sharepoint', 'excel', 'power apps']
        
        # Soft skills & concepts
        soft_skills = ['leadership', 'communication', 'teamwork', 'problem solving', 'analytical', 'project management', 'mentoring', 'collaboration', 'innovation', 'autonomy', 'adaptability']
        
        # Certifications courantes
        certifications = ['aws certified', 'azure certified', 'pmp', 'itil', 'cissp', 'ceh', 'ccna', 'comptia', 'scrum master', 'safe', 'togaf']
        
        # Combiner toutes les catégories
        all_keywords = languages + frameworks + ml_tools + cloud_tools + databases + tools + web_tech + systems + business + soft_skills + certifications
        
        # Extraire les mots-clés présents
        found_keywords = []
        text_lower = text.lower()
        for keyword in all_keywords:
            if keyword in text_lower and keyword not in found_keywords:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _compute_llm_score(self, cv_text: str, job_description: str, cv_entities: Optional[Dict]) -> Tuple[float, str]:
        """Calcule le score LLM en utilisant Groq ou OpenAI pour une analyse contextuelle."""
        try:
            # Import OpenAI-compatible client
            try:
                from openai import OpenAI
            except ImportError:
                logger.warning("OpenAI package not installed. Using fallback scoring.")
                return 0.5, "Analyse LLM non disponible: package OpenAI manquant"
            
            # Get API configuration
            api_key = None
            provider = "groq"
            model = "llama-3.1-70b-versatile"
            base_url = None
            
            try:
                from config.settings import config
                provider = config.model.llm_provider
                model = config.model.llm_model
                
                if provider == "groq":
                    api_key = config.model.api_keys.get('groq', '')
                    base_url = "https://api.groq.com/openai/v1"
                else:
                    api_key = config.model.api_keys.get('openai', '')
            except:
                pass
            
            if not api_key:
                logger.warning(f"{provider.upper()} API key not configured. Using fallback scoring.")
                return 0.5, "Analyse LLM non disponible: clé API manquante"
            
            # Initialize client (Groq or OpenAI)
            if base_url:
                client = OpenAI(api_key=api_key, base_url=base_url)
            else:
                client = OpenAI(api_key=api_key)
            
            # Prepare entities summary
            entities_summary = ""
            if cv_entities:
                if cv_entities.get('skills'):
                    entities_summary += f"\nCompétences: {', '.join(cv_entities['skills'][:10])}"
                if cv_entities.get('experience'):
                    exp_count = len(cv_entities['experience'])
                    entities_summary += f"\nExpériences: {exp_count} postes"
                if cv_entities.get('education'):
                    edu_count = len(cv_entities['education'])
                    entities_summary += f"\nFormation: {edu_count} diplômes"
            
            # Create prompt for LLM
            prompt = f"""Tu es un expert en recrutement. Analyse ce CV par rapport à la description de poste et fournis un score de correspondance entre 0 et 1.

DESCRIPTION DU POSTE:
{job_description[:1500]}

CV DU CANDIDAT (extrait):
{cv_text[:2000]}
{entities_summary}

Analyse la correspondance entre le CV et la description de poste en considérant:
1. Les compétences techniques requises
2. L'expérience pertinente
3. La formation et les qualifications
4. Les soft skills et la culture d'entreprise
5. Le potentiel d'évolution

Réponds UNIQUEMENT au format JSON suivant:
{{
    "score": 0.0-1.0,
    "reasoning": "Explication détaillée en 2-3 phrases",
    "strengths": ["point fort 1", "point fort 2"],
    "weaknesses": ["point faible 1", "point faible 2"],
    "recommendation": "EXCELLENT/BON/MOYEN/FAIBLE"
}}"""
            
            # Call LLM API (Groq or OpenAI)
            logger.info(f"Calling {provider.upper()} with model {model}")
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Tu es un expert en recrutement et en analyse de CVs. Tu fournis des évaluations précises et objectives au format JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800,
                response_format={"type": "json_object"} if provider == "openai" else None
            )
            
            # Parse response
            import json
            response_text = response.choices[0].message.content
            
            # Try to extract JSON if embedded in text
            try:
                # Try direct parse first
                result = json.loads(response_text)
            except:
                # Try to find JSON block in text
                import re
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(0))
                else:
                    logger.warning(f"Could not parse LLM response as JSON: {response_text[:200]}")
                    return 0.5, "Réponse LLM invalide"
            
            score = float(result.get('score', 0.5))
            reasoning = result.get('reasoning', 'Analyse LLM effectuée')
            strengths = result.get('strengths', [])
            weaknesses = result.get('weaknesses', [])
            recommendation = result.get('recommendation', 'MOYEN')
            
            # Build detailed reasoning
            detailed_reasoning = f"{reasoning}\n\n"
            detailed_reasoning += f"🎯 Recommandation: {recommendation}\n"
            if strengths:
                detailed_reasoning += f"✅ Points forts: {', '.join(strengths)}\n"
            if weaknesses:
                detailed_reasoning += f"⚠️ Points à améliorer: {', '.join(weaknesses)}"
            
            logger.info(f"LLM scoring completed with score: {score:.2f}")
            return min(max(score, 0.0), 1.0), detailed_reasoning
            
        except Exception as e:
            logger.error(f"Erreur lors du scoring LLM: {e}")
            return 0.5, f"Analyse LLM partielle: {str(e)[:100]}"
    
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
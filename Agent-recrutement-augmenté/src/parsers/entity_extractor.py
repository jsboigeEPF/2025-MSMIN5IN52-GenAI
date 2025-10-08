"""
Module pour l'extraction d'entités structurées à partir de CVs.
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import spacy
from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop_words
from spacy.lang.en.stop_words import STOP_WORDS as en_stop_words

# Configuration du logging
logger = logging.getLogger(__name__)

@dataclass
class ExtractionResult:
    """Résultat de l'extraction d'entités"""
    entities: Dict[str, List]
    confidence: float
    processing_time: float
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

class EntityExtractor:
    """
    Classe pour extraire des entités structurées à partir de texte de CV.
    Utilise spaCy pour l'analyse NLP avec fallback sur les expressions régulières.
    """
    
    def __init__(self, config_path: str = "config/settings.py"):
        """
        Initialise l'extracteur d'entités.
        
        Args:
            config_path (str): Chemin vers le fichier de configuration
        """
        try:
            # Import dynamique de la configuration
            import importlib.util
            spec = importlib.util.spec_from_file_location("settings", config_path)
            settings = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(settings)
            self.config = settings.config.extraction
            
            # Charger le modèle spaCy
            self._load_spacy_model()
            
        except Exception as e:
            logger.warning(f"Erreur lors du chargement de la configuration: {e}")
            logger.info("Utilisation des paramètres par défaut")
            self.config = ExtractionConfig()
            self.nlp = None
    
    def _load_spacy_model(self):
        """Charge le modèle spaCy selon la configuration."""
        try:
            if self.config.use_spacy:
                self.nlp = spacy.load(self.config.spacy_model)
                logger.info(f"Modèle spaCy '{self.config.spacy_model}' chargé avec succès")
            else:
                self.nlp = None
                logger.info("Utilisation uniquement des expressions régulières")
        except OSError:
            logger.warning(f"Modèle spaCy '{self.config.spacy_model}' non trouvé")
            logger.info("Tentative avec le modèle par défaut 'fr_core_news_sm'")
            try:
                self.nlp = spacy.load("fr_core_news_sm")
                logger.info("Modèle 'fr_core_news_sm' chargé avec succès")
            except:
                logger.warning("Aucun modèle spaCy disponible, utilisation uniquement des regex")
                self.nlp = None
    
    def extract_entities(self, text: str) -> ExtractionResult:
        """
        Extrait toutes les entités structurées du texte.
        
        Args:
            text (str): Texte du CV
            
        Returns:
            ExtractionResult: Résultat de l'extraction avec entités, confiance et métadonnées
        """
        import time
        start_time = time.time()
        entities = {}
        warnings = []
        
        try:
            # Prétraitement du texte
            clean_text = self._preprocess_text(text)
            
            # Extraction par type d'entité
            entities['skills'] = self._extract_skills(clean_text)
            entities['education'] = self._extract_education(clean_text)
            entities['experience'] = self._extract_experience(clean_text)
            entities['certifications'] = self._extract_certifications(clean_text)
            entities['personal_info'] = self._extract_personal_info(clean_text)
            entities['languages'] = self._extract_languages(clean_text)
            
            # Calcul de la confiance globale
            confidence = self._calculate_confidence(entities, text)
            
            processing_time = time.time() - start_time
            
            return ExtractionResult(
                entities=entities,
                confidence=confidence,
                processing_time=processing_time,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des entités: {e}")
            processing_time = time.time() - start_time
            return ExtractionResult(
                entities={key: [] for key in ['skills', 'education', 'experience', 'certifications', 'personal_info', 'languages']},
                confidence=0.0,
                processing_time=processing_time,
                warnings=[f"Erreur d'extraction: {str(e)}"]
            )
    
    def _preprocess_text(self, text: str) -> str:
        """Prétraite le texte pour l'analyse."""
        if not text:
            return ""
        
        # Normalisation
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)  # Remplacer les espaces multiples
        text = text.strip()
        
        return text
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extrait les compétences techniques du texte."""
        skills = []
        
        # Utiliser spaCy si disponible
        if self.nlp:
            doc = self.nlp(text)
            # Extraire les entités nommées pertinentes
            for ent in doc.ents:
                if ent.label_ in ['SKILL', 'TECHNOLOGY', 'PRODUCT']:
                    skills.append(ent.text.title())
        
        # Fallback sur les expressions régulières
        if self.config.fallback_regex:
            # Mots-clés de compétences techniques
            tech_keywords = [
                'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust',
                'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'linux', 'git',
                'machine learning', 'deep learning', 'nlp', 'computer vision',
                'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
                'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
                'hadoop', 'spark', 'kafka', 'airflow', 'jenkins', 'ansible'
            ]
            
            for keyword in tech_keywords:
                if keyword in text and keyword.title() not in skills:
                    skills.append(keyword.title())
        
        # Supprimer les doublons et trier
        return sorted(list(set(skills)))
    
    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extrait les informations d'éducation du texte."""
        education_entries = []
        
        # Utiliser spaCy si disponible
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['DEGREE', 'EDUCATION']:
                    education_entries.append({
                        'degree': ent.text.title(),
                        'institution': self._extract_institution(text, ent.text),
                        'year': self._extract_year(text)
                    })
        
        # Fallback sur les expressions régulières
        if self.config.fallback_regex and not education_entries:
            education_patterns = [
                r'(?:bac\+?\d|bachelor|licence|master|phd|doctorat|ingénieur|diplôme|certificat|formation)[\s:]*([^\n,;]+)',
                r'(?:université|école|institut|faculté)[\s:]*([^\n,;]+)'
            ]
            
            for pattern in education_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    clean_text = re.sub(r'\s+', ' ', match.strip())
                    if len(clean_text) > 5:
                        education_entries.append({
                            'degree': clean_text.title(),
                            'institution': self._extract_institution(text, clean_text),
                            'year': self._extract_year(text)
                        })
        
        return education_entries
    
    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extrait les expériences professionnelles du texte."""
        experience_entries = []
        
        # Utiliser spaCy si disponible
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['WORK_OF_ART', 'ORG', 'DATE']:
                    # Heuristique pour détecter les expériences
                    context = self._get_context(ent.text, text, window=50)
                    if any(word in context.lower() for word in ['expérience', 'poste', 'travail', 'emploi', 'stage']):
                        experience_entries.append({
                            'position': ent.text.title(),
                            'company': self._extract_company(text),
                            'duration': self._extract_duration(text),
                            'description': context
                        })
        
        # Fallback sur les expressions régulières
        if self.config.fallback_regex and not experience_entries:
            experience_patterns = [
                r'(?:expérience|expérience professionnelle|carrière|poste|travail|emploi|stage|alternance|freelance)[\s:\n]+((?:[^:\n][^\n]*\n?)+?)(?=\n\s*[A-Z]|\n\n|$)',
                r'(?:\d{4}.*?)(?:[^:\n][^\n]*\n?)+?',
            ]
            
            for pattern in experience_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    clean_text = re.sub(r'\s+', ' ', match.strip())
                    if len(clean_text) > 20:
                        experience_entries.append({
                            'position': self._extract_position(clean_text),
                            'company': self._extract_company(clean_text),
                            'duration': self._extract_duration(clean_text),
                            'description': clean_text
                        })
        
        return experience_entries
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extrait les certifications du texte."""
        certifications = []
        
        # Utiliser spaCy si disponible
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['CERTIFICATE', 'LICENSE']:
                    certifications.append(ent.text.title())
        
        # Fallback sur les expressions régulières
        if self.config.fallback_regex:
            cert_patterns = [
                r'(?:certifications?|certificats?|diplômes professionnels?)[\s:]*([^\n]+)',
            ]
            
            for pattern in cert_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    items = re.split(r'[,;]', match)
                    for item in items:
                        item = item.strip()
                        if len(item) > 1:
                            certifications.append(item.title())
        
        return sorted(list(set(certifications)))
    
    def _extract_personal_info(self, text: str) -> Dict[str, str]:
        """Extrait les informations personnelles (email, téléphone, LinkedIn, etc.)."""
        personal_info = {}
        
        # Utiliser les patterns de configuration
        for field, pattern in self.config.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                personal_info[field] = matches[0]
        
        return personal_info
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extrait les langues parlées."""
        languages = []
        language_list = [
            'français', 'anglais', 'espagnol', 'allemand', 'italien', 'portugais',
            'chinois', 'japonais', 'arabe', 'russe', 'néerlandais', 'suédois'
        ]
        
        text_lower = text.lower()
        for lang in language_list:
            if lang in text_lower and lang.title() not in languages:
                languages.append(lang.title())
        
        return languages
    
    def _extract_institution(self, text: str, context: str = "") -> Optional[str]:
        """Extrait le nom de l'institution."""
        # Recherche de mots-clés d'institutions
        patterns = [
            r'(?:université|university|école|school|institut|college|faculté|faculty)',
            r'(?:\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)'
        ]
        
        search_text = context if context else text
        for pattern in patterns:
            matches = re.findall(pattern, search_text, re.IGNORECASE)
            if matches:
                return matches[0].title()
        
        return None
    
    def _extract_year(self, text: str) -> Optional[str]:
        """Extrait l'année."""
        year_pattern = r'(?:\b|[^0-9])(20[0-9]{2}|19[0-9]{2})(?:\b|[^0-9])'
        matches = re.findall(year_pattern, text)
        return matches[0] if matches else None
    
    def _extract_position(self, text: str) -> Optional[str]:
        """Extrait le poste."""
        # Recherche de postes courants
        position_keywords = [
            'ingénieur', 'engineer', 'développeur', 'developer', 'analyste', 'analyst',
            'consultant', 'manager', 'responsable', 'lead', 'architecte', 'architect',
            'technicien', 'specialist', 'expert', 'director', 'chef de projet'
        ]
        
        for keyword in position_keywords:
            if keyword.lower() in text.lower():
                # Extraire le contexte autour du mot-clé
                pattern = r'(?:\b\w+\s+){0,3}' + keyword + r'(?:\s+\w+){0,3}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    return matches[0].title()
        
        return None
    
    def _extract_company(self, text: str) -> Optional[str]:
        """Extrait le nom de l'entreprise."""
        # Recherche de noms d'entreprises courants
        company_patterns = [
            r'(?:chez|at|for|pour)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        return None
    
    def _extract_duration(self, text: str) -> Optional[str]:
        """Extrait la durée."""
        duration_patterns = [
            r'(?:depuis|since|from)\s+(?:\w+\s+)?\d{4}',
            r'(?:\d{4}\s*-\s*\d{4}|\d{4}\s*-\s*présent)',
            r'(?:\d+\s+(?:ans?|years?|mois|months?))'
        ]
        
        for pattern in duration_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return None
    
    def _get_context(self, target: str, text: str, window: int = 50) -> str:
        """Récupère le contexte autour d'un mot cible."""
        pos = text.find(target)
        if pos == -1:
            return target
        
        start = max(0, pos - window)
        end = min(len(text), pos + len(target) + window)
        return text[start:end]
    
    def _calculate_confidence(self, entities: Dict[str, List], original_text: str) -> float:
        """Calcule la confiance globale de l'extraction."""
        if not original_text.strip():
            return 0.0
        
        # Facteurs de confiance
        total_entities = sum(len(entities[key]) for key in entities)
        text_length = len(original_text)
        
        # Base de confiance selon la longueur du texte
        base_confidence = min(0.3 + (text_length / 1000) * 0.4, 0.7)
        
        # Bonus pour les entités trouvées
        if total_entities > 0:
            entity_confidence = min(total_entities * 0.1, 0.3)
            base_confidence += entity_confidence
        
        # Appliquer le seuil de confiance de la configuration
        return min(base_confidence, self.config.confidence_threshold)
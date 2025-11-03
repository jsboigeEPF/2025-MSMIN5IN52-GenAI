"""
Module pour l'extraction d'entités structurées à partir de CVs.
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import spacy
from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop_words
from spacy.lang.en.stop_words import STOP_WORDS as en_stop_words
from config.settings import ExtractionConfig # Import de la classe de configuration

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
            # Import direct de la configuration
            from config.settings import Config
            self.config = Config().extraction
            
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
        
        # Fallback sur les expressions régulières - Liste exhaustive
        if self.config.fallback_regex:
            # Langages de programmation
            languages = ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'ruby', 'php', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash', 'powershell', 'vba', 'cobol', 'fortran', 'assembly', 'lua', 'dart', 'elixir', 'haskell', 'clojure', 'groovy', 'objective-c']
            
            # Frameworks & librairies
            frameworks = ['react', 'angular', 'vue', 'vue.js', 'node.js', 'express', 'django', 'flask', 'fastapi', 'spring', 'spring boot', 'hibernate', 'asp.net', '.net', 'laravel', 'symfony', 'rails', 'ruby on rails', 'nextjs', 'next.js', 'nuxt', 'gatsby', 'svelte', 'ember', 'backbone', 'jquery', 'bootstrap', 'tailwind', 'material-ui', 'ant design']
            
            # Data science & ML
            ml_tools = ['machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly', 'jupyter', 'anaconda', 'opencv', 'nltk', 'spacy', 'hugging face', 'transformers', 'bert', 'gpt', 'llm', 'neural networks', 'cnn', 'rnn', 'lstm', 'gan', 'reinforcement learning', 'xgboost', 'lightgbm', 'catboost']
            
            # Cloud & DevOps
            cloud_tools = ['aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s', 'jenkins', 'gitlab', 'github', 'bitbucket', 'terraform', 'ansible', 'puppet', 'chef', 'vagrant', 'ci/cd', 'circleci', 'travis', 'github actions', 'argocd', 'helm', 'prometheus', 'grafana', 'elk', 'datadog', 'new relic', 'splunk', 'nagios', 'cloudformation', 'serverless', 'lambda', 'ec2', 's3', 'rds', 'dynamodb', 'cloudwatch']
            
            # Databases
            databases = ['sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'mariadb', 'oracle', 'sql server', 'sqlite', 'redis', 'elasticsearch', 'cassandra', 'couchbase', 'neo4j', 'influxdb', 'timescaledb', 'firebase', 'supabase', 'snowflake', 'bigquery', 'redshift', 'athena', 'hive', 'presto', 'clickhouse']
            
            # Outils & méthodologies
            tools = ['git', 'svn', 'mercurial', 'jira', 'confluence', 'trello', 'asana', 'slack', 'teams', 'agile', 'scrum', 'kanban', 'devops', 'tdd', 'bdd', 'rest', 'api', 'graphql', 'soap', 'microservices', 'soa', 'etl', 'data pipeline', 'apache spark', 'hadoop', 'kafka', 'rabbitmq', 'celery', 'airflow', 'luigi', 'prefect', 'dbt', 'tableau', 'power bi', 'looker', 'metabase', 'superset']
            
            # Technologies web
            web_tech = ['html', 'html5', 'css', 'css3', 'sass', 'scss', 'less', 'webpack', 'vite', 'babel', 'eslint', 'prettier', 'jest', 'mocha', 'chai', 'cypress', 'selenium', 'playwright', 'puppeteer', 'webdriver', 'postman', 'insomnia', 'swagger', 'openapi', 'oauth', 'jwt', 'saml', 'ldap', 'sso', 'websocket', 'grpc', 'protobuf']
            
            # Systèmes & réseaux
            systems = ['linux', 'unix', 'ubuntu', 'debian', 'centos', 'rhel', 'fedora', 'windows', 'macos', 'windows server', 'active directory', 'nginx', 'apache', 'tomcat', 'iis', 'load balancer', 'cdn', 'dns', 'tcp/ip', 'http', 'https', 'ssl', 'tls', 'vpn', 'firewall', 'proxy', 'ssh', 'ftp', 'sftp']
            
            # Business & ERP
            business = ['sap', 'erp', 'crm', 'salesforce', 'dynamics', 'oracle erp', 'workday', 'servicenow', 'sharepoint', 'excel', 'vba', 'power apps', 'power automate', 'zapier', 'n8n']
            
            # Combiner toutes les catégories
            all_keywords = languages + frameworks + ml_tools + cloud_tools + databases + tools + web_tech + systems + business
            
            for keyword in all_keywords:
                if keyword in text:
                    # Ajouter avec capitalisation appropriée
                    if keyword.title() not in skills and keyword.upper() not in skills:
                        # Garder certains acronymes en majuscules
                        if keyword.upper() in ['API', 'REST', 'SQL', 'HTML', 'CSS', 'HTTP', 'HTTPS', 'SSL', 'TLS', 'VPN', 'SSH', 'FTP', 'DNS', 'CDN', 'SSO', 'JWT', 'ETL', 'TDD', 'BDD', 'CI', 'CD', 'ERP', 'CRM', 'SAP', 'AWS', 'GCP', 'NLP', 'CNN', 'RNN', 'LSTM', 'GAN', 'LLM', 'ML', 'AI']:
                            skills.append(keyword.upper())
                        else:
                            skills.append(keyword.title())
        
        # Supprimer les doublons et trier
        return sorted(list(set(skills)))
    
    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extrait les informations d'éducation du texte avec patterns améliorés."""
        education_entries = []
        
        # Patterns améliorés pour l'éducation
        education_patterns = [
            # Diplômes français
            r'(bac\+?[1-5]|licence|master[12]?|doctorat|ph\.?d|ingénieur|mba|dut|bts|deug|deust)',
            # Diplômes anglais
            r'(bachelor\'?s?|master\'?s?|doctorate|associate degree)',
            # Spécialisations
            r'(diplôme (?:d\')?ingénieur|grande école|école (?:de )?commerce)',
            # Établissements
            r'(université [^\n,;]{3,40}|école [^\n,;]{3,40}|institut [^\n,;]{3,40})',
            # Années avec contexte
            r'(\d{4}[\s-]+\d{4})\s*[:\-]?\s*([^\n]{10,80})',
        ]
        
        seen_degrees = set()
        
        # Utiliser spaCy si disponible
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['ORG'] and any(keyword in ent.text.lower() for keyword in ['université', 'école', 'institut', 'college', 'university']):
                    degree_text = ent.text.title()
                    if degree_text not in seen_degrees:
                        education_entries.append({
                            'degree': degree_text,
                            'institution': ent.text.title(),
                            'year': self._extract_year(self._get_context(ent.text, text, 100))
                        })
                        seen_degrees.add(degree_text)
        
        # Fallback amélioré sur expressions régulières
        for pattern in education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(m for m in match if m)
                
                clean_text = re.sub(r'\s+', ' ', str(match).strip())
                if 5 < len(clean_text) < 100 and clean_text not in seen_degrees:
                    context = self._get_context(clean_text, text, 150)
                    education_entries.append({
                        'degree': clean_text.title(),
                        'institution': self._extract_institution(context, clean_text),
                        'year': self._extract_year(context),
                        'field': self._extract_field_of_study(context)
                    })
                    seen_degrees.add(clean_text)
        
        return education_entries[:10]  # Limiter à 10 entrées max
    
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
    
    def _extract_field_of_study(self, text: str) -> Optional[str]:
        """Extrait le domaine d'études."""
        fields = [
            'informatique', 'computer science', 'génie logiciel', 'software engineering',
            'data science', 'intelligence artificielle', 'machine learning', 'cybersécurité',
            'réseaux', 'networks', 'télécommunications', 'électronique', 'mécanique',
            'gestion', 'management', 'commerce', 'business', 'marketing', 'finance',
            'mathématiques', 'mathematics', 'statistiques', 'physics', 'chimie'
        ]
        
        text_lower = text.lower()
        for field in fields:
            if field in text_lower:
                return field.title()
        return None
    
    def _calculate_confidence(self, entities: Dict[str, List], original_text: str) -> float:
        """Calcule la confiance globale de l'extraction avec scoring amélioré."""
        if not original_text.strip():
            return 0.0
        
        # Facteurs de confiance pondérés
        weights = {
            'skills': 0.30,
            'experience': 0.25,
            'education': 0.20,
            'personal_info': 0.15,
            'languages': 0.05,
            'certifications': 0.05
        }
        
        confidence_score = 0.0
        text_length = len(original_text)
        
        # Base de confiance selon la longueur du texte
        if text_length < 100:
            base_confidence = 0.2
        elif text_length < 500:
            base_confidence = 0.4
        elif text_length < 1500:
            base_confidence = 0.6
        else:
            base_confidence = 0.7
        
        # Ajouter confiance par catégorie d'entités
        for category, weight in weights.items():
            if category in entities and entities[category]:
                count = len(entities[category])
                # Plus d'entités = meilleure confiance, avec saturation
                category_confidence = min(count / 10.0, 1.0) * weight
                confidence_score += category_confidence
        
        # Bonus si email ou téléphone trouvé
        if entities.get('personal_info', {}).get('email') or entities.get('personal_info', {}).get('phone'):
            confidence_score += 0.1
        
        # Score final combiné
        final_confidence = (base_confidence * 0.4) + (confidence_score * 0.6)
        
        return min(final_confidence, 1.0)

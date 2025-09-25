"""
Module pour l'extraction d'entités structurées à partir de CVs.
"""

import re
import json
import os
from typing import Dict, List, Optional
import logging

# Configuration de base du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config(config_path: str = "config/config.json") -> Dict:
    """
    Charge la configuration depuis un fichier JSON.
    
    Args:
        config_path (str): Chemin vers le fichier de configuration
        
    Returns:
        Dict: Configuration chargée
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement de la configuration: {e}")
        return {}

class EntityExtractor:
    """
    Classe pour extraire des entités structurées à partir de texte de CV.
    """
    
    def __init__(self):
        # Charger la configuration
        config = load_config()
        
        # Utiliser la configuration ou des valeurs par défaut
        self.technical_skills = set(
            config.get("entity_extraction", {}).get("skills", [
                'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust',
                'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'linux', 'git',
                'machine learning', 'deep learning', 'nlp', 'computer vision',
                'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
                'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
                'hadoop', 'spark', 'kafka', 'airflow', 'jenkins', 'ansible'
            ])
        )
        
        self.education_levels = set(
            config.get("entity_extraction", {}).get("education_levels", [
                'bac', 'bachelor', 'licence', 'master', 'phd', 'doctorat',
                'diplôme', 'certificat', 'formation'
            ])
        )
        
        self.certifications = set(
            config.get("entity_extraction", {}).get("certifications", [
                'aws certified', 'azure certified', 'google cloud certified',
                'scrum master', 'pmp', 'six sigma', 'cissp', 'ceh',
                'oracle certified', 'microsoft certified', 'cisco certified'
            ])
        )
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extrait les compétences techniques du texte.
        
        Args:
            text (str): Texte du CV
            
        Returns:
            List[str]: Liste des compétences extraites
        """
        text_lower = text.lower()
        extracted_skills = []
        
        # Recherche par mots-clés
        for skill in self.technical_skills:
            if skill in text_lower:
                extracted_skills.append(skill.title())
        
        # Recherche de sections de compétences
        skills_patterns = [
            r'(?:compétences|skills|technologies)[\s:]*([^\n]+)',
            r'(?:langages?|languages?)[\s:]*([^\n]+)',
            r'(?:outils?|tools?)[\s:]*([^\n]+)',
            r'(?:frameworks?)[\s:]*([^\n]+)'
        ]
        
        for pattern in skills_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Nettoyer et diviser par virgules ou points-virgules
                items = re.split(r'[,;]', match)
                for item in items:
                    item = item.strip()
                    if len(item) > 1 and item.lower() not in ['et', 'or']:
                        extracted_skills.append(item.title())
        
        # Supprimer les doublons et trier
        return sorted(list(set(extracted_skills)))
    
    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """
        Extrait les informations d'éducation du texte.
        
        Args:
            text (str): Texte du CV
            
        Returns:
            List[Dict[str, str]]: Liste des diplômes avec détails
        """
        education_entries = []
        
        # Recherche de sections d'éducation
        education_patterns = [
            r'(?:éducation|formation|diplômes?|studies|education)[\s:\n]+((?:[^:\n][^\n]*\n?)+?)(?=\n\s*[A-Z]|\n\n|$)',
            r'(?:bac.*?|bachelor.*?|licence.*?|master.*?|phd.*?|doctorat.*?|diplôme.*?)(?:[^:\n][^\n]*\n?)+?',
        ]
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Nettoyer le texte
                clean_text = re.sub(r'\s+', ' ', match.strip())
                if len(clean_text) > 10:  # Éviter les entrées trop courtes
                    education_entries.append({
                        'degree': clean_text,
                        'institution': self._extract_institution(clean_text),
                        'year': self._extract_year(clean_text)
                    })
        
        return education_entries
    
    def extract_experience(self, text: str) -> List[Dict[str, str]]:
        """
        Extrait les expériences professionnelles du texte.
        
        Args:
            text (str): Texte du CV
            
        Returns:
            List[Dict[str, str]]: Liste des expériences avec détails
        """
        experience_entries = []
        
        # Recherche de sections d'expérience
        experience_patterns = [
            r'(?:expérience|expérience professionnelle|carrière|poste|travail|emploi|stage|alternance|freelance)[\s:\n]+((?:[^:\n][^\n]*\n?)+?)(?=\n\s*[A-Z]|\n\n|$)',
            r'(?:\d{4}.*?)(?:[^:\n][^\n]*\n?)+?',
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Nettoyer le texte
                clean_text = re.sub(r'\s+', ' ', match.strip())
                if len(clean_text) > 20:  # Éviter les entrées trop courtes
                    experience_entries.append({
                        'position': self._extract_position(clean_text),
                        'company': self._extract_company(clean_text),
                        'duration': self._extract_duration(clean_text),
                        'description': clean_text
                    })
        
        return experience_entries
    
    def extract_certifications(self, text: str) -> List[str]:
        """
        Extrait les certifications du texte.
        
        Args:
            text (str): Texte du CV
            
        Returns:
            List[str]: Liste des certifications extraites
        """
        text_lower = text.lower()
        certifications = []
        
        # Recherche par mots-clés
        for cert in self.certifications:
            if cert in text_lower:
                certifications.append(cert.title())
        
        # Recherche de sections de certifications
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
    
    def extract_all_entities(self, text: str) -> Dict[str, any]:
        """
        Extrait toutes les entités structurées du texte.
        
        Args:
            text (str): Texte du CV
            
        Returns:
            Dict[str, any]: Dictionnaire contenant toutes les entités extraites
        """
        try:
            return {
                'skills': self.extract_skills(text),
                'education': self.extract_education(text),
                'experience': self.extract_experience(text),
                'certifications': self.extract_certifications(text)
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des entités: {e}")
            return {
                'skills': [],
                'education': [],
                'experience': [],
                'certifications': []
            }
    
    def _extract_institution(self, text: str) -> Optional[str]:
        """Extrait le nom de l'institution."""
        # Recherche de mots-clés d'institutions
        patterns = [
            r'(?:université|university|école|school|institut|college|faculté|faculty)',
            r'(?:\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
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

# Fonction utilitaire pour l'extraction
def extract_entities_from_cv(cv_text: str) -> Dict[str, any]:
    """
    Fonction utilitaire pour extraire les entités d'un CV.
    
    Args:
        cv_text (str): Texte du CV
        
    Returns:
        Dict[str, any]: Entités extraites
    """
    extractor = EntityExtractor()
    return extractor.extract_all_entities(cv_text)
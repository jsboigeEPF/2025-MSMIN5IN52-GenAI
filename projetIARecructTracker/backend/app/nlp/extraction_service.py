from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from app.core.mistral_client import mistral_client
from loguru import logger
import re


class ExtractedEntity(BaseModel):
    """Modèle pour les entités extraites d'un email"""
    company_name: Optional[str] = Field(None, description="Nom de l'entreprise")
    job_title: Optional[str] = Field(None, description="Intitulé du poste")
    contact_name: Optional[str] = Field(None, description="Nom du contact/recruteur")
    contact_email: Optional[str] = Field(None, description="Email du contact")
    location: Optional[str] = Field(None, description="Localisation du poste")
    salary_range: Optional[str] = Field(None, description="Fourchette de salaire")
    contract_type: Optional[str] = Field(None, description="Type de contrat")
    date_mentioned: Optional[str] = Field(None, description="Date mentionnée dans l'email")
    required_skills: List[str] = Field(default_factory=list, description="Compétences requises")
    status_keywords: List[str] = Field(default_factory=list, description="Mots-clés de statut détectés")
    confidence: float = Field(0.0, description="Score de confiance de l'extraction")


class EmailExtractionService:
    """Service d'extraction d'entités depuis les emails"""
    
    def __init__(self):
        self.extraction_schema = {
            "company_name": {
                "type": "string",
                "description": "Nom complet de l'entreprise ou organisation (ex: 'Google', 'Microsoft', 'Airbus')"
            },
            "job_title": {
                "type": "string", 
                "description": "Intitulé exact du poste mentionné (ex: 'Développeur Full-Stack', 'Data Scientist Senior')"
            },
            "contact_name": {
                "type": "string",
                "description": "Nom complet de la personne de contact (prénom + nom si disponible)"
            },
            "contact_email": {
                "type": "string",
                "description": "Adresse email du recruteur ou contact RH"
            },
            "location": {
                "type": "string",
                "description": "Lieu de travail (ville, région, 'Remote', 'Télétravail', etc.)"
            },
            "salary_range": {
                "type": "string",
                "description": "Fourchette de salaire mentionnée (ex: '45-55K€', '60000-70000$')"
            },
            "contract_type": {
                "type": "string",
                "description": "Type de contrat (CDI, CDD, Stage, Alternance, Freelance, etc.)"
            },
            "date_mentioned": {
                "type": "string",
                "description": "Date importante (entretien, début de poste, deadline) au format ISO si possible"
            },
            "required_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Compétences techniques ou qualifications requises mentionnées"
            },
            "status_keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Mots-clés de statut (accusé réception, refus, entretien, offre, etc.)"
            },
            "confidence": {
                "type": "number",
                "description": "Score de confiance de l'extraction entre 0 et 1"
            }
        }
        
        # Contexte amélioré pour Mistral
        self.extraction_context = """
Tu es un assistant IA spécialisé dans l'extraction d'informations structurées depuis des emails de recrutement.

🎯 OBJECTIF: Extraire toutes les informations pertinentes pour suivre une candidature.

📋 INSTRUCTIONS D'EXTRACTION:

1. **company_name**: 
   - Cherche dans: signature, domaine email, corps du message
   - Formats: "Entreprise X", "Société Y", domaine "@company.com"
   - Normalise: "google.com" → "Google"

2. **job_title**:
   - Intitulé exact du poste mentionné
   - Ex: "Développeur Python", "Chef de projet", "Data Engineer"
   - Pas de synonymes, titre exact

3. **contact_name**:
   - Nom du recruteur/RH dans signature ou corps
   - Format: "Prénom NOM" si disponible
   - Ex: "Marie DUPONT", "John Smith"

4. **contact_email**:
   - Email direct du recruteur (pas no-reply)
   - Format valide: xyz@domain.com

5. **location**:
   - Lieu de travail mentionné
   - Formats acceptés: "Paris", "Lyon, France", "Remote", "Télétravail", "Paris 75"

6. **salary_range**:
   - Fourchette ou montant exact
   - Ex: "45-50K€", "3000€/mois", "60000$ annually"

7. **contract_type**:
   - Type: CDI, CDD, Stage, Alternance, Freelance, Intérim, etc.
   - En français ou anglais selon l'email

8. **date_mentioned**:
   - Dates importantes: entretien, début, deadline
   - Privilégie format ISO (YYYY-MM-DD) si possible
   - Ex: "2025-03-15", "15/03/2025", "March 15"

9. **required_skills**:
   - Technologies, langages, outils mentionnés
   - Ex: ["Python", "React", "AWS", "Agile"]
   - Max 8-10 compétences principales

10. **status_keywords**:
    - Mots-clés de statut détectés
    - Ex: ["accusé de réception", "entretien", "refus"]

11. **confidence**:
    - 0.9-1.0: Beaucoup d'infos claires et structurées
    - 0.7-0.9: Infos principales présentes
    - 0.5-0.7: Quelques infos, certaines incertaines
    - <0.5: Peu d'infos exploitables

⚠️ SI UNE INFO N'EST PAS PRÉSENTE: retourne null/None, ne devine pas.
⚠️ SOIS PRÉCIS: extrais exactement ce qui est écrit, pas d'interprétation.
"""
    
    async def extract_entities(
        self, 
        email_subject: str, 
        email_body: str, 
        sender_email: str = ""
    ) -> ExtractedEntity:
        """
        Extraire les entités d'un email avec Mistral AI
        
        Args:
            email_subject: Sujet de l'email
            email_body: Corps de l'email
            sender_email: Adresse de l'expéditeur
            
        Returns:
            ExtractedEntity avec les informations extraites
        """
        # Combiner les informations disponibles
        full_text = f"Expéditeur: {sender_email}\nSujet: {email_subject}\n\nCorps:\n{email_body}"
        
        # Essayer d'abord l'extraction avec des règles simples
        simple_extraction = self._extract_with_rules(email_subject, email_body, sender_email)
        
        # Si les règles simples sont insuffisantes, utiliser Mistral
        if simple_extraction.confidence < 0.6:
            logger.info("Simple rules insufficient, calling Mistral AI for extraction")
            mistral_extraction = await self._extract_with_mistral(full_text)
            if mistral_extraction:
                # Combiner les résultats (privilégier Mistral si disponible)
                return self._merge_extractions(simple_extraction, mistral_extraction)
        
        return simple_extraction
    
    def _extract_with_rules(
        self, 
        subject: str, 
        body: str, 
        sender_email: str
    ) -> ExtractedEntity:
        """
        Extraction basique avec des règles regex et mots-clés
        """
        extracted = ExtractedEntity()
        
        # Extraction du nom d'entreprise depuis l'email
        if sender_email:
            domain = sender_email.split('@')[-1].lower()
            # Nettoyer le domaine pour obtenir le nom d'entreprise probable
            company_guess = domain.split('.')[0]
            if company_guess not in ['gmail', 'yahoo', 'hotmail', 'outlook']:
                extracted.company_name = company_guess.title()
        
        # Extraction de mots-clés de statut
        status_patterns = {
            'acknowledgment': [
                r'accusé de réception', r'reçu votre candidature', r'received your application',
                r'nous avons bien reçu', r'thank you for applying'
            ],
            'rejection': [
                r'ne donnerons pas suite', r'candidature non retenue', r'not selected',
                r'unfortunately', r'regret to inform', r'other candidates'
            ],
            'interview': [
                r'entretien', r'interview', r'convocation', r'rencontrer',
                r'meeting', r'disponibilité', r'availability'
            ],
            'offer': [
                r'offre', r'proposition d\'embauche', r'offer', r'congratulations',
                r'pleased to offer', r'job offer'
            ]
        }
        
        full_text = f"{subject} {body}".lower()
        detected_keywords = []
        
        for status, patterns in status_patterns.items():
            for pattern in patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    detected_keywords.append(status)
                    break
        
        extracted.status_keywords = list(set(detected_keywords))
        
        # Extraction de dates (format simple)
        date_patterns = [
            r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}',
            r'\d{1,2} \w+ \d{4}',
            r'\w+ \d{1,2}, \d{4}'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, full_text)
            if match:
                extracted.date_mentioned = match.group()
                break
        
        # Calculer un score de confiance basique
        confidence = 0.0
        if extracted.company_name:
            confidence += 0.3
        if extracted.status_keywords:
            confidence += 0.4
        if extracted.date_mentioned:
            confidence += 0.2
        if sender_email and '@' in sender_email:
            confidence += 0.1
        
        extracted.confidence = min(confidence, 1.0)
        
        return extracted
    
    async def _extract_with_mistral(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extraction avec Mistral AI en mode JSON structuré
        """
        try:
            result = await mistral_client.extract_structured_data(
                text=text,
                extraction_schema=self.extraction_schema,
                context=self.extraction_context  # ✅ Ajout du contexte détaillé
            )
            return result
        except Exception as e:
            logger.error(f"Error in Mistral extraction: {e}")
            return None
    
    def _merge_extractions(
        self, 
        simple: ExtractedEntity, 
        mistral: Dict[str, Any]
    ) -> ExtractedEntity:
        """
        Fusionner les résultats d'extraction simple et Mistral (privilégier Mistral)
        """
        # Privilégier Mistral pour la plupart des champs
        merged = ExtractedEntity(
            company_name=mistral.get('company_name') or simple.company_name,
            job_title=mistral.get('job_title') or simple.job_title,
            contact_name=mistral.get('contact_name') or simple.contact_name,
            contact_email=mistral.get('contact_email') or simple.contact_email,
            location=mistral.get('location') or simple.location,
            salary_range=mistral.get('salary_range') or simple.salary_range,
            contract_type=mistral.get('contract_type') or simple.contract_type,
            date_mentioned=mistral.get('date_mentioned') or simple.date_mentioned,
            required_skills=mistral.get('required_skills', []) + simple.required_skills,
            status_keywords=mistral.get('status_keywords', []) + simple.status_keywords,
            confidence=max(mistral.get('confidence', 0), simple.confidence)
        )
        
        # Déduplication des listes
        merged.required_skills = list(set(merged.required_skills))
        merged.status_keywords = list(set(merged.status_keywords))
        
        return merged

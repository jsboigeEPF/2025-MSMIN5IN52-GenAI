from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field
from enum import Enum
from app.core.mistral_client import mistral_client
from app.core.config import settings
from loguru import logger
import re
import yaml
import os


class EmailType(str, Enum):
    """Types d'emails de recrutement"""
    ACKNOWLEDGMENT = "ACK"  # Accusé de réception
    REJECTED = "REJECTED"   # Refus
    INTERVIEW = "INTERVIEW" # Convocation entretien
    OFFER = "OFFER"        # Offre d'emploi
    REQUEST = "REQUEST"    # Demande de documents/infos
    OTHER = "OTHER"        # Autre type


class ClassificationResult(BaseModel):
    """Résultat de classification d'un email"""
    email_type: EmailType
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: Optional[str] = None
    keywords_matched: List[str] = Field(default_factory=list)
    method_used: str = "rules"  # "rules" ou "mistral"


class EmailClassificationService:
    """Service de classification des emails de recrutement"""
    
    def __init__(self):
        self.rules_path = settings.CLASSIFICATION_RULES_PATH
        self.rules = self._load_classification_rules()
        
        # Patterns d'exclusion pour filtrer les newsletters et notifications
        self.exclusion_patterns = [
            # Domaines commerciaux
            r'@(uber|snapchat|vercel|teamviewer|netflix|spotify|amazon|ebay)\.com',
            r'@mails\.(teamviewer|uber|snapchat)',
            r'@(noreply|no-reply|notifications?|newsletter)',
            r'privaterelay\.appleid\.com',
            
            # Mots-clés marketing
            r'newsletter', r'promo(tion)?', r'offre? spéciale?',
            r'réduction', r'-\d+[€$£]', r'commande', r'livraison',
            r'abonnement', r'subscription', r'unsubscribe',
            r'se désabonner', r'marketing@', r'ads@'
        ]
    
    def _load_classification_rules(self) -> Dict[str, List[str]]:
        """Charger les règles de classification depuis les fichiers YAML"""
        rules = {
            EmailType.ACKNOWLEDGMENT: [
                # Français
                r'accusé de réception', r'avons bien reçu', r'reçu votre candidature',
                r'prise en compte', r'candidature enregistrée', r'merci pour votre candidature',
                # Anglais  
                r'received your application', r'thank you for applying', r'application received',
                r'acknowledgment', r'confirm receipt', r'thank you for your interest'
            ],
            EmailType.REJECTED: [
                # Français
                r'ne donnerons pas suite', r'candidature non retenue', r'ne sera pas retenue',
                r'autres candidats', r'profil différent', r'malheureusement',
                r'nous regrettons', r'ne correspond pas',
                # Anglais
                r'unfortunately', r'not selected', r'other candidates', r'not proceed',
                r'regret to inform', r'unable to offer', r'not successful', r'declined'
            ],
            EmailType.INTERVIEW: [
                # Français
                r'entretien', r'convocation', r'rencontrer', r'disponibilité',
                r'rdv', r'rendez-vous', r'planifier', r'échange téléphonique',
                # Anglais
                r'interview', r'meeting', r'schedule', r'availability',
                r'phone call', r'video call', r'zoom', r'teams'
            ],
            EmailType.OFFER: [
                # Français
                r'offre', r'proposition d\'embauche', r'contrat', r'félicitations',
                r'heureux de vous proposer', r'accepter le poste',
                # Anglais
                r'job offer', r'offer letter', r'congratulations', r'pleased to offer',
                r'contract', r'employment offer', r'accept the position'
            ],
            EmailType.REQUEST: [
                # Français
                r'documents', r'pièces jointes', r'compléter', r'informations supplémentaires',
                r'cv mis à jour', r'portfolio', r'références',
                # Anglais
                r'additional information', r'documents', r'portfolio', r'references',
                r'updated resume', r'complete', r'provide'
            ]
        }
        
        return rules
    
    async def classify_email(
        self, 
        subject: str, 
        body: str, 
        sender_email: str = ""
    ) -> ClassificationResult:
        """
        Classifier un email selon son type
        
        Args:
            subject: Sujet de l'email
            body: Corps de l'email  
            sender_email: Email de l'expéditeur
            
        Returns:
            ClassificationResult avec le type et la confiance
        """
        # Combiner sujet, corps et expéditeur pour l'analyse
        full_text = f"{sender_email} {subject} {body}".lower()
        
        # Étape 1: Vérifier si c'est une newsletter/notification (exclusion rapide)
        if self._is_excluded_email(full_text):
            return ClassificationResult(
                email_type=EmailType.OTHER,
                confidence=0.95,
                reasoning="Excluded: Newsletter, notification or marketing email",
                method_used="exclusion_filter"
            )
        
        # Étape 2: Essayer avec les règles
        rules_result = self._classify_with_rules(full_text)
        
        # Étape 3: Si la confiance est faible, utiliser Mistral AI
        if rules_result.confidence < settings.CLASSIFICATION_CONFIDENCE_THRESHOLD:
            logger.info(f"Rules confidence {rules_result.confidence} below threshold, trying Mistral AI")
            mistral_result = await self._classify_with_mistral(subject, body)
            
            if mistral_result and mistral_result.confidence > rules_result.confidence:
                mistral_result.method_used = "mistral"
                return mistral_result
        
        return rules_result
    
    def _is_excluded_email(self, text: str) -> bool:
        """
        Vérifier si l'email doit être exclu (newsletter, notification, etc.)
        """
        for pattern in self.exclusion_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _classify_with_rules(self, text: str) -> ClassificationResult:
        """
        Classification basée sur les règles regex
        """
        best_match = ClassificationResult(
            email_type=EmailType.OTHER,
            confidence=0.0,
            method_used="rules"
        )
        
        for email_type, patterns in self.rules.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matches.append(pattern)
            
            if matches:
                # Calculer la confiance basée sur le nombre de matches
                confidence = min(len(matches) * 0.3 + 0.4, 1.0)
                
                if confidence > best_match.confidence:
                    best_match = ClassificationResult(
                        email_type=email_type,
                        confidence=confidence, 
                        keywords_matched=matches,
                        method_used="rules",
                        reasoning=f"Matched {len(matches)} keywords for {email_type}"
                    )
        
        return best_match
    
    async def _classify_with_mistral(
        self, 
        subject: str, 
        body: str
    ) -> Optional[ClassificationResult]:
        """
        Classification avec Mistral AI
        """
        if not mistral_client.is_available():
            return None
        
        try:
            categories = [e.value for e in EmailType]
            context = """
Tu es un expert en analyse d'emails de recrutement. Ton rôle est de classifier précisément les emails liés aux candidatures d'emploi.

🎯 RÈGLES DE CLASSIFICATION STRICTES:

1️⃣ EMAILS À EXCLURE (→ OTHER):
   - Newsletters commerciales (Uber, Snapchat, LinkedIn notifications, etc.)
   - Notifications de services (réseaux sociaux, e-commerce)
   - Emails marketing, promotions, publicités
   - Confirmations de commande, livraison
   - Alertes techniques ou sécurité
   - Invitations à des événements non-recrutement
   - Messages automatiques génériques

2️⃣ EMAILS DE RECRUTEMENT (analyser avec précision):
   
   📧 ACK (Accusé de Réception):
      - Confirmation de réception de candidature
      - "Nous avons bien reçu votre CV"
      - Remerciement pour la candidature
      ⚠️ DOIT explicitement mentionner: candidature, CV, application
   
   ❌ REJECTED (Refus):
      - Refus clair et définitif
      - "Candidature non retenue", "profil ne correspond pas"
      - "Autres candidats", "ne donnerons pas suite"
      ⚠️ Mots clés: malheureusement, regret, unable, unfortunately
   
   📞 INTERVIEW (Entretien):
      - Convocation à un entretien
      - Demande de disponibilité pour rencontre
      - Confirmation de RDV téléphonique/vidéo
      ⚠️ Mots clés: entretien, interview, rencontrer, disponibilité, RDV
   
   💼 OFFER (Offre d'emploi):
      - Proposition d'embauche concrète
      - Offre de contrat
      - "Heureux de vous proposer le poste"
      ⚠️ Mots clés: félicitations, offre, contrat, embauche, accepter
   
   📋 REQUEST (Demande d'infos):
      - Demande de documents supplémentaires
      - Besoin de compléter le dossier
      - Demande de références, portfolio, CV mis à jour
      ⚠️ Contexte: processus de candidature en cours

3️⃣ ANALYSE CONTEXTUELLE:
   - Regarde l'expéditeur: est-ce un service RH, recrutement, careers@ ?
   - Analyse le ton: formel (recrutement) vs marketing (promotion)
   - Vérifie les mentions: poste, candidature, CV, application
   - Si aucun contexte de recrutement → OTHER

4️⃣ NIVEAU DE CONFIANCE:
   - 0.9-1.0: Mots-clés très clairs et contexte évident
   - 0.7-0.9: Bonne correspondance avec quelques ambiguïtés
   - 0.5-0.7: Correspondance partielle, contexte incertain
   - <0.5: Très incertain ou probablement OTHER

⚠️ EN CAS DE DOUTE: privilégie OTHER plutôt qu'une mauvaise classification.
"""
            
            full_text = f"Sujet: {subject}\n\nCorps:\n{body}"
            
            result = await mistral_client.classify_text(
                text=full_text,
                categories=categories,
                context=context
            )
            
            if result:
                return ClassificationResult(
                    email_type=EmailType(result.get('category', 'OTHER')),
                    confidence=result.get('confidence', 0.0),
                    reasoning=result.get('reasoning'),
                    method_used="mistral"
                )
        
        except Exception as e:
            logger.error(f"Error in Mistral classification: {e}")
        
        return None
    
    def get_status_from_email_type(self, email_type: EmailType) -> str:
        """
        Convertir le type d'email en statut de candidature
        """
        mapping = {
            EmailType.ACKNOWLEDGMENT: "ACKNOWLEDGED",
            EmailType.REJECTED: "REJECTED", 
            EmailType.INTERVIEW: "INTERVIEW",
            EmailType.OFFER: "OFFER",
            EmailType.REQUEST: "SCREENING",
            EmailType.OTHER: None  # Pas de changement de statut
        }
        
        return mapping.get(email_type)
    
    async def classify_and_suggest_status(
        self, 
        subject: str, 
        body: str, 
        current_status: str = "APPLIED"
    ) -> Tuple[ClassificationResult, Optional[str]]:
        """
        Classifier un email et suggérer un nouveau statut de candidature
        
        Returns:
            Tuple (classification_result, suggested_status)
        """
        classification = await self.classify_email(subject, body)
        suggested_status = self.get_status_from_email_type(classification.email_type)
        
        # Logique de transition de statut
        if suggested_status and self._is_valid_transition(current_status, suggested_status):
            return classification, suggested_status
        
        return classification, None
    
    def _is_valid_transition(self, current: str, new: str) -> bool:
        """
        Vérifier si la transition de statut est valide
        """
        # Définir les transitions valides
        valid_transitions = {
            "APPLIED": ["ACKNOWLEDGED", "REJECTED", "INTERVIEW", "SCREENING"],
            "ACKNOWLEDGED": ["REJECTED", "INTERVIEW", "SCREENING", "OFFER"],
            "SCREENING": ["REJECTED", "INTERVIEW", "OFFER"],
            "INTERVIEW": ["REJECTED", "OFFER", "ON_HOLD"],
            "OFFER": ["REJECTED"],  # Peut être rejetée après négociation
        }
        
        return new in valid_transitions.get(current, [])

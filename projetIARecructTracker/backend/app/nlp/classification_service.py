from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field
from enum import Enum
from app.core.mistral_client import mistral_client
from app.core.gemini_client import gemini_client
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
        
        # 🚨 Patterns d'exclusion RENFORCÉS pour filtrer newsletters et notifications
        self.exclusion_patterns = [
            # === DOMAINES COMMERCIAUX CONNUS ===
            r'@(uber|snapchat|vercel|teamviewer|netflix|spotify|amazon|ebay)\.com',
            r'@(unidays|zalando|carrefour|auchan|leclerc|fnac)\.com',
            r'@mails\.(teamviewer|uber|snapchat|zalando|prive)',
            r'@(noreply|no-reply|notifications?|newsletter|info|contact)@',
            r'@(marketing|promo|offers|deals|sales)@',
            r'privaterelay\.appleid\.com',
            
            # === DOMAINES DE RÉSEAUX SOCIAUX ===
            r'@(linkedin|facebook|twitter|instagram|tiktok)\.com',
            r'@notify\.(linkedin|facebook|twitter)',
            
            # === PLATEFORMES D'EMPLOI (notifications, pas candidatures) ===
            r'@(indeed|monster|glassdoor|jobteaser)\.com.*(?=notification|alerte|alert)',
            
            # === MOTS-CLÉS MARKETING EXPLICITES ===
            r'\b(newsletter|promotional|promo(tion)?)\b',
            r'\boffre[s]? (spéciale|exclusive|limitée|promotionnelle)\b',
            r'\b(réduction|discount|soldes?|vente[s]? privée[s]?)\b',
            r'\b(code promo|coupon|bon de réduction)\b',
            r'\b-\d{1,2}[€$£%]\b',  # -20€, -50%
            
            # === TERMES E-COMMERCE ===
            r'\b(commande|livraison|colis|panier|paiement|facture)\b',
            r'\b(votre achat|votre commande|tracking|suivi de commande)\b',
            
            # === ABONNEMENTS ===
            r'\b(abonnement|subscription|s\'abonner|subscribe)\b',
            r'\b(unsubscribe|désabonner|se désinscrire)\b',
            
            # === ÉVÉNEMENTS NON-RECRUTEMENT ===
            r'\b(webinar|webinaire|conférence|salon)\b(?!.*(recrutement|carrière|emploi|entretien))',
            r'\binvitation\b.*(?=événement|event|billets?|réservation)(?!.*(entretien|interview))',  # Invitation SAUF entretien
            r'\b(réservation|billets?)\b(?!.*(entretien|interview))',
            
            # === INDICATEURS AUTOMATIQUES ===
            r'\[automatic\]|\[auto\]|auto-reply|réponse automatique',
            r'do.not.reply|ne.pas.repondre',
            
            # === SUJETS SUSPECTS (patterns dans le sujet) ===
            r'^\s*(re:|fwd:|tr:|visuel|info|newsletter)',
            r'vive les bons plans|c\'est parti pour',
            r'votre sélection du|top \d+ de|meilleures? offres?'
        ]
        
        # 🎯 Mots-clés OBLIGATOIRES pour les vrais emails de recrutement
        self.recruitment_indicators = [
            # Termes recrutement explicites
            r'\b(candidature|application|cv|curriculum vitae|resume)\b',
            r'\b(poste|position|job|emploi|opportunité|opportunity)\b',
            r'\b(recrutement|recruitment|hiring|embauche)\b',
            r'\b(entretien|interview|rendez-vous|rdv)\b',
            r'\b(offre d\'emploi|job offer|proposition)\b',
            
            # Contexte RH
            r'\b(ressources humaines|rh|human resources|hr)\b',
            r'\b(recruteur|recruiter|talent acquisition)\b',
            
            # Domaines RH spécifiques
            r'@(careers|recrutement|rh|hr|talent)[\.-]',
            r'careers@|recrutement@|rh@|hr@'
        ]
    
    def _load_classification_rules(self) -> Dict[str, List[str]]:
        """Charger les règles de classification depuis les fichiers YAML"""
        rules = {
            EmailType.ACKNOWLEDGMENT: [
                # Français - Accusé de réception SANS action/décision
                r'accusé de réception', r'avons bien reçu', r'reçu votre candidature',
                r'prise en compte', r'candidature enregistrée', 
                r'merci pour votre candidature', r'merci d\'avoir postulé',
                r'confirmation.*candidature', r'dossier.*étude',
                r'candidature.*cours.*traitement',
                # Anglais  
                r'received your application', r'thank you for applying', 
                r'application received', r'acknowledgment', r'confirm receipt', 
                r'thank you for your interest', r'application.*under review'
            ],
            EmailType.REJECTED: [
                # Français - Refus EXPLICITE
                r'ne donnerons pas suite', r'candidature non retenue', r'ne sera pas retenue',
                r'autres candidats', r'profil différent', r'malheureusement.*ne',
                r'nous regrettons', r'ne correspond pas', r'avons retenu d\'autres',
                # Anglais
                r'unfortunately.*not', r'not selected', r'other candidates', r'not proceed',
                r'regret to inform', r'unable to offer', r'not successful', r'declined'
            ],
            EmailType.INTERVIEW: [
                # Français - Actions de suivi (PRIORITÉ HAUTE - mettre AVANT ACK)
                # ⚠️ IMPORTANT: Exclure les contextes de refus avec negative lookahead
                r'suite à votre candidature(?!.*\b(ne donnerons pas|malheureusement|regret|pas retenue|refus)\b)',
                r'(?<!ne )donnons suite',  # "donnons suite" MAIS PAS "ne donnerons pas suite"
                r'revenons vers vous(?!.*\b(malheureusement|regret)\b)',
                r'faire suite', r'suite.*dossier', r'suite.*votre.*profil',
                # Français - Invitation/Convocation EXPLICITE
                r'invitation.*entretien', r'convocation.*entretien', 
                r'souhaitons vous rencontrer', r'rencontrer.*entretien',
                r'rendez-vous.*entretien', r'planifier.*entretien',
                r'disponibilité.*entretien', r'échange.*entretien',
                r'entretien.*téléphonique', r'entretien.*prévu',
                # Patterns génériques SEULEMENT si contexte clair
                r'\bentretien\b(?!.*candidature.*reçu)',  # "entretien" SAUF si juste accusé
                # Anglais
                r'invitation.*interview', r'schedule.*interview', 
                r'interview.*scheduled', r'would like to meet',
                r'phone call.*discuss', r'video call', r'zoom.*interview', 
                r'teams.*meeting', r'following up on your application',
                r'following your application', r'regarding your application'
            ],
            EmailType.OFFER: [
                # Français - Félicitations (signal TRÈS fort d'offre/progression positive)
                r'félicitations.*\b(offre|poste|sélectionné|retenu|candidature)\b',
                r'félicitations.*avance',  # "félicitations votre candidature avance"
                r'\bfélicitations\b(?!.*\b(pas retenu|refus|malheureusement)\b)',  # Félicitations seul (sans refus)
                # Français - Offre/Proposition EXPLICITE
                r'heureux de vous (proposer|offrir)', r'offre.*contrat',
                r'proposition d\'embauche', r'vous proposer le poste',
                r'avez été (retenu|sélectionné)', 
                r'(candidature|profil|dossier).*avance',  # Candidature/profil avance
                r'accepter (le poste|notre offre)',
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
        Classifier un email selon son type avec filtrage renforcé
        
        Args:
            subject: Sujet de l'email
            body: Corps de l'email  
            sender_email: Email de l'expéditeur
            
        Returns:
            ClassificationResult avec le type et la confiance
        """
        # Combiner sujet, corps et expéditeur pour l'analyse
        full_text = f"{sender_email} {subject} {body}".lower()
        
        # 🚨 ÉTAPE 1: Filtre d'exclusion (newsletters, marketing, etc.)
        if self._is_excluded_email(full_text):
            return ClassificationResult(
                email_type=EmailType.OTHER,
                confidence=0.95,
                reasoning="Excluded: Newsletter, notification, marketing or non-recruitment email",
                method_used="exclusion_filter"
            )
        
        # 🎯 ÉTAPE 2: Vérifier qu'il y a des indicateurs de recrutement
        if not self._has_recruitment_indicators(full_text):
            return ClassificationResult(
                email_type=EmailType.OTHER,
                confidence=0.85,
                reasoning="No clear recruitment indicators found (no mention of job, candidature, CV, etc.)",
                method_used="recruitment_filter"
            )
        
        # ✅ ÉTAPE 3: Classification avec règles
        rules_result = self._classify_with_rules(full_text)
        
        # 🤖 ÉTAPE 4: Si confiance faible, utiliser IA (Mistral puis Gemini en fallback)
        # ⚠️ Seuil abaissé à 0.6 pour éviter trop d'appels IA (quota limité)
        if rules_result.confidence < 0.6:
            logger.info(f"Rules confidence {rules_result.confidence} below threshold, trying AI classification")
            
            # Essayer d'abord Mistral
            ai_result = await self._classify_with_ai(subject, body, sender_email)
            
            if ai_result and ai_result.confidence > rules_result.confidence:
                return ai_result
        
        return rules_result
    
    def _is_excluded_email(self, text: str) -> bool:
        """
        Vérifier si l'email doit être exclu (newsletter, notification, marketing, etc.)
        Retourne True si l'email doit être REJETÉ
        """
        for pattern in self.exclusion_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.debug(f"Exclusion pattern matched: {pattern}")
                return True
        return False
    
    def _has_recruitment_indicators(self, text: str) -> bool:
        """
        Vérifier qu'il y a au moins un indicateur clair de recrutement
        Retourne True si l'email semble être lié au recrutement
        """
        for pattern in self.recruitment_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                logger.debug(f"Recruitment indicator found: {pattern}")
                return True
        
        logger.debug("No recruitment indicators found")
        return False
        return False
    
    def _classify_with_rules(self, text: str) -> ClassificationResult:
        """
        Classification basée sur les règles regex avec système de priorité
        
        Priorité (du plus spécifique au plus général):
        1. OFFER (offre d'emploi - décision positive finale)
        2. REJECTED (refus - décision négative finale)
        3. INTERVIEW (entretien planifié - action concrète)
        4. REQUEST (demande documents)
        5. ACKNOWLEDGMENT (accusé réception)
        """
        # Ordre de priorité (du plus spécifique au plus général)
        # ⚠️ REJECTED avant INTERVIEW car un refus est une décision finale
        priority_order = [
            EmailType.OFFER,      # Offre = décision positive finale
            EmailType.REJECTED,   # Refus = décision négative finale (AVANT INTERVIEW)
            EmailType.INTERVIEW,  # Entretien = action concrète
            EmailType.REQUEST,    # Demande = action requise
            EmailType.ACKNOWLEDGMENT  # ACK = le plus générique
        ]
        
        # Collecter tous les matches
        all_matches = {}
        for email_type, patterns in self.rules.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matches.append(pattern)
            
            if matches:
                confidence = min(len(matches) * 0.3 + 0.4, 1.0)
                all_matches[email_type] = {
                    'matches': matches,
                    'confidence': confidence,
                    'count': len(matches)
                }
        
        # Si aucun match
        if not all_matches:
            return ClassificationResult(
                email_type=EmailType.OTHER,
                confidence=0.0,
                method_used="rules"
            )
        
        # Sélectionner selon la priorité et la confiance
        # Si INTERVIEW a au moins 1 match fort, privilégier même si ACK a plus de matches
        if EmailType.INTERVIEW in all_matches and all_matches[EmailType.INTERVIEW]['count'] >= 2:
            match_data = all_matches[EmailType.INTERVIEW]
            return ClassificationResult(
                email_type=EmailType.INTERVIEW,
                confidence=match_data['confidence'],
                keywords_matched=match_data['matches'],
                method_used="rules",
                reasoning=f"Matched {match_data['count']} INTERVIEW keywords (priority rule)"
            )
        
        # Sinon, suivre l'ordre de priorité
        for email_type in priority_order:
            if email_type in all_matches:
                match_data = all_matches[email_type]
                return ClassificationResult(
                    email_type=email_type,
                    confidence=match_data['confidence'],
                    keywords_matched=match_data['matches'],
                    method_used="rules",
                    reasoning=f"Matched {match_data['count']} keywords for {email_type}"
                )
        
        # Fallback (ne devrait jamais arriver)
        return ClassificationResult(
            email_type=EmailType.OTHER,
            confidence=0.0,
            method_used="rules"
        )
    
    async def _classify_with_ai(
        self, 
        subject: str, 
        body: str,
        sender_email: str = ""
    ) -> Optional[ClassificationResult]:
        """
        Classification avec IA : Mistral en priorité, Gemini en fallback
        """
        # Essayer d'abord Mistral
        if mistral_client.is_available():
            logger.info("Trying Mistral AI for classification")
            mistral_result = await self._classify_with_mistral(subject, body, sender_email)
            if mistral_result:
                logger.info(f"Mistral classification successful: {mistral_result.email_type.value} (confidence: {mistral_result.confidence})")
                return mistral_result
            else:
                logger.warning("Mistral AI failed or returned no result, trying Gemini fallback")
        
        # Fallback sur Gemini si Mistral échoue ou n'est pas disponible
        if gemini_client.is_available():
            logger.info("Trying Gemini AI for classification (fallback)")
            gemini_result = await self._classify_with_gemini(subject, body, sender_email)
            if gemini_result:
                logger.info(f"Gemini classification successful: {gemini_result.email_type.value} (confidence: {gemini_result.confidence})")
                return gemini_result
            else:
                logger.warning("Gemini AI also failed")
        
        logger.warning("No AI classification available (both Mistral and Gemini failed or unavailable)")
        return None
    
    async def _classify_with_mistral(
        self, 
        subject: str, 
        body: str,
        sender_email: str = ""
    ) -> Optional[ClassificationResult]:
        """
        Classification avancée avec Mistral AI et validation stricte
        """
        if not mistral_client.is_available():
            return None
        
        try:
            categories = [e.value for e in EmailType]
            context = """
Tu es un expert en analyse d'emails de recrutement. Ton rôle est de classifier UNIQUEMENT les emails vraiment liés aux candidatures d'emploi.

🚨 RÈGLE ABSOLUE: SI CE N'EST PAS CLAIREMENT UN EMAIL DE RECRUTEMENT → OTHER

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ EMAILS À REJETER IMMÉDIATEMENT (→ OTHER avec confiance 0.95):

   ❌ Newsletters commerciales:
      - "Vive les bons plans du mois"
      - "Offres exclusives", "Promotions", "Réductions"
      - Uber, Snapchat, Zalando, Carrefour, etc.
   
   ❌ Notifications de plateformes:
      - LinkedIn: "X a consulté votre profil"
      - Indeed: "Nouvelles offres correspondant à votre recherche"
      - Alertes emploi automatiques (pas une réponse à candidature)
   
   ❌ Marketing et e-commerce:
      - Confirmations de commande
      - Suivis de livraison
      - Invitations à des événements non-recrutement
      - Webinaires marketing
   
   ❌ Messages automatiques génériques:
      - "Do not reply"
      - Pas de contexte de candidature spécifique
      - Absence totale des mots: candidature, CV, poste, entretien

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ VRAIS EMAILS DE RECRUTEMENT (analyser le sous-type):

   ✅ PRÉREQUIS OBLIGATOIRES pour être considéré comme recrutement:
      - Mention explicite de: candidature, CV, application, poste, job
      - OU contexte clair d'un processus de recrutement en cours
      - OU expéditeur identifiable comme RH/recruteur (careers@, rh@, recruiter@)

   📧 ACK (Accusé de Réception) - Confiance 0.8-1.0:
      Mots-clés: "avons bien reçu votre candidature", "CV enregistré"
      Contexte: Confirmation automatique ou personnalisée de réception
      ⚠️ Ne PAS confondre avec: newsletter d'inscription, confirmation de commande
   
   ❌ REJECTED (Refus) - Confiance 0.85-1.0:
      Mots-clés: "candidature non retenue", "ne donnerons pas suite"
      Ton: Poli mais négatif, "malheureusement", "autres candidats"
      ⚠️ Doit être un REFUS CLAIR d'une candidature
   
   📞 INTERVIEW (Entretien) - Confiance 0.9-1.0:
      Mots-clés: "entretien", "disponibilité", "rencontrer", "rdv"
      Contexte: Invitation concrète à un échange
      ⚠️ Ne PAS confondre avec: invitation à un webinar marketing
   
   💼 OFFER (Offre d'emploi) - Confiance 0.95-1.0:
      Mots-clés: "offre d'emploi", "contrat", "félicitations"
      Contexte: Proposition formelle d'embauche
      ⚠️ Très rare, demande confiance maximale
   
   📋 REQUEST (Demande compléments) - Confiance 0.75-0.95:
      Mots-clés: "documents supplémentaires", "compléter votre dossier"
      Contexte: Processus de candidature en cours
      ⚠️ Doit concerner UNE candidature existante

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ ANALYSE MÉTHODIQUE:

   Étape 1 - Expéditeur:
   • Est-ce @careers, @rh, @recrutement, @hr ?
   • Est-ce un domaine commercial connu (Uber, Zalando) ?
   • Est-ce "noreply" ou "notifications" ?
   
   Étape 2 - Sujet:
   • Contient "candidature", "entretien", "poste" ?
   • OU contient "promo", "offre spéciale", "newsletter" ?
   
   Étape 3 - Corps:
   • Y a-t-il mention d'un CV, d'une candidature spécifique ?
   • Ton formel professionnel RH ou marketing commercial ?
   • Signature d'un recruteur identifié ?
   
   Étape 4 - Décision:
   • Si AUCUN indicateur de recrutement → OTHER (0.9)
   • Si doute → OTHER (0.7-0.85) - mieux vaut filtrer
   • Si indicateurs clairs → Sous-catégorie appropriée

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣ EXEMPLES DE RAISONNEMENT:

❌ "Vive les bons plans du mois d'octobre"
   → OTHER (0.95) - Newsletter marketing évidente

❌ "X a consulté votre profil LinkedIn"
   → OTHER (0.90) - Notification plateforme, pas candidature

❌ "Nouvelles offres correspondant à votre recherche"
   → OTHER (0.85) - Alerte automatique, pas réponse candidature

✅ "Nous avons bien reçu votre candidature pour le poste de Développeur"
   → ACK (0.95) - Accusé réception clair

✅ "Malheureusement votre candidature n'a pas été retenue"
   → REJECTED (0.95) - Refus explicite

✅ "Nous souhaitons vous rencontrer en entretien mardi prochain"
   → INTERVIEW (0.95) - Convocation entretien claire

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ PRIORITÉ: ÉVITER LES FAUX POSITIFS
   → En cas de doute, préférer OTHER plutôt qu'une mauvaise classification
   → Confiance < 0.7 pour les cas ambigus → OTHER
"""
            
            full_text = f"Expéditeur: {sender_email}\nSujet: {subject}\n\nCorps:\n{body[:1500]}"
            
            result = await mistral_client.classify_text(
                text=full_text,
                categories=categories,
                context=context
            )
            
            if result:
                category = EmailType(result.get('category', 'OTHER'))
                confidence = result.get('confidence', 0.0)
                reasoning = result.get('reasoning', '')
                
                # 🛡️ Validation supplémentaire: si Mistral dit ACK/REJECTED/INTERVIEW/OFFER
                # mais confiance < 0.7 → forcer OTHER
                if category != EmailType.OTHER and confidence < 0.7:
                    logger.warning(f"Low confidence {confidence} for {category}, forcing OTHER")
                    category = EmailType.OTHER
                    confidence = 0.75
                    reasoning = f"Low confidence for recruitment classification. Original: {reasoning}"
                
                return ClassificationResult(
                    email_type=category,
                    confidence=confidence,
                    reasoning=reasoning,
                    method_used="mistral"
                )
        
        except Exception as e:
            logger.error(f"Error in Mistral classification: {e}")
        
        return None
    
    async def _classify_with_gemini(
        self, 
        subject: str, 
        body: str,
        sender_email: str = ""
    ) -> Optional[ClassificationResult]:
        """
        Classification avec Gemini AI (Google) - Fallback si Mistral échoue
        """
        if not gemini_client.is_available():
            return None
        
        try:
            categories = [e.value for e in EmailType]
            
            # Contexte simplifié pour Gemini (plus concis)
            context = """Tu es un expert en classification d'emails de recrutement.

CATÉGORIES:
- ACK: Accusé de réception de candidature
- REJECTED: Refus de candidature
- INTERVIEW: Convocation/invitation à un entretien
- OFFER: Offre d'emploi/contrat
- REQUEST: Demande de documents/infos complémentaires
- OTHER: Tout le reste (newsletters, marketing, notifications, etc.)

RÈGLES STRICTES:
1. Si pas de mention de "candidature", "CV", "poste", "job" → OTHER
2. Si newsletter, marketing, notification → OTHER
3. Si invitation à entretien → INTERVIEW (pas OTHER)
4. Si accusé réception, confirmation candidature → ACK
5. En cas de doute → OTHER

Analyse l'email et retourne un JSON avec:
{"category": "CATEGORIE", "confidence": 0.XX, "reasoning": "explication courte"}"""
            
            full_text = f"Expéditeur: {sender_email}\nSujet: {subject}\n\nCorps:\n{body[:1500]}"
            
            result = await gemini_client.classify_text(
                text=full_text,
                categories=categories,
                context=context
            )
            
            if result:
                category = EmailType(result.get('category', 'OTHER'))
                confidence = result.get('confidence', 0.0)
                reasoning = result.get('reasoning', '')
                
                # 🛡️ Validation supplémentaire
                if category != EmailType.OTHER and confidence < 0.7:
                    logger.warning(f"Gemini: Low confidence {confidence} for {category}, forcing OTHER")
                    category = EmailType.OTHER
                    confidence = 0.75
                    reasoning = f"Low confidence for recruitment classification. Original: {reasoning}"
                
                return ClassificationResult(
                    email_type=category,
                    confidence=confidence,
                    reasoning=reasoning,
                    method_used="gemini"
                )
        
        except Exception as e:
            logger.error(f"Error in Gemini classification: {e}")
        
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

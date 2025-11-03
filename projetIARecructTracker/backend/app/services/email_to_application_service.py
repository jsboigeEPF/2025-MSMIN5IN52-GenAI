from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.models import Email, Application
from app.models.schemas import (
    ApplicationCreate, ApplicationStatus, EmailClassification
)
from app.services.application_service import ApplicationService
import re
import logging

logger = logging.getLogger(__name__)


class EmailToApplicationService:
    """
    Service pour créer automatiquement des candidatures à partir des emails classifiés
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.application_service = ApplicationService(db)

    def process_classified_emails(self) -> dict:
        """
        Traite tous les emails classifiés qui n'ont pas encore de candidature associée
        """
        # Récupérer les emails classifiés qui n'ont pas d'application_id
        emails_to_process = self.db.query(Email).filter(
            Email.application_id.is_(None),
            Email.classification.in_([
                EmailClassification.ACK.value,
                EmailClassification.INTERVIEW.value,
                EmailClassification.OFFER.value,
                EmailClassification.REQUEST.value,
                EmailClassification.REJECTED.value
            ])
        ).all()
        
        results = {
            "processed": 0,
            "created_applications": 0,
            "linked_applications": 0,
            "errors": []
        }
        
        for email in emails_to_process:
            try:
                application = self._create_or_link_application(email)
                if application:
                    email.application_id = application.id
                    self.db.commit()
                    results["processed"] += 1
                    if hasattr(application, '_newly_created'):
                        results["created_applications"] += 1
                    else:
                        results["linked_applications"] += 1
                        
            except Exception as e:
                logger.error(f"Erreur lors du traitement de l'email {email.id}: {str(e)}")
                results["errors"].append(f"Email {email.id}: {str(e)}")
                
        return results

    def _create_or_link_application(self, email: Email) -> Optional[Application]:
        """
        Crée une nouvelle candidature ou lie à une existante basé sur l'email
        """
        if not self._is_recruitment_email(email):
            logger.info(f"Email {email.id} ignoré: contenu non lié au recrutement.")
            return None

        # Extraire les informations de l'email
        company_name = self._extract_company_name(email) or "Entreprise non spécifiée"
        job_title = self._extract_job_title(email) or self._generate_job_title(email)
        
        if not email.user_id:
            logger.warning(f"Email {email.id} has no user_id; skipping automatic application creation.")
            return None
        
        # Chercher une candidature existante pour la même entreprise
        existing_application = self.db.query(Application).filter(
            Application.user_id == email.user_id,
            Application.company_name.ilike(f"%{company_name}%")
        ).first()
        
        if existing_application:
            # Lier à la candidature existante
            return existing_application
        
        # Créer une nouvelle candidature
        status = self._determine_status_from_classification(email.classification)
        
        application_data = ApplicationCreate(
            job_title=job_title,
            company_name=company_name,
            source=f"Email de {email.sender or 'expéditeur inconnu'}",
            location=None,
            status=status,
            notes=f"Créé automatiquement à partir de l'email: {(email.subject or 'Sujet inconnu')}\n\nContenu: {(email.snippet or email.raw_body or '')[:200]}..."
        )
        
        application = self.application_service.create_application(application_data, email.user_id)
        application._newly_created = True  # Marquer comme nouvellement créé
        
        return application

    def _is_recruitment_email(self, email: Email) -> bool:
        """
        Vérifie qu'un email est réellement lié au recrutement avant de créer une candidature.
        """
        subject = (email.subject or "").lower()
        content = (email.raw_body or email.snippet or "").lower()
        sender = (email.sender or "").lower()
        text = f"{subject} {content}"
        classification = (email.classification or "").upper()

        # Keywords positifs
        strong_keywords = [
            'candidature', 'recrutement', 'entretien', 'entervue',
            'cv', 'curriculum', 'profil', 'processus de recrutement',
            'application', 'applicant', 'hiring', 'candidate', 'interview',
            'talent acquisition', 'rh', 'ressources humaines', 'notre équipe rh',
            'thank you for applying', 'we received your application',
            'offre d\'emploi', 'offer letter', 'contrat de travail'
        ]
        weak_keywords = [
            'poste', 'position', 'emploi', 'job', 'mission', 'stage',
            'offre', 'opportunité', 'career', 'team', 'manager', 'full stack',
            'développeur', 'ingénieur', 'product', 'data', 'developer',
            'software', 'technique', 'rejoindre', 'process', 'hiring manager'
        ]
        recruitment_phrases = [
            'votre candidature', 'nous avons bien reçu votre candidature',
            'processus de recrutement', 'prochaine étape', 'merci pour votre candidature',
            'nous reviendrons vers vous', 'suite à votre candidature',
            'entretien prévu', 'planifier un entretien', 'convocation',
            'selection process', 'your application'
        ]

        # Keywords ou domaines à exclure
        exclusion_keywords = [
            'newsletter', 'promotion', 'bons plans', 'bon plan', 'événement', 'abonnement', 'publicité',
            'réduction', 'réductions', 'remise', 'remises', 'vente', 'soldes', 'billet', 'concert', 'festival',
            'avis client', 'parrainage', 'streaming', 'film', 'serie', 'évènement', 'code promo', 'livraison gratuite',
            'livraison express', 'cashback', 'catalogue', 'nouvelle collection', 'lookbook', 'magasin',
            'panier', 'shopping', 'promotionnelle', 'newsletter', 'bons d\'achat', 'bons d’achat',
            'unsubscribe', 'se désabonner', 'désabonner', 'préférences d\'abonnement', 'preferences marketing',
            'gérer mes préférences', 'view in browser', 'voir dans le navigateur', 'special offer',
            'exclusive offer', 'save up to', 'flash sale', 'soldes exceptionnelles', 'promo exceptionnelle',
            'financement disponible'
        ]
        exclusion_domains = [
            'spotify', 'netflix', 'youtube', 'deezer', 'ticketmaster',
            'allocine', 'eventbrite', 'meetup', 'mailchimp', 'sendgrid',
            'zalando', 'carrefour', 'myunidays', 'promopro', 'vente-privee',
            'groupon', 'promotions', 'journee-offres'
        ]
        marketing_patterns = [
            r'\b\d{1,2}\s*%(\s*de)?\s*(réduction|off)\b',
            r'\b(code|coupon)\s+promo\b',
            r'\boffre\s+(?:spéciale|exclusive)\b',
            r'\bvente\s+flash\b',
            r'\bacheter\s+maintenant\b',
            r'livraison\s+(?:gratuite|offerte)',
            r'\bprofitez-en\b',
            r'\bremise\s+exceptionnelle\b'
        ]

        text_with_sender = f"{text} {sender}"
        recruitment_classifications = {'ACK', 'INTERVIEW', 'OFFER', 'REQUEST', 'REJECTED'}
        classification_priority = classification in recruitment_classifications

        if any(domain in sender for domain in exclusion_domains):
            logger.info(f"Email {email.id} ignoré: domaine marketing détecté ({sender}).")
            return False
        marketing_keyword_hit = any(keyword in text_with_sender for keyword in exclusion_keywords)
        marketing_pattern_hit = any(re.search(pattern, text_with_sender) for pattern in marketing_patterns)

        strong_hits = sum(1 for keyword in strong_keywords if keyword in text)
        phrase_hits = sum(1 for phrase in recruitment_phrases if phrase in text)
        weak_hits = sum(1 for keyword in weak_keywords if keyword in text)

        has_recruitment_signal = strong_hits > 0 or phrase_hits > 0

        # Pour les emails sans mots forts, exiger au moins deux mots faibles ET une structure typique
        context_markers = [
            'candidature', 'candidat', 'candidate', 'recrutement', 'ressources humaines',
            'entrevue', 'entretien', 'processus de recrutement', 'talent', 'profil', 'cv',
            'application', 'applicant', 'hiring process', 'recruter', 'position ouverte',
            'stage', 'internship'
        ]
        context_match = weak_hits >= 2 and any(marker in text for marker in context_markers)

        if not has_recruitment_signal and not context_match:
            logger.info(f"Email {email.id} ignoré: aucun signal de recrutement détecté.")
            return False

        # Si des signaux marketing sont présents et qu'aucun mot fort n'est détecté,
        # considérer l'email comme marketing (sauf si classification prioritaire)
        if not classification_priority and (marketing_keyword_hit or marketing_pattern_hit):
            if not has_recruitment_signal:
                logger.info(f"Email {email.id} ignoré: signaux marketing sans mots forts de recrutement.")
                return False

        return True

    def _extract_company_name(self, email: Email) -> str:
        """
        Extrait le nom de l'entreprise à partir de l'email
        """
        sender_domain = email.sender.split('@')[-1] if '@' in email.sender else email.sender
        
        # Nettoyer le domaine
        company_name = sender_domain.replace('.com', '').replace('.fr', '').replace('.net', '')
        company_name = company_name.split('.')[0]  # Prendre seulement la première partie
        
        # Capitaliser
        company_name = company_name.capitalize()
        
        # Cas spéciaux pour des domaines connus
        domain_mapping = {
            'linkedin': 'LinkedIn',
            'gmail': 'Contact Gmail',
            'noreply': 'Contact Direct',
            'hr': 'Ressources Humaines',
            'jobs': 'Plateforme Emploi',
            'recrutement': 'Service Recrutement'
        }
        
        for key, value in domain_mapping.items():
            if key in sender_domain.lower():
                return value
                
        if not company_name:
            return "Entreprise non spécifiée"
        return company_name
    
    def _generate_job_title(self, email: Email) -> str:
        """
        Fallback pour générer un intitulé lisible lorsque l'extraction échoue
        """
        subject = (email.subject or "").strip()
        if subject:
            cleaned = re.sub(r'^(re|fw|fwd)\s*[:\-]\s*', '', subject, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r'\s+', ' ', cleaned)
            return cleaned[:120] or "Candidature"
        
        snippet = (email.snippet or "").strip()
        if snippet:
            first_line = snippet.splitlines()[0]
            return first_line[:120] or "Candidature"
        
        return "Candidature"

    def _extract_job_title(self, email: Email) -> Optional[str]:
        """
        Extrait le titre du poste à partir du sujet de l'email
        """
        subject = (email.subject or "").lower()
        
        # Patterns courants pour les titres de poste
        job_patterns = [
            r'poste\s+(?:de\s+)?([^-,\n]+)',
            r'(?:développeur|developer)\s+([^-,\n]+)',
            r'(?:ingénieur|engineer)\s+([^-,\n]+)',
            r'(?:lead|senior|junior)\s+([^-,\n]+)',
            r'candidature[^-]*-\s*([^-,\n]+)',
            r'offre\s+(?:d\'emploi\s+)?[^-]*-\s*([^-,\n]+)',
            r'entretien[^-]*-\s*([^-,\n]+)'
        ]
        
        for pattern in job_patterns:
            match = re.search(pattern, subject)
            if match:
                job_title = match.group(1).strip()
                # Nettoyer et capitaliser
                job_title = ' '.join(word.capitalize() for word in job_title.split())
                return job_title
                
        return None

    def _determine_status_from_classification(self, classification: str) -> ApplicationStatus:
        """
        Détermine le statut de la candidature basé sur la classification de l'email
        """
        status_mapping = {
            EmailClassification.INTERVIEW.value: ApplicationStatus.INTERVIEW,
            EmailClassification.OFFER.value: ApplicationStatus.OFFER,
            EmailClassification.REQUEST.value: ApplicationStatus.APPLIED,
            EmailClassification.REJECTED.value: ApplicationStatus.REJECTED,
            EmailClassification.ACK.value: ApplicationStatus.ACKNOWLEDGED
        }
        
        return status_mapping.get(classification, ApplicationStatus.APPLIED)

    def get_unprocessed_emails_count(self) -> int:
        """
        Retourne le nombre d'emails classifiés qui n'ont pas encore de candidature associée
        """
        return self.db.query(Email).filter(
            Email.application_id.is_(None),
            Email.classification.in_([
                EmailClassification.ACK.value,
                EmailClassification.INTERVIEW.value,
                EmailClassification.OFFER.value,
                EmailClassification.REQUEST.value,
                EmailClassification.REJECTED.value
            ])
        ).count()

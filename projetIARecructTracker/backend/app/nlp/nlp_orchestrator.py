from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.nlp.extraction_service import EmailExtractionService, ExtractedEntity
from app.nlp.classification_service import EmailClassificationService, ClassificationResult
from app.nlp.matching_service import EmailMatchingService, MatchingResult
from app.models.models import Email, Application
from loguru import logger
import re


class NLPOrchestrator:
    """
    Service orchestrateur pour tous les traitements NLP d'emails
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.extraction_service = EmailExtractionService()
        self.classification_service = EmailClassificationService()
        self.matching_service = EmailMatchingService(db)
    
    async def process_email_complete(
        self, 
        email: Email
    ) -> Dict[str, Any]:
        """
        Traitement NLP complet d'un email
        
        Returns:
            Dictionnaire avec tous les résultats du traitement
        """
        subject = email.subject or ""
        body = email.snippet or email.raw_body or ""
        sender = email.sender or ""
        
        results = {
            "email_id": str(email.id),
            "processing_success": True,
            "extraction": None,
            "classification": None,
            "matching": None,
            "actions_taken": []
        }
        
        try:
            # 1. Extraction d'entités
            logger.info(f"Starting NLP processing for email {email.id}")
            extraction = await self.extraction_service.extract_entities(subject, body, sender)
            results["extraction"] = extraction.model_dump()
            
            # 2. Classification
            classification = await self.classification_service.classify_email(subject, body, sender)
            results["classification"] = classification.model_dump()
            
            # Mettre à jour l'email avec la classification
            email.classification = classification.email_type.value
            
            # 3. Matching avec candidatures existantes (en filtrant par utilisateur)
            matches = await self.matching_service.find_matching_applications(
                subject, body, sender, email.user_id
            )
            results["matching"] = [m.model_dump() for m in matches]
            
            # 4. Actions automatiques
            actions = await self._take_automatic_actions(
                email, extraction, classification, matches
            )
            results["actions_taken"] = actions
            
            self.db.commit()
            logger.info(f"Successfully processed email {email.id} with NLP")
            
        except Exception as e:
            logger.error(f"Error in NLP processing for email {email.id}: {e}")
            results["processing_success"] = False
            results["error"] = str(e)
        
        return results
    
    async def _take_automatic_actions(
        self,
        email: Email,
        extraction: ExtractedEntity,
        classification: ClassificationResult,
        matches: List[MatchingResult]
    ) -> List[str]:
        """
        Prendre des actions automatiques basées sur les résultats NLP
        """
        actions = []
        
        try:
            # Action 1: Lier automatiquement à une candidature si confiance élevée
            if matches and matches[0].confidence > 0.8 and not email.application_id:
                best_match = matches[0]
                email.application_id = best_match.application_id
                actions.append(f"Auto-linked to application {best_match.application_id}")
            
            # Action 2: Mettre à jour le statut de candidature si approprié
            if email.application_id and classification.confidence > 0.7:
                new_status = self.classification_service.get_status_from_email_type(
                    classification.email_type
                )
                
                if new_status:
                    updated = await self._update_application_status(
                        email.application_id, 
                        new_status,
                        email.id
                    )
                    if updated:
                        actions.append(f"Updated application status to {new_status}")
            
            # Action 3: Créer des candidatures automatiques SEULEMENT si:
            # - Classification = email de recrutement (ACK, INTERVIEW, OFFER, REQUEST)
            # - Confiance élevée
            # - Pas de match existant
            recruitment_types = ["ACK", "INTERVIEW", "OFFER", "REQUEST", "REJECTED"]
            
            if (not matches and 
                classification.email_type.value in recruitment_types and  # Tous types de recrutement
                classification.confidence > 0.7):  # Confiance raisonnable
                
                # ⚠️ Créer même si extraction partielle (entreprise ou poste manquant)
                # Utiliser des valeurs par défaut si nécessaire
                company = extraction.company_name or "Entreprise non spécifiée"
                job = extraction.job_title or "Poste non spécifié"
                
                # Créer une nouvelle candidature automatiquement
                logger.info(f"Creating auto-application: {company} - {job} (type: {classification.email_type.value})")
                new_app = await self._create_application_from_extraction(extraction, email)
                if new_app:
                    actions.append(f"Created new application {new_app.id}")
                    email.application_id = new_app.id
                    
                    # Mettre à jour immédiatement le statut selon le type d'email
                    new_status = self.classification_service.get_status_from_email_type(
                        classification.email_type
                    )
                    if new_status:
                        await self._update_application_status(new_app.id, new_status, email.id)
                        actions.append(f"Set initial status to {new_status}")
            
            # ⚠️ Si email classé OTHER, ne rien faire d'automatique
            elif classification.email_type.value == "OTHER":
                logger.info(f"Email {email.id} classified as OTHER, skipping auto-actions")
                actions.append("Skipped: Email classified as non-recruitment (OTHER)")
            
            # Action 4: Planifier des rappels basés sur le type d'email
            reminder_scheduled = self._schedule_reminder(email, classification)
            if reminder_scheduled:
                actions.append("Scheduled follow-up reminder")
        
        except Exception as e:
            logger.error(f"Error taking automatic actions: {e}")
            actions.append(f"Error in automatic actions: {str(e)}")
        
        return actions
    
    async def _update_application_status(
        self, 
        app_id: str, 
        new_status: str, 
        email_id: str
    ) -> bool:
        """
        Mettre à jour le statut d'une candidature
        """
        from app.models.models import ApplicationEvent
        from datetime import datetime, timezone
        
        try:
            application = self.db.query(Application).filter(
                Application.id == app_id
            ).first()
            
            if not application:
                return False
            
            # Vérifier que c'est une transition valide
            if not self.classification_service._is_valid_transition(
                application.status, new_status
            ):
                return False
            
            old_status = application.status
            application.status = new_status
            application.updated_at = datetime.now(timezone.utc)
            
            # Créer un événement
            event = ApplicationEvent(
                application_id=app_id,
                event_type="STATUS_CHANGE",
                payload={
                    "previous_status": old_status,
                    "new_status": new_status,
                    "triggered_by_email": str(email_id),  # ⚠️ Convertir UUID en string pour JSON
                    "auto_classified": True
                }
            )
            self.db.add(event)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating application status: {e}")
            return False
    
    async def _create_application_from_extraction(
        self, 
        extraction: ExtractedEntity, 
        email: Email
    ) -> Optional[Application]:
        """
        Créer une candidature automatiquement depuis les entités extraites
        """
        try:
            from datetime import datetime, timedelta, timezone
            
            # Utiliser des valeurs par défaut si extraction partielle
            company_name = extraction.company_name or self._infer_company_from_email(email)
            job_title = extraction.job_title or self._infer_job_title_from_email(email)
            
            subject_label = (email.subject or "Sujet inconnu").strip()

            application = Application(
                user_id=email.user_id,  # ⚠️ FIX: Lier au bon utilisateur !
                company_name=company_name,
                job_title=job_title,
                location=extraction.location,
                status="ACKNOWLEDGED",  # Email d'accusé de réception reçu
                source="Email auto-detection",
                notes=f"Candidature créée automatiquement depuis l'email {email.id} : {subject_label}",
                next_action_at=datetime.now(timezone.utc) + timedelta(days=7)
            )
            
            self.db.add(application)
            self.db.flush()  # Pour obtenir l'ID
            
            # Lier l'email à cette candidature
            email.application_id = application.id
            
            return application
            
        except Exception as e:
            logger.error(f"Error creating application from extraction: {e}")
            return None
    
    def _schedule_reminder(self, email: Email, classification: ClassificationResult) -> bool:
        """
        Planifier des rappels basés sur le type d'email
        """
        # TODO: Implémenter la logique de rappels
        # Ceci serait connecté au système de scheduler
        
        reminder_days = {
            "ACK": 7,      # Rappel dans 7 jours si pas de nouvelles
            "INTERVIEW": 1, # Rappel le jour avant
            "REQUEST": 3,   # Rappel pour fournir les documents
        }
        
        email_type = classification.email_type.value
        if email_type in reminder_days:
            # Ici on ajouterait la logique de planification
            logger.info(f"Would schedule reminder for {email_type} in {reminder_days[email_type]} days")
            return True
        
        return False
    
    async def reprocess_email(self, email_id: str) -> Dict[str, Any]:
        """
        Retraiter un email avec les services NLP (utile pour améliorer les résultats)
        """
        email = self.db.query(Email).filter(Email.id == email_id).first()
        if not email:
            return {"error": "Email not found"}
        
        # Réinitialiser les champs liés au NLP
        email.classification = None
        
        # Retraiter
        return await self.process_email_complete(email)

    def _infer_job_title_from_email(self, email: Email) -> str:
        subject = (email.subject or "").strip()
        if subject:
            cleaned = re.sub(r'^(re|fw|fwd)\s*[:\-]\s*', '', subject, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r'\s+', ' ', cleaned)
            return cleaned[:120] or "Poste non spécifié"
        
        snippet = (email.snippet or email.raw_body or "").strip()
        if snippet:
            first_line = snippet.splitlines()[0]
            return first_line[:120] or "Poste non spécifié"
        
        return "Poste non spécifié"

    def _infer_company_from_email(self, email: Email) -> str:
        sender = (email.sender or "").strip()
        if '@' in sender:
            domain = sender.split('@')[-1]
        else:
            domain = sender
        
        domain = domain.lower()
        for suffix in ('.com', '.fr', '.net', '.io', '.co', '.org'):
            if domain.endswith(suffix):
                domain = domain[:-len(suffix)]
        parts = [part for part in domain.split('.') if part]
        if parts:
            candidate = parts[0].replace('-', ' ').strip()
            if candidate:
                return candidate.capitalize()
        
        return "Entreprise non spécifiée"

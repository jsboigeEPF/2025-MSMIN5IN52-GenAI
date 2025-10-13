"""
Service pour interagir avec l'API Gmail en utilisant OAuth 2.0
"""
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import base64
import email
import json
from sqlalchemy.orm import Session
from app.models.models import User, Email
from app.services.gmail_oauth_service import GmailOAuthService
import logging

logger = logging.getLogger(__name__)


class GmailAPIService:
    """
    Service pour interagir avec l'API Gmail
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.oauth_service = GmailOAuthService(db)
        self.base_url = "https://gmail.googleapis.com/gmail/v1"
        
    async def get_user_profile(self, user: User) -> Dict[str, Any]:
        """
        Récupère le profil Gmail de l'utilisateur
        """
        if not await self.oauth_service.ensure_valid_token(user):
            raise Exception("Token Gmail non valide")
            
        headers = {"Authorization": f"Bearer {user.gmail_access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/me/profile",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur récupération profil Gmail: {response.status_code} - {response.text}")
                raise Exception(f"Erreur API Gmail: {response.status_code}")
                
            return response.json()

    async def list_messages(
        self, 
        user: User, 
        max_results: int = 50,
        query: Optional[str] = None,
        label_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Liste les messages Gmail avec des filtres optionnels
        
        Args:
            user: Utilisateur dont on veut récupérer les emails
            max_results: Nombre maximum de messages à récupérer
            query: Requête de recherche Gmail (ex: "is:unread", "from:recruiter")
            label_ids: IDs des labels à filtrer
        """
        if not await self.oauth_service.ensure_valid_token(user):
            raise Exception("Token Gmail non valide")
            
        headers = {"Authorization": f"Bearer {user.gmail_access_token}"}
        
        params = {
            "maxResults": max_results,
            "includeSpamTrash": False
        }
        
        if query:
            params["q"] = query
        if label_ids:
            params["labelIds"] = label_ids
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/me/messages",
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur liste messages Gmail: {response.status_code} - {response.text}")
                raise Exception(f"Erreur API Gmail: {response.status_code}")
                
            data = response.json()
            return data.get("messages", [])

    async def get_message_details(self, user: User, message_id: str) -> Dict[str, Any]:
        """
        Récupère les détails d'un message avec le format METADATA
        Note: Le scope gmail.metadata ne permet que les formats 'metadata' et 'minimal'
        Format 'metadata' inclut: headers complets, payload metadata, snippet
        """
        if not await self.oauth_service.ensure_valid_token(user):
            raise Exception("Token Gmail non valide")
            
        headers = {"Authorization": f"Bearer {user.gmail_access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/me/messages/{message_id}",
                headers=headers,
                params={"format": "metadata", "metadataHeaders": ["From", "To", "Subject", "Date"]}
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur récupération message Gmail: {response.status_code} - {response.text}")
                raise Exception(f"Erreur API Gmail: {response.status_code}")
                
            return response.json()

    async def sync_emails_from_gmail(
        self, 
        user: User, 
        max_emails: int = 100,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Synchronise les emails depuis Gmail vers la base de données
        
        Args:
            user: Utilisateur dont synchroniser les emails
            max_emails: Nombre maximum d'emails à synchroniser
            days_back: Nombre de jours dans le passé à synchroniser
        """
        try:
            # Note: Le scope gmail.metadata ne supporte pas le paramètre 'q' (query)
            # On récupère simplement les N derniers emails sans filtre de date
            # Le filtrage par date sera fait côté serveur après récupération
            
            # Récupérer la liste des messages (sans query)
            messages = await self.list_messages(user, max_emails, query=None)
            
            synced_count = 0
            skipped_count = 0
            error_count = 0
            
            # Calculer la date limite pour le filtrage côté serveur
            date_limit = datetime.now() - timedelta(days=days_back)
            
            for message_info in messages:
                try:
                    message_id = message_info["id"]
                    
                    # Vérifier si l'email existe déjà
                    existing_email = self.db.query(Email).filter(
                        Email.user_id == user.id,
                        Email.gmail_message_id == message_id
                    ).first()
                    
                    if existing_email:
                        skipped_count += 1
                        continue
                    
                    # Récupérer les détails du message
                    message_details = await self.get_message_details(user, message_id)
                    
                    # Vérifier la date du message (filtrage côté serveur)
                    message_timestamp = int(message_details.get("internalDate", 0)) / 1000
                    message_date = datetime.fromtimestamp(message_timestamp)
                    
                    if message_date < date_limit:
                        skipped_count += 1
                        continue
                    
                    # Parser et sauvegarder l'email
                    email_data = self._parse_gmail_message(message_details, user.id)
                    if email_data:
                        email_obj = Email(**email_data)
                        self.db.add(email_obj)
                        synced_count += 1
                        
                except Exception as e:
                    logger.error(f"Erreur lors du traitement du message {message_info.get('id')}: {str(e)}")
                    error_count += 1
                    continue
            
            # Sauvegarder en lot
            if synced_count > 0:
                self.db.commit()
                
            logger.info(f"Synchronisation Gmail terminée pour l'utilisateur {user.id}: "
                       f"{synced_count} nouveaux, {skipped_count} ignorés, {error_count} erreurs")
            
            return {
                "success": True,
                "synced_emails": synced_count,
                "skipped_emails": skipped_count,
                "errors": error_count,
                "total_processed": len(messages)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation Gmail: {str(e)}")
            raise Exception(f"Erreur de synchronisation: {str(e)}")

    def _parse_gmail_message(self, message_data: Dict[str, Any], user_id: int) -> Optional[Dict[str, Any]]:
        """
        Parse un message Gmail et extrait les informations pertinentes
        """
        try:
            headers = {h["name"].lower(): h["value"] for h in message_data["payload"]["headers"]}
            
            # Extraire les informations de base
            subject = headers.get("subject", "")
            sender = headers.get("from", "")
            recipient = headers.get("to", "")
            date_header = headers.get("date", "")
            
            # Parser la date
            sent_at = self._parse_email_date(date_header)
            
            # Extraire le corps du message
            body_text, body_html = self._extract_message_body(message_data["payload"])
            
            # Déterminer si c'est un email entrant ou sortant
            is_sent = sender.lower().find(headers.get("delivered-to", "").lower()) != -1
            
            return {
                "user_id": user_id,
                "gmail_message_id": message_data["id"],
                "subject": subject,
                "sender": sender,
                "recipient": recipient,
                "sent_at": sent_at,
                "raw_body": body_text,
                "html_body": body_html,
                "snippet": message_data.get("snippet", ""),
                "thread_id": message_data.get("threadId"),
                "is_sent": is_sent,
                "gmail_labels": ",".join(message_data.get("labelIds", [])),
                "created_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du parsing du message: {str(e)}")
            return None

    def _extract_message_body(self, payload: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
        """
        Extrait le corps du message (texte et HTML)
        """
        body_text = None
        body_html = None
        
        def extract_from_part(part):
            nonlocal body_text, body_html
            
            mime_type = part.get("mimeType", "")
            
            if mime_type == "text/plain" and not body_text:
                data = part.get("body", {}).get("data")
                if data:
                    body_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    
            elif mime_type == "text/html" and not body_html:
                data = part.get("body", {}).get("data")
                if data:
                    body_html = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    
            # Traiter les parties multiples
            if "parts" in part:
                for sub_part in part["parts"]:
                    extract_from_part(sub_part)
        
        extract_from_part(payload)
        return body_text, body_html

    def _parse_email_date(self, date_str: str) -> datetime:
        """
        Parse la date d'un email au format RFC 2822
        """
        try:
            # Utiliser le module email pour parser la date
            import email.utils
            timestamp = email.utils.parsedate_tz(date_str)
            if timestamp:
                # Convertir en datetime UTC
                dt = datetime(*timestamp[:6])
                if timestamp[9]:  # Timezone offset
                    dt = dt - timedelta(seconds=timestamp[9])
                return dt
        except:
            pass
            
        # Fallback: retourner l'heure actuelle si le parsing échoue
        return datetime.utcnow()

    async def get_labels(self, user: User) -> List[Dict[str, Any]]:
        """
        Récupère la liste des labels Gmail de l'utilisateur
        """
        if not await self.oauth_service.ensure_valid_token(user):
            raise Exception("Token Gmail non valide")
            
        headers = {"Authorization": f"Bearer {user.gmail_access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/me/labels",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur récupération labels Gmail: {response.status_code} - {response.text}")
                raise Exception(f"Erreur API Gmail: {response.status_code}")
                
            data = response.json()
            return data.get("labels", [])

    async def search_job_related_emails(
        self, 
        user: User, 
        max_results: int = 50,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Recherche spécifiquement les emails liés aux candidatures
        Note: Le scope gmail.metadata ne supporte pas les queries de recherche
        On récupère tous les emails et on filtre côté serveur
        """
        try:
            # Récupérer les messages sans query (scope metadata ne supporte pas 'q')
            messages = await self.list_messages(user, max_results, query=None)
            
            # Mots-clés pour identifier les emails de recrutement
            job_keywords = [
                "candidature", "entretien", "interview", "poste", "offre d'emploi",
                "recrutement", "RH", "ressources humaines", "CV", "motivation",
                "job", "employment", "hiring", "recruiter", "opportunity"
            ]
            
            # Date limite pour le filtrage
            date_limit = datetime.now() - timedelta(days=days_back)
            
            detailed_messages = []
            for message_info in messages:
                try:
                    details = await self.get_message_details(user, message_info["id"])
                    
                    # Filtrer par date
                    message_timestamp = int(details.get("internalDate", 0)) / 1000
                    message_date = datetime.fromtimestamp(message_timestamp)
                    
                    if message_date < date_limit:
                        continue
                    
                    # Filtrer par mots-clés (dans le sujet ou le corps)
                    headers = {h["name"].lower(): h["value"] for h in details["payload"]["headers"]}
                    subject = headers.get("subject", "").lower()
                    snippet = details.get("snippet", "").lower()
                    
                    # Vérifier si un mot-clé est présent
                    content_to_check = f"{subject} {snippet}"
                    if any(keyword.lower() in content_to_check for keyword in job_keywords):
                        detailed_messages.append(details)
                    
                except Exception as e:
                    logger.error(f"Erreur récupération détails message {message_info['id']}: {str(e)}")
                    continue
            
            logger.info(f"Trouvé {len(detailed_messages)} emails de candidature sur {len(messages)} examinés")
            return detailed_messages
            
        except Exception as e:
            logger.error(f"Erreur recherche emails de candidature: {str(e)}")
            raise Exception(f"Erreur de recherche: {str(e)}")

    async def mark_message_as_processed(self, user: User, message_id: str) -> bool:
        """
        Marque un message comme traité (ajoute un label custom)
        """
        # Cette fonctionnalité nécessiterait la création d'un label custom
        # ou l'utilisation d'un système de tracking dans notre DB
        # Pour l'instant, on se contente de logger
        logger.info(f"Message {message_id} marqué comme traité pour l'utilisateur {user.id}")
        return True

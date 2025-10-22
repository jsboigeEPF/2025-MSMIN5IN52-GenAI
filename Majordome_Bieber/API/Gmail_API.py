from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText

from login import get_credentials


def create_draft(service):
    """Create and insert a draft email.
    """
    message = MIMEText("hello world")
    message['to'] = ""  # laissé vide pour le brouillon
    message['subject'] = "Test Draft"

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {
        'message': {
            'raw': encoded_message
        }
    }

    try:
        draft = service.users().drafts().create(
            userId="me", body=create_message).execute()
        print(F'Draft id: {draft["id"]}\nDraft created successfully.')
        return draft
    except HttpError as error:
        print(F'An error occurred: {error}')
        return None


def createDraft():
    """Shows basic usage of the Gmail API.
    Creates a draft email.
    """
    creds = get_credentials()

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        create_draft(service)

    except HttpError as error:
        print(f"An error occurred: {error}")


def readMail(nbr_mail=10):
    """Affiche l'utilisation de base de l'API Gmail.
    Récupère et affiche les 10 derniers e-mails de l'utilisateur.
    """
    creds = get_credentials()

    try:
        # Appeler l'API Gmail
        service = build("gmail", "v1", credentials=creds)

        # Récupérer la liste des 10 derniers messages.
        results = service.users().messages().list(
            userId="me", maxResults=nbr_mail).execute()
        messages = results.get("messages", [])

        if not messages:
            return []

        emails_list = []
        for message in messages:
            msg = service.users().messages().get(
                userId="me", id=message["id"]).execute()
            payload = msg.get("payload", {})
            headers = payload.get("headers", [])

            subject = ""
            sender = ""
            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                if header['name'] == 'From':
                    sender = header['value']

            snippet = msg.get("snippet", "")
            emails_list.append({
                "from": sender,
                "subject": subject,
                "snippet": snippet,
                "id": message["id"]
            })

        return emails_list

    except HttpError as error:
        print(f"An error occurred: {error}")

from pydantic import BaseModel, Field
from typing import Optional, List, Generic, TypeVar
from datetime import datetime
from uuid import UUID
from enum import Enum

T = TypeVar('T')


class ApplicationStatus(str, Enum):
    APPLIED = "APPLIED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    SCREENING = "SCREENING"
    INTERVIEW = "INTERVIEW"
    TECHNICAL_TEST = "TECHNICAL_TEST"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    ON_HOLD = "ON_HOLD"
    ACCEPTED = "ACCEPTED"


class UrgencyLevel(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class EventType(str, Enum):
    STATUS_CHANGE = "STATUS_CHANGE"
    EMAIL_RECEIVED = "EMAIL_RECEIVED"
    NOTE = "NOTE"
    REMINDER = "REMINDER"


class UserBase(BaseModel):
    email: str
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: UUID
    created_at: datetime

class UserLogin(BaseModel):
    email: str
    password: str

class EmailClassification(str, Enum):
    ACK = "ACK"
    REJECTED = "REJECTED"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REQUEST = "REQUEST"
    OTHER = "OTHER"


# Application schemas
class ApplicationBase(BaseModel):
    job_title: str = Field(..., description="Intitulé du poste")
    company_name: str = Field(..., description="Nom de l'entreprise")
    source: Optional[str] = Field(None, description="Source de la candidature (LinkedIn, site web, etc.)")
    location: Optional[str] = Field(None, description="Localisation du poste")
    status: ApplicationStatus = Field(ApplicationStatus.APPLIED, description="Statut de la candidature")
    notes: Optional[str] = Field(None, description="Notes personnelles")
    
    # Nouveaux champs pour le tracking intelligent
    contact_person: Optional[str] = Field(None, description="Personne de contact")
    contact_email: Optional[str] = Field(None, description="Email de contact")
    interview_date: Optional[datetime] = Field(None, description="Date d'entretien programmé")
    response_deadline: Optional[datetime] = Field(None, description="Date limite de réponse")
    job_reference: Optional[str] = Field(None, description="Référence du poste")
    urgency_level: UrgencyLevel = Field(UrgencyLevel.NORMAL, description="Niveau d'urgence")
    expected_salary: Optional[str] = Field(None, description="Salaire espéré")
    offer_amount: Optional[str] = Field(None, description="Montant de l'offre reçue")
    offer_deadline: Optional[datetime] = Field(None, description="Date limite pour répondre à l'offre")
    rejection_reason: Optional[str] = Field(None, description="Raison du refus")
    applied_date: Optional[datetime] = Field(None, description="Date de candidature")
    priority: Priority = Field(Priority.MEDIUM, description="Priorité de la candidature")


class ApplicationCreate(ApplicationBase):
    next_action_at: Optional[datetime] = Field(None, description="Date de la prochaine action à effectuer")


class ApplicationUpdate(BaseModel):
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    source: Optional[str] = None
    location: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    next_action_at: Optional[datetime] = None
    
    # Nouveaux champs optionnels pour la mise à jour
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    interview_date: Optional[datetime] = None
    response_deadline: Optional[datetime] = None
    job_reference: Optional[str] = None
    urgency_level: Optional[UrgencyLevel] = None
    expected_salary: Optional[str] = None
    offer_amount: Optional[str] = None
    offer_deadline: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    applied_date: Optional[datetime] = None
    priority: Optional[Priority] = None


class Application(ApplicationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    next_action_at: Optional[datetime] = None
    last_update_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Email schemas
class EmailBase(BaseModel):
    external_id: Optional[str] = None
    subject: Optional[str] = None
    sender: Optional[str] = None
    recipients: Optional[List[str]] = []
    cc: Optional[List[str]] = []
    bcc: Optional[List[str]] = []
    sent_at: Optional[datetime] = None
    snippet: Optional[str] = None
    language: Optional[str] = None
    classification: Optional[EmailClassification] = None


class EmailCreate(EmailBase):
    application_id: Optional[UUID] = None
    raw_headers: Optional[str] = None
    raw_body: Optional[str] = None


class Email(EmailBase):
    id: UUID
    application_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Application Event schemas
class ApplicationEventBase(BaseModel):
    event_type: EventType
    payload: Optional[dict] = None


class ApplicationEventCreate(ApplicationEventBase):
    application_id: UUID


class ApplicationEvent(ApplicationEventBase):
    id: UUID
    application_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Response schemas
class ApplicationWithEvents(Application):
    events: List[ApplicationEvent] = []


class ApplicationWithEmails(Application):
    emails: List[Email] = []


class ApplicationFull(Application):
    events: List[ApplicationEvent] = []
    emails: List[Email] = []


# Generic schemas for API responses
class PaginatedResponse(BaseModel, Generic[T]):
    """Response model for paginated API endpoints"""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")

from sqlalchemy import Column, String, Text, TIMESTAMP, ARRAY, UUID, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from app.core.database import Base
import uuid


class User(Base):
    __tablename__ = "users"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=func.now())
    
    # Relations Gmail OAuth
    gmail_refresh_token = Column(Text)
    gmail_access_token = Column(Text)
    gmail_token_expires_at = Column(TIMESTAMP(timezone=True))
    gmail_connected = Column(Boolean, default=False)  # Statut de connexion Gmail
    gmail_email = Column(String(255))  # Email Gmail connecté
    gmail_scopes = Column(Text)  # Scopes OAuth accordés
    
    # Relations
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    emails = relationship("Email", back_populates="user", cascade="all, delete-orphan")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    job_title = Column(Text, nullable=False)
    company_name = Column(Text, nullable=False)
    source = Column(Text)
    location = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    status = Column(Text, nullable=False, default="APPLIED")
    next_action_at = Column(TIMESTAMP(timezone=True))
    notes = Column(Text)
    
    # Nouveaux champs pour le tracking intelligent
    contact_person = Column(Text)
    contact_email = Column(Text)
    interview_date = Column(TIMESTAMP(timezone=True))
    response_deadline = Column(TIMESTAMP(timezone=True))
    job_reference = Column(Text)
    urgency_level = Column(Text, default="NORMAL")  # NORMAL, HIGH, URGENT
    last_update_date = Column(TIMESTAMP(timezone=True))
    expected_salary = Column(Text)
    offer_amount = Column(Text)
    offer_deadline = Column(TIMESTAMP(timezone=True))
    rejection_reason = Column(Text)
    applied_date = Column(TIMESTAMP(timezone=True))
    priority = Column(Text, default="MEDIUM")  # LOW, MEDIUM, HIGH
    
    # Relationship with user, emails and events
    user = relationship("User", back_populates="applications")
    emails = relationship("Email", back_populates="application")
    events = relationship("ApplicationEvent", back_populates="application", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint(
            status.in_([
                'APPLIED', 'ACKNOWLEDGED', 'SCREENING', 'INTERVIEW',
                'TECHNICAL_TEST', 'OFFER', 'REJECTED', 'WITHDRAWN', 'ON_HOLD', 'ACCEPTED'
            ]),
            name='status_check'
        ),
        CheckConstraint(
            urgency_level.in_(['NORMAL', 'HIGH', 'URGENT']),
            name='urgency_check'
        ),
        CheckConstraint(
            priority.in_(['LOW', 'MEDIUM', 'HIGH']),
            name='priority_check'
        ),
    )


class Email(Base):
    __tablename__ = "emails"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    application_id = Column(PGUUID(as_uuid=True), ForeignKey('applications.id', ondelete='SET NULL'))
    external_id = Column(Text, index=True)  # Message-Id, Gmail ID, etc.
    gmail_message_id = Column(Text, index=True)  # ID spécifique Gmail
    subject = Column(Text)
    sender = Column(Text)
    recipient = Column(Text)  # Destinataire principal
    recipients = Column(ARRAY(Text))
    cc = Column(ARRAY(Text))
    bcc = Column(ARRAY(Text))
    sent_at = Column(TIMESTAMP(timezone=True))
    raw_headers = Column(Text)
    raw_body = Column(Text)
    html_body = Column(Text)  # Corps HTML de l'email
    snippet = Column(Text)
    thread_id = Column(Text)  # Thread Gmail
    is_sent = Column(String(10), default="false")  # Email envoyé ou reçu
    gmail_labels = Column(Text)  # Labels Gmail (séparés par virgules)
    language = Column(Text)
    classification = Column(Text)  # ACK/REJECTED/INTERVIEW/OTHER
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=func.now())
    
    # Relationship with user and application
    user = relationship("User", back_populates="emails")
    application = relationship("Application", back_populates="emails")


class ApplicationEvent(Base):
    __tablename__ = "application_events"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(PGUUID(as_uuid=True), ForeignKey('applications.id', ondelete='CASCADE'), nullable=False)
    event_type = Column(Text, nullable=False)  # 'STATUS_CHANGE','EMAIL_RECEIVED','NOTE','REMINDER'
    payload = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=func.now())
    
    # Relationship with application
    application = relationship("Application", back_populates="events")

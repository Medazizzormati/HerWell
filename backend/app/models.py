from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def get_utc_now():
    return datetime.now(timezone.utc)

class MoodCheckin(Base):
    __tablename__ = "mood_checkins"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mood: Mapped[str] = mapped_column(String(32))
    stress: Mapped[int] = mapped_column(Integer, default=3)
    energy: Mapped[int] = mapped_column(Integer, default=3)
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)

class StudyTask(Base):
    __tablename__ = "study_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(180))
    subject: Mapped[str] = mapped_column(String(100), default="")
    deadline: Mapped[str] = mapped_column(String(32), default="")
    duration_minutes: Mapped[int] = mapped_column(Integer, default=45)
    priority: Mapped[str] = mapped_column(String(16), default="medium")
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)

class Resource(Base):
    __tablename__ = "resources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(180), unique=True)
    category: Mapped[str] = mapped_column(String(80))
    content: Mapped[str] = mapped_column(Text)
    source_label: Mapped[str] = mapped_column(String(180), default="Rédigé par l'équipe — contenu éducatif non médical")
    source_url: Mapped[str] = mapped_column(String(500), nullable=True, default="")
    language: Mapped[str] = mapped_column(String(10), nullable=True, default="fr")
    verification_status: Mapped[str] = mapped_column(String(20), nullable=True, default="internal")
    publication_date: Mapped[str] = mapped_column(String(32), nullable=True, default="")

class ResourceChunk(Base):
    __tablename__ = "resource_chunks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource_id: Mapped[int] = mapped_column(Integer, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(JSON, nullable=True)
    chunk_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    technologies: Mapped[str] = mapped_column(String(500), default="")  # Comma-separated
    status: Mapped[str] = mapped_column(String(32), default="planning")  # planning, development, testing, completed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)

class ProjectDocument(Base):
    __tablename__ = "project_documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    file_type: Mapped[str] = mapped_column(String(32), default="txt")  # txt, md, pdf, code
    source_type: Mapped[str] = mapped_column(String(64), default="user_upload")  # user_upload, requirements, documentation
    language: Mapped[str] = mapped_column(String(10), default="fr")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    
    project = relationship("Project", backref="documents")

class ProjectTask(Base):
    __tablename__ = "project_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    deadline: Mapped[str] = mapped_column(String(32), default="")
    status: Mapped[str] = mapped_column(String(32), default="todo")  # todo, in_progress, done
    priority: Mapped[str] = mapped_column(String(16), default="medium")
    technology: Mapped[str] = mapped_column(String(100), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    project = relationship("Project", backref="tasks")

class TechnicalConversation(Base):
    __tablename__ = "technical_conversations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=True)
    user_message: Mapped[str] = mapped_column(Text)
    assistant_response: Mapped[str] = mapped_column(Text)
    intent: Mapped[str] = mapped_column(String(64), default="general")
    sources: Mapped[dict] = mapped_column(JSON, nullable=True)
    degraded_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    
    project = relationship("Project", backref="conversations")

# Women's Wellbeing and Menstrual Health Module
# Privacy-first design: These tables are separate from general project data
# Users must explicitly enable tracking; data is stored locally only

class CycleTracking(Base):
    __tablename__ = "cycle_tracking"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    period_start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    cycle_length_days: Mapped[int] = mapped_column(Integer, nullable=True)  # User-reported cycle length
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    # Privacy flag: user must explicitly enable tracking
    tracking_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

class SymptomLog(Base):
    __tablename__ = "symptom_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    log_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    physical_symptoms: Mapped[str] = mapped_column(String(500), default="")  # Comma-separated: cramps, headache, fatigue, etc.
    mood: Mapped[str] = mapped_column(String(32), default="neutral")  # low, neutral, good
    energy_level: Mapped[int] = mapped_column(Integer, default=3)  # 1-5 scale
    pain_level: Mapped[int] = mapped_column(Integer, nullable=True)  # 1-10 scale for physical pain
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    # Privacy flag: user must explicitly enable tracking
    tracking_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

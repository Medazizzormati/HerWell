from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from datetime import datetime

class MoodCreate(BaseModel):
    mood: Literal["very_low", "low", "okay", "good", "great"]
    stress: int = Field(ge=1, le=5, default=3)
    energy: int = Field(ge=1, le=5, default=3)
    note: str = Field(default="", max_length=1000)

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    subject: str = Field(default="", max_length=100)
    deadline: str = Field(default="", max_length=32)
    duration_minutes: int = Field(default=45, ge=5, le=600)
    priority: Literal["low", "medium", "high"] = "medium"

class TaskUpdate(BaseModel):
    completed: bool | None = None
    title: str | None = Field(default=None, min_length=1, max_length=180)
    priority: Literal["low", "medium", "high"] | None = None

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

class PlanRequest(BaseModel):
    available_minutes: int = Field(default=180, ge=15, le=900)
    break_minutes: int = Field(default=10, ge=0, le=30)

# Technical PFE Assistant Schemas
class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    technologies: str = Field(default="", max_length=500)
    status: Literal["planning", "development", "testing", "completed"] = "planning"

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    technologies: Optional[str] = Field(None, max_length=500)
    status: Optional[Literal["planning", "development", "testing", "completed"]] = None

class ProjectDocumentCreate(BaseModel):
    project_id: int
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=50000)
    file_type: Literal["txt", "md", "pdf", "code"] = "txt"
    source_type: Literal["user_upload", "requirements", "documentation"] = "user_upload"
    language: str = Field(default="fr", max_length=10)

class ProjectTaskCreate(BaseModel):
    project_id: int
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    deadline: str = Field(default="", max_length=32)
    priority: Literal["low", "medium", "high"] = "medium"
    technology: str = Field(default="", max_length=100)

class ProjectTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    deadline: Optional[str] = Field(None, max_length=32)
    status: Optional[Literal["todo", "in_progress", "done"]] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    technology: Optional[str] = Field(None, max_length=100)

class TechnicalChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    project_id: Optional[int] = None
    context: Optional[str] = Field(None, max_length=2000)  # Error message, code snippet, etc.

# Women's Wellbeing and Menstrual Health Schemas
class CycleTrackingCreate(BaseModel):
    period_start_date: datetime
    cycle_length_days: Optional[int] = Field(None, ge=21, le=45)  # Typical range 21-35, allow up to 45
    notes: str = Field(default="", max_length=500)
    tracking_enabled: bool = True  # User must explicitly enable

class SymptomLogCreate(BaseModel):
    log_date: datetime
    physical_symptoms: str = Field(default="", max_length=500)  # Comma-separated
    mood: Literal["low", "neutral", "good"] = "neutral"
    energy_level: int = Field(ge=1, le=5, default=3)
    pain_level: Optional[int] = Field(None, ge=1, le=10)  # 1-10 pain scale
    notes: str = Field(default="", max_length=500)
    tracking_enabled: bool = True  # User must explicitly enable

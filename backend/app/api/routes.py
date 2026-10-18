from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import MoodCheckin, StudyTask, Resource, Project, ProjectDocument, ProjectTask, TechnicalConversation, CycleTracking, SymptomLog
from ..schemas import (
    MoodCreate, TaskCreate, TaskUpdate, ChatRequest, PlanRequest,
    ProjectCreate, ProjectUpdate, ProjectDocumentCreate, ProjectTaskCreate, ProjectTaskUpdate, TechnicalChatRequest,
    CycleTrackingCreate, SymptomLogCreate
)
from ..ai.rag import seed_resources, retrieve_resources
from ..ai.graph import run_chat
import json
from pathlib import Path

router = APIRouter(prefix="/api")

@router.get("/resources")
def resources(db: Session = Depends(get_db)):
    seed_resources(db)
    return [{"title": r.title, "category": r.category, "content": r.content, "source": r.source_label}
            for r in db.query(Resource).all()]

@router.get("/resources/search")
def search_resources(query: str, db: Session = Depends(get_db)):
    resources = retrieve_resources(db, query, limit=10)
    return resources

@router.post("/checkins")
def create_checkin(payload: MoodCreate, db: Session = Depends(get_db)):
    item = MoodCheckin(**payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return {"id": item.id, "mood": item.mood, "stress": item.stress, "energy": item.energy,
            "note": item.note, "created_at": item.created_at.isoformat()}

@router.get("/checkins")
def list_checkins(db: Session = Depends(get_db)):
    return [{"id": x.id, "mood": x.mood, "stress": x.stress, "energy": x.energy,
             "note": x.note, "created_at": x.created_at.isoformat()}
            for x in db.query(MoodCheckin).order_by(MoodCheckin.created_at.desc()).limit(100).all()]

@router.get("/checkins/{checkin_id}")
def get_checkin(checkin_id: int, db: Session = Depends(get_db)):
    checkin = db.get(MoodCheckin, checkin_id)
    if not checkin: raise HTTPException(status_code=404, detail="Check-in not found")
    return {"id": checkin.id, "mood": checkin.mood, "stress": checkin.stress, "energy": checkin.energy,
            "note": checkin.note, "created_at": checkin.created_at.isoformat()}

@router.delete("/checkins/{checkin_id}")
def delete_checkin(checkin_id: int, db: Session = Depends(get_db)):
    checkin = db.get(MoodCheckin, checkin_id)
    if not checkin: raise HTTPException(status_code=404, detail="Check-in not found")
    db.delete(checkin); db.commit()
    return {"deleted": True}

@router.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    return [{"id": t.id, "title": t.title, "subject": t.subject, "deadline": t.deadline,
             "duration_minutes": t.duration_minutes, "priority": t.priority, "completed": t.completed}
            for t in db.query(StudyTask).order_by(StudyTask.id.desc()).all()]

@router.post("/tasks")
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = StudyTask(**payload.model_dump())
    db.add(task); db.commit(); db.refresh(task)
    return {"id": task.id, "title": task.title, "subject": task.subject, "deadline": task.deadline,
            "duration_minutes": task.duration_minutes, "priority": task.priority, "completed": task.completed}

@router.patch("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(StudyTask, task_id)
    if not task: raise HTTPException(status_code=404, detail="Task not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit(); db.refresh(task)
    return {"id": task.id, "title": task.title, "completed": task.completed, "priority": task.priority}

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(StudyTask, task_id)
    if not task: raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task); db.commit()
    return {"deleted": True}

@router.post("/plans")
def create_plan(payload: PlanRequest, db: Session = Depends(get_db)):
    tasks = db.query(StudyTask).filter(StudyTask.completed == False).order_by(StudyTask.priority.desc(), StudyTask.id.asc()).all()
    remaining = payload.available_minutes
    slots = []
    for task in tasks:
        if remaining <= 0: break
        duration = min(task.duration_minutes, remaining)
        slots.append({"task_id": task.id, "title": task.title, "minutes": duration,
                      "break_after_minutes": payload.break_minutes if remaining > duration else 0})
        remaining -= duration + (payload.break_minutes if remaining > duration else 0)
    return {"available_minutes": payload.available_minutes, "slots": slots,
            "unallocated_minutes": max(0, remaining), "method": "deterministic_scheduler"}

@router.get("/plans")
def list_plans(db: Session = Depends(get_db)):
    return {"message": "Plan history not implemented in MVP. Use POST /api/plans to generate a new plan."}

@router.post("/chat")
async def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    seed_resources(db)
    return await run_chat(db, payload.message)

@router.get("/support-resources")
def get_support_resources():
    data_file = Path(__file__).resolve().parents[1] / "data" / "support_resources.json"
    if data_file.exists():
        return json.loads(data_file.read_text(encoding="utf-8"))
    return {"verified_contacts": [], "note": "No support resources configured."}

# Technical PFE Assistant Endpoints
@router.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    return [{"id": p.id, "title": p.title, "description": p.description, "technologies": p.technologies,
            "status": p.status, "created_at": p.created_at.isoformat(), "updated_at": p.updated_at.isoformat()}
            for p in db.query(Project).order_by(Project.updated_at.desc()).all()]

@router.post("/projects")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**payload.model_dump())
    db.add(project); db.commit(); db.refresh(project)
    return {"id": project.id, "title": project.title, "description": project.description,
            "technologies": project.technologies, "status": project.status,
            "created_at": project.created_at.isoformat()}

@router.get("/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"id": project.id, "title": project.title, "description": project.description,
            "technologies": project.technologies, "status": project.status,
            "created_at": project.created_at.isoformat(), "updated_at": project.updated_at.isoformat()}

@router.patch("/projects/{project_id}")
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    project.updated_at = datetime.now()
    db.commit(); db.refresh(project)
    return {"id": project.id, "title": project.title, "status": project.status}

@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project); db.commit()
    return {"deleted": True}

@router.get("/projects/{project_id}/documents")
def list_project_documents(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return [{"id": d.id, "title": d.title, "file_type": d.file_type, "source_type": d.source_type,
            "language": d.language, "uploaded_at": d.uploaded_at.isoformat()}
            for d in db.query(ProjectDocument).filter(ProjectDocument.project_id == project_id).all()]

@router.post("/projects/{project_id}/documents")
def create_project_document(project_id: int, payload: ProjectDocumentCreate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    doc_data = payload.model_dump()
    doc_data['project_id'] = project_id
    doc = ProjectDocument(**doc_data)
    db.add(doc); db.commit(); db.refresh(doc)
    return {"id": doc.id, "title": doc.title, "file_type": doc.file_type, "uploaded_at": doc.uploaded_at.isoformat()}

@router.delete("/documents/{document_id}")
def delete_project_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.get(ProjectDocument, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc); db.commit()
    return {"deleted": True}

@router.get("/projects/{project_id}/tasks")
def list_project_tasks(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return [{"id": t.id, "title": t.title, "description": t.description, "deadline": t.deadline,
            "status": t.status, "priority": t.priority, "technology": t.technology,
            "created_at": t.created_at.isoformat()}
            for t in db.query(ProjectTask).filter(ProjectTask.project_id == project_id).all()]

@router.post("/projects/{project_id}/tasks")
def create_project_task(project_id: int, payload: ProjectTaskCreate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    task_data = payload.model_dump()
    task_data['project_id'] = project_id
    task = ProjectTask(**task_data)
    db.add(task); db.commit(); db.refresh(task)
    return {"id": task.id, "title": task.title, "status": task.status, "priority": task.priority}

@router.patch("/tasks/{task_id}")
def update_project_task(task_id: int, payload: ProjectTaskUpdate, db: Session = Depends(get_db)):
    task = db.get(ProjectTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    if payload.status == "done" and not task.completed_at:
        task.completed_at = datetime.now()
    db.commit(); db.refresh(task)
    return {"id": task.id, "title": task.title, "status": task.status}

@router.delete("/tasks/{task_id}")
def delete_project_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(ProjectTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task); db.commit()
    return {"deleted": True}

@router.post("/technical-chat")
async def technical_chat(payload: TechnicalChatRequest, db: Session = Depends(get_db)):
    """Technical PFE Assistant chat endpoint"""
    # Retrieve project documents if project_id is provided
    project_context = ""
    if payload.project_id:
        project = db.get(Project, payload.project_id)
        if project:
            project_context = f"Project: {project.title}\nTechnologies: {project.technologies}\nStatus: {project.status}\n"
            docs = db.query(ProjectDocument).filter(ProjectDocument.project_id == payload.project_id).all()
            if docs:
                project_context += "\nProject Documents:\n"
                for doc in docs:
                    project_context += f"- {doc.title} ({doc.file_type}): {doc.content[:500]}...\n"
    
    # Combine user message with context
    full_message = payload.message
    if payload.context:
        full_message = f"{payload.context}\n\nQuestion: {payload.message}"
    if project_context:
        full_message = f"{project_context}\n\n{full_message}"
    
    # Run chat with enhanced context and project_id for RAG
    result = await run_chat(db, full_message, project_id=payload.project_id)
    
    # Save conversation if project_id is provided
    if payload.project_id:
        conv = TechnicalConversation(
            project_id=payload.project_id,
            user_message=payload.message,
            assistant_response=result.get("response", ""),
            intent=result.get("intent", "general_support"),
            sources=result.get("sources", []),
            degraded_mode=result.get("degraded_mode", False)
        )
        db.add(conv); db.commit()
    
    return result

# Women's Wellbeing and Menstrual Health API Endpoints
# Privacy-first: All endpoints require explicit tracking_enabled=True

@router.get("/menstrual/cycles")
def list_cycles(db: Session = Depends(get_db)):
    """List all menstrual cycle entries (only if tracking is enabled)"""
    cycles = db.query(CycleTracking).filter(CycleTracking.tracking_enabled == True).order_by(CycleTracking.period_start_date.desc()).all()
    return [{
        "id": c.id,
        "period_start_date": c.period_start_date.isoformat(),
        "cycle_length_days": c.cycle_length_days,
        "notes": c.notes,
        "created_at": c.created_at.isoformat()
    } for c in cycles]

@router.post("/menstrual/cycles")
def create_cycle(payload: CycleTrackingCreate, db: Session = Depends(get_db)):
    """Create a new menstrual cycle entry"""
    if not payload.tracking_enabled:
        raise HTTPException(status_code=400, detail="Tracking must be explicitly enabled")
    
    cycle = CycleTracking(**payload.model_dump())
    db.add(cycle); db.commit(); db.refresh(cycle)
    
    return {
        "id": cycle.id,
        "period_start_date": cycle.period_start_date.isoformat(),
        "cycle_length_days": cycle.cycle_length_days,
        "notes": cycle.notes,
        "created_at": cycle.created_at.isoformat()
    }

@router.delete("/menstrual/cycles/{cycle_id}")
def delete_cycle(cycle_id: int, db: Session = Depends(get_db)):
    """Delete a menstrual cycle entry"""
    cycle = db.get(CycleTracking, cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle entry not found")
    db.delete(cycle); db.commit()
    return {"deleted": True}

@router.get("/menstrual/symptoms")
def list_symptoms(db: Session = Depends(get_db)):
    """List all symptom logs (only if tracking is enabled)"""
    symptoms = db.query(SymptomLog).filter(SymptomLog.tracking_enabled == True).order_by(SymptomLog.log_date.desc()).all()
    return [{
        "id": s.id,
        "log_date": s.log_date.isoformat(),
        "physical_symptoms": s.physical_symptoms,
        "mood": s.mood,
        "energy_level": s.energy_level,
        "pain_level": s.pain_level,
        "notes": s.notes,
        "created_at": s.created_at.isoformat()
    } for s in symptoms]

@router.post("/menstrual/symptoms")
def create_symptom_log(payload: SymptomLogCreate, db: Session = Depends(get_db)):
    """Create a new symptom log entry"""
    if not payload.tracking_enabled:
        raise HTTPException(status_code=400, detail="Tracking must be explicitly enabled")
    
    symptom = SymptomLog(**payload.model_dump())
    db.add(symptom); db.commit(); db.refresh(symptom)
    
    return {
        "id": symptom.id,
        "log_date": symptom.log_date.isoformat(),
        "physical_symptoms": symptom.physical_symptoms,
        "mood": symptom.mood,
        "energy_level": symptom.energy_level,
        "pain_level": symptom.pain_level,
        "notes": symptom.notes,
        "created_at": symptom.created_at.isoformat()
    }

@router.delete("/menstrual/symptoms/{symptom_id}")
def delete_symptom_log(symptom_id: int, db: Session = Depends(get_db)):
    """Delete a symptom log entry"""
    symptom = db.get(SymptomLog, symptom_id)
    if not symptom:
        raise HTTPException(status_code=404, detail="Symptom log not found")
    db.delete(symptom); db.commit()
    return {"deleted": True}

@router.delete("/menstrual/all-data")
def delete_all_menstrual_data(db: Session = Depends(get_db)):
    """Delete ALL menstrual health data (privacy control)"""
    # This is a destructive operation - confirm with user in UI
    cycles_deleted = db.query(CycleTracking).delete()
    symptoms_deleted = db.query(SymptomLog).delete()
    db.commit()
    return {
        "deleted": True,
        "cycles_deleted": cycles_deleted,
        "symptoms_deleted": symptoms_deleted,
        "message": "All menstrual health data has been permanently deleted"
    }

@router.get("/menstrual/estimate-next-period")
def estimate_next_period(db: Session = Depends(get_db)):
    """
    Estimate next period date based on historical data.
    Returns None if insufficient data.
    Clearly labeled as estimate, not prediction.
    """
    # Get last 3 cycle entries with cycle_length_days
    cycles = db.query(CycleTracking).filter(
        CycleTracking.tracking_enabled == True,
        CycleTracking.cycle_length_days.isnot(None)
    ).order_by(CycleTracking.period_start_date.desc()).limit(3).all()
    
    if len(cycles) < 2:
        return {
            "estimate": None,
            "message": "Insufficient data to estimate next period. Record at least 2 complete cycles.",
            "data_points": len(cycles)
        }
    
    # Calculate average cycle length
    avg_cycle_length = sum(c.cycle_length_days for c in cycles) / len(cycles)
    
    # Get most recent period start
    last_period = cycles[0].period_start_date
    
    # Estimate next period
    from datetime import timedelta
    estimated_date = last_period + timedelta(days=int(avg_cycle_length))
    
    return {
        "estimate": estimated_date.isoformat(),
        "average_cycle_length": round(avg_cycle_length, 1),
        "data_points": len(cycles),
        "last_period_start": last_period.isoformat(),
        "disclaimer": "This is an estimate based on your historical data. Individual cycles vary. This is not a medical prediction or confirmation.",
        "irregular": len(cycles) >= 3 and max(c.cycle_length_days for c in cycles) - min(c.cycle_length_days for c in cycles) > 7
    }

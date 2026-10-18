from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import get_db
from .models import Project
from .schemas import ProjectCreate, ProjectOut, ProjectUpdate

app = FastAPI(
    title="HackBoard API",
    description="Hackathon project tracker - DevOps final capstone (Session 21)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/")
def root():
    return {"name": "HackBoard API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    # Liveness: process is up. Does not touch the database.
    return {"status": "ok"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    # Readiness: can we actually serve traffic? Verify DB access.
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"database not ready: {exc.__class__.__name__}")
    return {"status": "ready"}


@app.get("/api/projects", response_model=list[ProjectOut])
def list_projects(
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    q = db.query(Project)
    if status:
        q = q.filter(Project.status == status)
    return q.order_by(Project.created_at.desc()).all()


@app.get("/api/projects/stats")
def project_stats(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    by_status: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    for p in projects:
        by_status[p.status] = by_status.get(p.status, 0) + 1
        by_priority[p.priority] = by_priority.get(p.priority, 0) + 1
    upcoming = [
        p.title
        for p in projects
        if p.deadline is not None and p.deadline >= date.today() and p.status in ("idea", "building")
    ]
    return {
        "total": len(projects),
        "by_status": by_status,
        "by_priority": by_priority,
        "high_priority_open": sum(1 for p in projects if p.priority == "high" and p.status in ("idea", "building")),
        "upcoming_deadlines": sorted(upcoming),
    }


@app.get("/api/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    return project


@app.post("/api/projects", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@app.put("/api/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


@app.delete("/api/projects/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    db.delete(project)
    db.commit()
    return None

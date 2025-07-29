from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
import os

from . import crud, models
from .database import engine, get_db
from .cron_service import CronService

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Linux Cron Job Manager", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Initialize cron service
cron_service = CronService()

# Pydantic models for API
from pydantic import BaseModel
from typing import Optional

class CronJobCreate(BaseModel):
    name: str
    expression: str
    command: str
    description: Optional[str] = None

class CronJobUpdate(BaseModel):
    name: Optional[str] = None
    expression: Optional[str] = None
    command: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None

class CronJobResponse(BaseModel):
    id: int
    name: str
    expression: str
    command: str
    description: Optional[str]
    enabled: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        # Convert datetime objects to strings
        data = {
            'id': obj.id,
            'name': obj.name,
            'expression': obj.expression,
            'command': obj.command,
            'description': obj.description,
            'enabled': obj.enabled,
            'created_at': obj.created_at.isoformat() if obj.created_at else None,
            'updated_at': obj.updated_at.isoformat() if obj.updated_at else None,
        }
        return cls(**data)

# Web interface routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# API routes
@app.get("/api/jobs", response_model=List[CronJobResponse])
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all cron jobs"""
    jobs = crud.get_cron_jobs(db, skip=skip, limit=limit)
    return [CronJobResponse.from_orm(job) for job in jobs]

@app.post("/api/jobs", response_model=CronJobResponse)
def create_job(job: CronJobCreate, db: Session = Depends(get_db)):
    """Create a new cron job"""
    # Validate cron expression
    if not cron_service.validate_expression(job.expression):
        raise HTTPException(status_code=400, detail="Invalid cron expression")
    
    # Check if job name already exists
    existing_jobs = crud.get_cron_jobs(db)
    for existing_job in existing_jobs:
        if existing_job.name == job.name:
            raise HTTPException(status_code=400, detail="Job name already exists")
    
    # Create job in database
    db_job = crud.create_cron_job(
        db=db,
        name=job.name,
        expression=job.expression,
        command=job.command,
        description=job.description
    )
    
    # Add job to system cron
    if cron_service.add_job(job.name, job.expression, job.command):
        return CronJobResponse.from_orm(db_job)
    else:
        # Rollback database if cron addition fails
        crud.delete_cron_job(db, db_job.id)
        raise HTTPException(status_code=500, detail="Failed to add job to system cron")

@app.get("/api/jobs/{job_id}", response_model=CronJobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific cron job"""
    job = crud.get_cron_job(db, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return CronJobResponse.from_orm(job)

@app.put("/api/jobs/{job_id}", response_model=CronJobResponse)
def update_job(job_id: int, job_update: CronJobUpdate, db: Session = Depends(get_db)):
    """Update a cron job"""
    db_job = crud.get_cron_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Validate cron expression if provided
    if job_update.expression and not cron_service.validate_expression(job_update.expression):
        raise HTTPException(status_code=400, detail="Invalid cron expression")
    
    # Update job
    updated_job = crud.update_cron_job(db, job_id=job_id, **job_update.dict(exclude_unset=True))
    return CronJobResponse.from_orm(updated_job)

@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a cron job"""
    db_job = crud.get_cron_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Remove from system cron
    if cron_service.remove_job(db_job.name):
        # Remove from database
        crud.delete_cron_job(db, job_id=job_id)
        return {"message": "Job deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to remove job from system cron")

@app.post("/api/jobs/{job_id}/disable")
def disable_job(job_id: int, db: Session = Depends(get_db)):
    """Disable a cron job (cancel next run)"""
    db_job = crud.get_cron_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if cron_service.disable_job(db_job.name):
        crud.toggle_cron_job(db, job_id=job_id, enabled=False)
        return {"message": "Job disabled successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to disable job")

@app.post("/api/jobs/{job_id}/enable")
def enable_job(job_id: int, db: Session = Depends(get_db)):
    """Enable a cron job"""
    db_job = crud.get_cron_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if cron_service.enable_job(db_job.name):
        crud.toggle_cron_job(db, job_id=job_id, enabled=True)
        return {"message": "Job enabled successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to enable job")

@app.get("/api/system/jobs")
def get_system_jobs():
    """Get all jobs from system cron"""
    return cron_service.list_jobs()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
from sqlalchemy.orm import Session
from . import models
from typing import List, Optional

def get_cron_job(db: Session, job_id: int) -> Optional[models.CronJob]:
    return db.query(models.CronJob).filter(models.CronJob.id == job_id).first()

def get_cron_jobs(db: Session, skip: int = 0, limit: int = 100) -> List[models.CronJob]:
    return db.query(models.CronJob).offset(skip).limit(limit).all()

def create_cron_job(db: Session, name: str, expression: str, command: str, description: str = None) -> models.CronJob:
    db_job = models.CronJob(
        name=name,
        expression=expression,
        command=command,
        description=description
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def update_cron_job(db: Session, job_id: int, **kwargs) -> Optional[models.CronJob]:
    db_job = get_cron_job(db, job_id)
    if db_job:
        for key, value in kwargs.items():
            if hasattr(db_job, key):
                setattr(db_job, key, value)
        db.commit()
        db.refresh(db_job)
    return db_job

def delete_cron_job(db: Session, job_id: int) -> bool:
    db_job = get_cron_job(db, job_id)
    if db_job:
        db.delete(db_job)
        db.commit()
        return True
    return False

def toggle_cron_job(db: Session, job_id: int, enabled: bool) -> Optional[models.CronJob]:
    return update_cron_job(db, job_id, enabled=enabled) 
# THIS FILE HOLDS THE BUSINESS LOGIC FOR MANAGING JOBS, INCLUDING CREATING, UPDATING, AND RETRIEVING JOBS FROM THE DATABASE.
from typing import Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.jobs import Job, JobStatus

def create_job(db: Session, name: str) -> Job:
    job = Job()
    job.name = name
    job.status = JobStatus.PENDING
    job.created_at = datetime.now()
    job.updated_at = datetime.now()
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_job(db: Session, job_id: int) -> Job | None:
    return db.query(Job).filter(Job.id == job_id).first()


def update_job_status(
    db: Session,
    job_id: int,
    status: JobStatus,
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> Job | None:

    job = get_job(db, job_id)
    if job:
        job.status = status
        job.result = result
        job.error = error
        db.commit()
        db.refresh(job)
    else:
        return None
    return job

def start_job(db: Session, job_id: int) -> Job | None:
    return update_job_status(db, job_id, JobStatus.IN_PROGRESS)


def retry_job(db: Session, job_id: int) -> Job | None:
    job = get_job(db, job_id)
    if not job:
        return None

    if job.retries >= job.max_retries:
        return update_job_status(db, job_id, JobStatus.FAILED, error="Maximum retries reached")

    increment_job_retries(db, job_id)
    return update_job_status(db, job_id, JobStatus.PENDING, result=None, error=None)


def increment_job_retries(db: Session, job_id: int) -> Job | None:
    job = get_job(db, job_id)
    if job:
        job.retries += 1
        db.commit()
        db.refresh(job)
    else:
        return None
    return job

def mark_job_failed(db: Session, job_id: int, error: str) -> Job | None:
    return update_job_status(db, job_id, JobStatus.FAILED, error=error)

def mark_job_completed(db: Session, job_id: int, result: dict[str, Any]) -> Job | None:
    return update_job_status(db, job_id, JobStatus.COMPLETED, result=result)

def reset_job(db: Session, job_id: int) -> Job | None:
    return update_job_status(db, job_id, JobStatus.PENDING, result=None, error=None)

def delete_job(db: Session, job_id: int) -> bool:
    job = get_job(db, job_id)
    if job:
        db.delete(job)
        db.commit()
        return True
    return False

def delete_user(db: Session, user_id: int) -> bool:
    from app.services.user_service import delete_user as delete_user_service
    delete_user_service(db, user_id)
    return True

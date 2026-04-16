import os

from celery import Celery

from app.db.session import SessionLocal
from app.services import job_service

celery_app = Celery(
    "job-processing",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
)


@celery_app.task(name="app.workers.create_user")
def create_user(username: str, email: str) -> None:
    from app.models.users import User

    db = SessionLocal()
    try:
        new_user = User(name=username, email=email)
        db.add(new_user)
        db.commit()
    finally:
        db.close()


@celery_app.task(name="app.workers.process_job")
def process_job(job_id: int) -> None:
    db = SessionLocal()
    try:
        job_service.mark_job_completed(db, job_id, result={"message": "Job processed successfully"})
    finally:
        db.close()


@celery_app.task(name="app.workers.retry_job")
def retry_job(job_id: int) -> None:
    db = SessionLocal()
    try:
        job_service.retry_job(db, job_id)
    finally:
        db.close()


@celery_app.task(name="app.workers.fail_job")
def fail_job(job_id: int, error_message: str) -> None:
    db = SessionLocal()
    try:
        job_service.mark_job_failed(db, job_id, error=error_message)
    finally:
        db.close()


__all__ = ["celery_app", "create_user", "process_job", "retry_job", "fail_job"]
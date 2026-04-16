from fastapi import APIRouter, Depends, HTTPException
from app.services import job_service
from app.db.session import get_db
from app.models.jobs import JobStatus
from sqlalchemy.orm import Session



router = APIRouter()

@router.get("/health")
def read_root():
    return {"status": "healthy",
            "message": "Welcome to the Job Processing API!",
            "version": "1.0.0"}

@router.post("/jobs")
def create_job(name: str, db: Session = Depends(get_db)):
    new_job = job_service.create_job(db, name)
    return new_job

@router.post("/jobs/{job_id}/start")
def start_job(job_id: int, db: Session = Depends(get_db)):
    job_service.start_job(db, job_id)
    return {"message": f"Job {job_id} started!"}

@router.get("/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = job_service.get_job(db, job_id)
    return job

@router.post("/jobs/{job_id}/retry")
def retry_job(job_id: int, db: Session = Depends(get_db)):
    job_service.retry_job(db, job_id)
    return {"message": f"Job {job_id} retry attempted!"}

@router.put("/jobs/{job_id}/status")
def update_job_status(job_id: int, status: str, db: Session = Depends(get_db)):
    try:
        parsed_status = JobStatus(status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}") from exc

    job_service.update_job_status(db, job_id, parsed_status)
    return {"message": f"Job {job_id} status updated to {status}!"}

@router.post("/users/", status_code=202)
def create_user_route(username: str, email: str):
    from app.workers.celery_app import celery_app

    celery_app.send_task("app.workers.create_user", args=[username, email])
    return {"message": f"User creation for {username} has been queued!"}

@router.get("/users/{user_name}")
def get_user_route(user_name: str):
    from app.workers.celery_app import celery_app

    result = celery_app.send_task("app.workers.get_user", args=[user_name])
    user_data = result.get(timeout=10)  # Wait for the result with a timeout
    if user_data is None:
        raise HTTPException(status_code=404, detail=f"User {user_name} not found")
    return user_data

@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    db.delete(job)
    db.commit()
    return {"message": f"Job {job_id} deleted successfully!"}
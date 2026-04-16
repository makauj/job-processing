from fastapi import APIRouter, Depends, HTTPException
from app.services import job_service
from app.services import user_service
from app.db.session import get_db
from app.models.jobs import JobStatus
from app.schema.users import UserCreate, UserLogin
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

@router.post("/users/", status_code=201)
def create_user_route(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        user = user_service.create_user(
            db,
            username=payload.username,
            password=payload.password,
            email=payload.email,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {
        "id": user.id,
        "username": user.name,
        "email": user.email,
        "created_at": user.created_at,
    }

@router.post("/login")
def login_route(payload: UserLogin, db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.name,
            "email": user.email,
        },
    }

@router.get("/users/{user_name}")
def get_user_route(user_name: str, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_name} not found")

    return {
        "id": user.id,
        "username": user.name,
        "email": user.email,
        "created_at": user.created_at,
    }

@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    deleted = job_service.delete_job(db, job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return {"message": f"Job {job_id} deleted successfully!"}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted = job_service.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return {"message": f"User {user_id} deleted successfully!"}

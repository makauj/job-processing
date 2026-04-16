# Job Processing

This is a personal project meant to showcase my programming skills. I am building a job processing web app that takes in tasks and processes them.

## How I am building the project

Below is a structured build plan for a **job processing platform** designed to demonstrate backend depth using Python. The emphasis is on clean architecture, asynchronous processing, and production-ready practices.

---

### Tech Stack

* API framework: FastAPI
* Task queue: Celery
* Broker / cache: Redis
* Database: PostgreSQL
* ORM: SQLAlchemy (or SQLModel for tighter FastAPI integration)
* Containerization: Docker
* API docs: OpenAPI (auto via FastAPI)

Optional but valuable:

* Auth: JWT (via python-jose)
* Background scheduler: Celery Beat
* Monitoring: Flower (Celery dashboard)

---

### Core Features

I am building a system that:

* Accepts jobs (via API)
* Queues them
* Processes asynchronously
* Tracks status/results
* Retries failures
* Supports multiple job types

Example job types:

* Image resize
* Email sending
* Data report generation

---

### High-Level Architecture

Client → FastAPI → PostgreSQL (job metadata)
→ Redis (queue broker) → Celery Workers → Results stored back in DB

---

## Run API + Celery Worker (local)

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start Redis (required by Celery broker):

```bash
docker run --name job-processing-redis -p 6379:6379 redis:7
```

3. Optional environment variables:

```bash
# Defaults to sqlite:///./job_processing.db
DATABASE_URL=sqlite:///./job_processing.db

# Defaults to redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
```

4. Start FastAPI:

```bash
uvicorn app.main:app --reload
```

5. Start Celery worker (separate terminal):

```bash
celery -A app.workers.celery_app:celery_app worker --loglevel=info
```

6. Queue a user creation task:

```bash
curl -X POST "http://127.0.0.1:8000/users/?username=alice&email=alice@example.com"
```

## Current Implementation Status (April 16, 2026)

Overall progress against the 12-step plan: about 45% complete.

| Step | Status | Notes |
| --- | --- | --- |
| 1. Project setup | Completed | FastAPI app structure is in place and dependencies are installable. |
| 2. Database design | In progress | Jobs and users models exist, but migrations are not implemented yet. |
| 3. Basic FastAPI app | In progress | Health, create/get/start/retry/update job endpoints exist; job listing/pagination is still missing. |
| 4. Integrate Celery | In progress | Celery broker and worker tasks are configured; user creation is queued asynchronously. |
| 5. Worker logic | In progress | Core task functions are present, but execution flow and production-grade task orchestration are still minimal. |
| 6. Status synchronization | In progress | Status updates and retry behavior exist in service logic; Celery signals/backoff are not implemented. |
| 7. Authentication | Not started | JWT auth and protected routes are not implemented. |
| 8. Caching layer | Not started | No Redis caching or rate limiting implemented yet. |
| 9. Observability | Not started | Structured logging, metrics, and Flower setup are not implemented. |
| 10. Dockerize system | Not started | Docker folder exists, but container definitions are not implemented yet. |
| 11. Testing | In progress | A smoke test exists for user queue dispatch; broader unit/integration coverage is still needed. |
| 12. Deployment | Not started | No deployment configuration/pipeline implemented yet. |

### What is currently working

* Job CRUD-like workflow for create, fetch, start, retry, and manual status update.
* Celery task module and worker startup path.
* Async queue dispatch from `POST /users/`.
* Local startup flow for API + Redis + Celery worker.
* Basic test coverage for queue dispatch.

## Step-by-Step Build Plan

### Step 1 - Project Setup

* Create repo and virtual environment

* Install dependencies:

  * fastapi, uvicorn
  * celery, redis
  * sqlalchemy, psycopg2
  * pydantic

* Initialize Git with a clean README

---

### Step 2 - Database Design

Create a `jobs` table:

Fields:

* id (UUID)
* type (string)
* status (pending, running, success, failed)
* payload (JSON)
* result (JSON)
* retries (int)
* created_at, updated_at

Set up migrations (Alembic recommended).

---

### Step 3 - Basic FastAPI App

Implement:

* POST `/jobs` → submit a job
* GET `/jobs/{id}` → check status
* GET `/jobs` → list jobs (pagination)

At this stage:

* Store jobs in DB
* Return mock responses (no Celery yet)

---

### Step 4 - Integrate Celery

* Configure Celery with Redis broker
* Create a worker service

Define tasks:

* `process_image`
* `send_email`
* `generate_report`

Modify job creation:

* When job is created → enqueue Celery task
* Store Celery task ID in DB

---

### Step 5 - Worker Logic

Each task should:

* Update job status → running
* Execute logic
* Save result → success
* Handle exceptions → failed
* Increment retries if needed

---

### Step 6 - Status Synchronization

Ensure:

* Worker updates DB directly OR
* Use Celery signals to track task lifecycle

Add retry logic:

* Automatic retries (Celery config)
* Backoff strategy

---

### Step 7 - Add Authentication

* JWT-based auth
* Protect endpoints
* Associate jobs with users

---

### Step 8 - Add Caching Layer

Use Redis for:

* Frequently requested job results
* Rate limiting

---

### Step 9 - Add Observability

* Logging (structured logs)
* Add Flower for monitoring Celery tasks
* Track failures and durations

---

### Step 10 - Dockerize the System

Create services:

* api
* worker
* redis
* postgres

Use docker-compose to run everything together.

---

### Step 11 - Testing

* Unit tests for services
* Integration tests for API + queue
* Mock Celery where needed

---

### Step 12 - Deployment

Deploy to a cloud platform:

* Single VM (simplest) OR
* Managed services (advanced)

Expose:

* API endpoint
* Optional monitoring dashboard

---

## Recommended Folder Structure

Keep it modular and production-like:

```bash
        job-platform/
        │
        ├── app/
        │   ├── main.py              # FastAPI entrypoint
        │   ├── api/                 # Routes
        │   │   ├── routes_jobs.py
        │   │   └── deps.py
        │   │
        │   ├── core/                # Config, settings
        │   │   ├── config.py
        │   │   └── security.py
        │   │
        │   ├── models/              # SQLAlchemy models
        │   │   └── job.py
        │   │
        │   ├── schemas/             # Pydantic schemas
        │   │   └── job.py
        │   │
        │   ├── services/            # Business logic
        │   │   └── job_service.py
        │   │
        │   ├── db/                  # DB connection/session
        │   │   ├── base.py
        │   │   └── session.py
        │   │
        │   └── workers/             # Celery tasks
        │       ├── celery_app.py
        │       └── tasks.py
        │
        ├── tests/
        │
        ├── docker/
        │   ├── Dockerfile.api
        │   ├── Dockerfile.worker
        │   └── docker-compose.yml
        │
        ├── alembic/                 # migrations
        │
        ├── requirements.txt
        └── README.md
```

---

## Why I chose this Project

This project signals:

* Understanding of async systems (queues, workers)
* Real-world backend patterns (retry, failure handling)
* Clean architecture (separation of concerns)
* Deployment knowledge (Dockerized services)

---

## Optional Enhancements (High Impact)

* Priority queues (high vs low jobs)
* Scheduled jobs (Celery Beat)
* WebSocket updates for live status
* Multi-tenant support
* File upload handling (S3 or local storage)

from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


def test_create_user_endpoint_creates_user():
    username = f"alice-{uuid4().hex[:8]}"
    email = f"{username}@example.com"

    client = TestClient(app)
    response = client.post(
        "/users/",
        json={"username": username, "password": "secret123", "email": email},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == username
    assert body["email"] == email
    assert body["id"] > 0


def test_login_endpoint_accepts_valid_credentials():
    username = f"bob-{uuid4().hex[:8]}"
    email = f"{username}@example.com"

    client = TestClient(app)
    create_response = client.post(
        "/users/",
        json={"username": username, "password": "secret123", "email": email},
    )

    assert create_response.status_code == 201

    login_response = client.post(
        "/login",
        json={"username": username, "password": "secret123"},
    )

    assert login_response.status_code == 200
    assert login_response.json()["message"] == "Login successful"
    assert login_response.json()["user"]["username"] == username


def test_delete_job_endpoint_deletes_existing_job():
    job_name = f"cleanup-{uuid4().hex[:8]}"

    client = TestClient(app)
    create_response = client.post("/jobs", params={"name": job_name})

    assert create_response.status_code == 200
    job_id = create_response.json()["id"]

    delete_response = client.delete(f"/jobs/{job_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Job {job_id} deleted successfully!"

    missing_response = client.delete(f"/jobs/{job_id}")

    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == f"Job {job_id} not found"

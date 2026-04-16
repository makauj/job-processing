from fastapi.testclient import TestClient

from app.main import app
from app.workers import celery_app as celery_module


def test_create_user_endpoint_queues_task(monkeypatch):
    captured: dict[str, object] = {}

    def fake_send_task(name, args=None, kwargs=None, **_options):
        captured["name"] = name
        captured["args"] = args
        captured["kwargs"] = kwargs
        return None

    monkeypatch.setattr(celery_module.celery_app, "send_task", fake_send_task)

    client = TestClient(app)
    response = client.post(
        "/users/",
        params={"username": "alice", "email": "alice@example.com"},
    )

    assert response.status_code == 202
    assert response.json() == {"message": "User creation for alice has been queued!"}
    assert captured["name"] == "app.workers.create_user"
    assert captured["args"] == ["alice", "alice@example.com"]

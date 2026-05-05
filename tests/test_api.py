from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_document():
    response = client.post("/documents", json={
        "user_id": "test_user",
        "title": "Test",
        "content": "This is a test"
    })

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "queued"
    assert "document_id" in data


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
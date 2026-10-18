from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_mood_checkin_validation():
    response = client.post("/api/checkins", json={"mood":"okay","stress":3,"energy":4,"note":"demo"})
    assert response.status_code == 200
    assert response.json()["mood"] == "okay"

def test_task_create_and_list():
    created = client.post("/api/tasks", json={"title":"Réviser SQL","duration_minutes":45,"priority":"high"})
    assert created.status_code == 200
    listed = client.get("/api/tasks")
    assert listed.status_code == 200
    assert any(task["title"] == "Réviser SQL" for task in listed.json())

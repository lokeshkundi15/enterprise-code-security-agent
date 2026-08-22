from fastapi.testclient import TestClient
from app.api.routes import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_webhook_idempotency():
    delivery_id = "delivery-uuid-999"
    payload = {
        "pull_request": {"number": 105},
        "diff": "diff --git a/app.py b/app.py\n+x = 1"
    }
    headers = {"X-GitHub-Delivery": delivery_id}
    
    # First delivery
    res1 = client.post("/api/v1/webhook/github", json=payload, headers=headers)
    assert res1.status_code == 200
    assert res1.json()["status"] == "success"
    
    # Duplicate delivery
    res2 = client.post("/api/v1/webhook/github", json=payload, headers=headers)
    assert res2.status_code == 200
    assert res2.json()["status"] == "skipped"
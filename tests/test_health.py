from fastapi.testclient import TestClient
from api.api import api


def test_health_live():
    client = TestClient(api)
    r = client.get("/health/live")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "alive"
    assert "uptime_s" in body

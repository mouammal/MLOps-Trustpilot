from fastapi.testclient import TestClient
from api.api import api  

client = TestClient(api)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API de prédiction Trustpilot !"}

def test_predict_label():
    response = client.post("/predict-label", json={"text": "Service rapide"})
    assert response.status_code == 200
    assert "label" in response.json()

def test_predict_score():
    response = client.post("/predict-score", json={"text": "Produit excellent"})
    assert response.status_code == 200
    assert "score" in response.json()
    assert 0 <= response.json()["score"] <= 5

# tests/test_predict_integration.py
import os
import pytest
from fastapi.testclient import TestClient
from sklearn.dummy import DummyClassifier, DummyRegressor
from unittest.mock import patch
from api.api import api

# ----------------------------
# Variables d'env
# ----------------------------
ADMIN_USERNAME = os.getenv("API_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("API_ADMIN_PASSWORD", "adminpass")
CLIENT_USERNAME = os.getenv("API_CLIENT_USERNAME", "client")
CLIENT_PASSWORD = os.getenv("API_CLIENT_PASSWORD", "clientpass")


# ----------------------------
# Fixture client
# ----------------------------
@pytest.fixture(scope="module")
def client():
    api.router.on_startup = []

    api.state.label_model = DummyClassifier(strategy="constant", constant="Autre").fit(
        [["x"]], ["Autre"]
    )
    api.state.score_model = DummyRegressor(strategy="constant", constant=4.2).fit(
        [[0]], [4.2]
    )

    with TestClient(api) as c:
        yield c


# ----------------------------
# Mock authenticate_user pour bypass mot de passe
# ----------------------------
@pytest.fixture(autouse=True)
def mock_auth():
    with patch("api.security.auth.authenticate_user") as mock_auth_fn:

        def _fake_auth(username, password):
            if username == ADMIN_USERNAME:
                return {"username": ADMIN_USERNAME, "role": "admin"}
            if username == CLIENT_USERNAME:
                return {"username": CLIENT_USERNAME, "role": "client"}
            return False

        mock_auth_fn.side_effect = _fake_auth
        yield


# ----------------------------
# Helper token
# ----------------------------
def get_token(client, username, password):
    r = client.post(
        "/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    return r.json()["access_token"]


# ----------------------------
# Tests d'intégration
# ----------------------------
def test_predict_endpoints_with_dummy_models(client):
    admin_token = get_token(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    client_token = get_token(client, CLIENT_USERNAME, CLIENT_PASSWORD)

    h_admin = {"Authorization": f"Bearer {admin_token}"}
    h_client = {"Authorization": f"Bearer {client_token}"}

    # Client → /predict-label OK
    r1 = client.post(
        "/predict-label", json={"text": "livraison rapide"}, headers=h_client
    )
    assert r1.status_code == 200
    assert "label" in r1.json()
    assert isinstance(r1.json()["label"], str)

    # Admin → /predict-label OK
    r2 = client.post("/predict-label", json={"text": "okkk"}, headers=h_admin)
    assert r2.status_code == 200
    assert "label" in r2.json()
    assert isinstance(r2.json()["label"], str)

    # Admin → /predict-score OK
    r3 = client.post("/predict-score", json={"text": "Très déçu"}, headers=h_admin)
    assert r3.status_code == 200
    score = r3.json()["score"]
    assert isinstance(score, (int, float))
    assert 0 <= score <= 5  # DummyRegressor constant=4.2

    # Client → /predict-score FORBIDDEN
    r4 = client.post("/predict-score", json={"text": "x"}, headers=h_client)
    assert r4.status_code == 403

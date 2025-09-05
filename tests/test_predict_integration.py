# tests/test_predict_integration.py
import os
import pytest
from fastapi.testclient import TestClient
from sklearn.dummy import DummyClassifier, DummyRegressor
from unittest.mock import patch
from api.api import api

# ----------------------------
# Variables d'env (optionnelles)
# ----------------------------
ADMIN_USERNAME = os.getenv("API_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("API_ADMIN_PASSWORD", "password")
CLIENT_USERNAME = os.getenv("API_CLIENT_USERNAME", "client")
CLIENT_PASSWORD = os.getenv("API_CLIENT_PASSWORD", "password")


# ----------------------------
# Fixture client
# ----------------------------
@pytest.fixture(scope="module")
def client():
    api.router.on_startup = []  # désactiver startup
    # Modèles dummy
    api.state.label_model = DummyClassifier(strategy="constant", constant="Autre").fit(
        [["x"]], ["Autre"]
    )
    api.state.score_model = DummyRegressor(strategy="constant", constant=4.2).fit(
        [[0]], [4.2]
    )
    with TestClient(api) as c:
        yield c


# ----------------------------
# Mock DB / auth
# ----------------------------
@pytest.fixture(autouse=True)
def mock_db_auth():
    """Bypass PostgreSQL pour /token."""
    with patch("api.security.auth.get_user_from_db") as mock_user:
        # On renvoie un user générique pour admin et client
        mock_user.side_effect = lambda username: {
            "username": username,
            "hashed_password": "fakehash",
            "role": "admin" if username == ADMIN_USERNAME else "client",
        }
        yield


def get_token(client, username, password):
    """Token factice pour bypass /token"""
    return "fake-token"


# ----------------------------
# Tests d'intégration
# ----------------------------
def test_predict_endpoints_with_dummy_models(client):
    admin_token = get_token(client, ADMIN_USERNAME, "pass")
    client_token = get_token(client, CLIENT_USERNAME, "pass")

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

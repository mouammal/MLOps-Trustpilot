import os
import pytest
from fastapi.testclient import TestClient
from sklearn.dummy import DummyClassifier, DummyRegressor
from unittest.mock import patch
from api.api import api
from api.security.auth import create_access_token

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
        # retourne un utilisateur admin ou client selon username
        def fake_user(username):
            if username == ADMIN_USERNAME:
                return {
                    "username": ADMIN_USERNAME,
                    "hashed_password": "fakehash",
                    "role": "admin",
                }
            else:
                return {
                    "username": CLIENT_USERNAME,
                    "hashed_password": "fakehash",
                    "role": "client",
                }

        mock_user.side_effect = fake_user
        yield


def get_token(client, username, password):
    """Génère un JWT valide pour tests"""
    # rôle pour l’endpoint
    role = "admin" if username == ADMIN_USERNAME else "client"
    token = create_access_token({"sub": username, "role": role})
    return token


# ----------------------------
# Tests
# ----------------------------
def test_predict_label_admin_and_client(client):
    for username in [ADMIN_USERNAME, CLIENT_USERNAME]:
        token = get_token(client, username, "pass")
        r = client.post(
            "/predict-label",
            json={"text": "Service rapide"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        body = r.json()
        assert "label" in body
        assert isinstance(body["label"], str)


def test_predict_score_admin_only(client):
    token = get_token(client, ADMIN_USERNAME, "pass")
    r = client.post(
        "/predict-score",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    score = r.json()["score"]
    assert isinstance(score, (int, float))
    assert 0 <= score <= 5


def test_predict_score_client_forbidden(client):
    token = get_token(client, CLIENT_USERNAME, "pass")
    r = client.post(
        "/predict-score",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_predict_label_unauthenticated(client):
    r = client.post("/predict-label", json={"text": "Service rapide"})
    assert r.status_code == 401

# tests/test_predict_integration.py
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sklearn.dummy import DummyClassifier, DummyRegressor

from api.api import api

# Récupérer les identifiants depuis l'environnement (CI ou .env)
ADMIN_USERNAME = os.getenv("API_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("API_ADMIN_PASSWORD", "admin")
CLIENT_USERNAME = os.getenv("API_CLIENT_USERNAME", "client")
CLIENT_PASSWORD = os.getenv("API_CLIENT_PASSWORD", "client")

# Skip si les creds ne sont pas fournies (utile localement)
SKIP_AUTH = not all([ADMIN_USERNAME, ADMIN_PASSWORD, CLIENT_USERNAME, CLIENT_PASSWORD])
skip_if_no_auth = pytest.mark.skipif(
    SKIP_AUTH,
    reason="Identifiants API manquants dans .env ou variables d'environnement",
)


@pytest.fixture(scope="module", autouse=True)
def mock_db_and_models():
    # Mock DB auth
    with patch("api.security.auth.get_user_from_db") as mock_get_user:

        def _fake_get_user(username):
            if username == ADMIN_USERNAME:
                return {
                    "username": ADMIN_USERNAME,
                    "password": "$2b$12$fakehashedadmin",
                    "role": "admin",
                }
            if username == CLIENT_USERNAME:
                return {
                    "username": CLIENT_USERNAME,
                    "password": "$2b$12$fakehashedclient",
                    "role": "client",
                }
            return None

        mock_get_user.side_effect = _fake_get_user

        # Injecter des modèles déterministes
        api.state.label_model = DummyClassifier(
            strategy="constant", constant="Autre"
        ).fit([["x"]], ["Autre"])
        api.state.score_model = DummyRegressor(strategy="constant", constant=4.2).fit(
            [[0]], [4.2]
        )

        yield


@pytest.fixture
def client():
    return TestClient(api)


def get_token(client, username, password):
    """Helper pour obtenir un token via /token"""
    r = client.post(
        "/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, f"Échec /token pour {username}"
    return r.json()["access_token"]


# -------------------------
# Tests intégration endpoints
# -------------------------


@skip_if_no_auth
def test_predict_label_admin_and_client(client):
    admin_token = get_token(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    client_token = get_token(client, CLIENT_USERNAME, CLIENT_PASSWORD)

    # Admin
    r_admin = client.post(
        "/predict-label",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r_admin.status_code == 200
    assert r_admin.json()["label"] == "Autre"

    # Client
    r_client = client.post(
        "/predict-label",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r_client.status_code == 200
    assert r_client.json()["label"] == "Autre"


@skip_if_no_auth
def test_predict_score_admin_only(client):
    admin_token = get_token(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    r = client.post(
        "/predict-score",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.json()["score"] == 4.2


@skip_if_no_auth
def test_predict_score_client_forbidden(client):
    client_token = get_token(client, CLIENT_USERNAME, CLIENT_PASSWORD)
    r = client.post(
        "/predict-score",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 403


def test_predict_label_unauthenticated(client):
    r = client.post("/predict-label", json={"text": "Service rapide"})
    assert r.status_code == 401


def test_predict_score_unauthenticated(client):
    r = client.post("/predict-score", json={"text": "Service rapide"})
    assert r.status_code == 401

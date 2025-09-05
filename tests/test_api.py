# tests/test_api.py
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
    api.router.on_startup = []  # désactiver le startup réel

    # Modèles Dummy pour bypasser les vrais artefacts
    api.state.label_model = DummyClassifier(strategy="constant", constant="Autre").fit(
        [["x"]], ["Autre"]
    )
    api.state.score_model = DummyRegressor(strategy="constant", constant=4.2).fit(
        [[0]], [4.2]
    )

    with TestClient(api) as c:
        yield c


# ----------------------------
# Mock DB pour /token
# ----------------------------
@pytest.fixture(autouse=True)
def mock_user_db():
    """
    Mock get_user_from_db pour bypasser PostgreSQL.
    Renvoie des users valides pour admin et client.
    """
    with patch("api.security.auth.get_user_from_db") as mock_user:

        def _get_user(username):
            if username == ADMIN_USERNAME:
                return {
                    "username": ADMIN_USERNAME,
                    "hashed_password": "fakehash",
                    "role": "admin",
                }
            if username == CLIENT_USERNAME:
                return {
                    "username": CLIENT_USERNAME,
                    "hashed_password": "fakehash",
                    "role": "client",
                }
            return None

        mock_user.side_effect = _get_user
        yield


# ----------------------------
# Helper token via /token réel (FastAPI va utiliser le mock)
# ----------------------------
def get_token(client, username, password):
    r = client.post(
        "/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, f"Échec /token pour {username}"
    return r.json()["access_token"]


# ----------------------------
# Tests
# ----------------------------
def test_predict_label_admin_and_client(client):
    for username, password in [
        (ADMIN_USERNAME, ADMIN_PASSWORD),
        (CLIENT_USERNAME, CLIENT_PASSWORD),
    ]:
        token = get_token(client, username, password)
        r = client.post(
            "/predict-label",
            json={"text": "Service rapide"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        assert "label" in r.json()


def test_predict_score_admin_only(client):
    token = get_token(client, ADMIN_USERNAME, ADMIN_PASSWORD)
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
    token = get_token(client, CLIENT_USERNAME, CLIENT_PASSWORD)
    r = client.post(
        "/predict-score",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_predict_label_unauthenticated(client):
    # Pas de token → 401
    r = client.post("/predict-label", json={"text": "Service rapide"})
    assert r.status_code == 401

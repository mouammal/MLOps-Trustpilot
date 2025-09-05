# tests/test_api.py
import os
import pytest
from fastapi.testclient import TestClient
from sklearn.dummy import DummyClassifier, DummyRegressor
from api.api import api

# ----------------------------
# Variables d'environnement (optionnelles)
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
    # Désactiver le startup réel
    api.router.on_startup = []

    # Injecter des modèles Dummy
    api.state.label_model = DummyClassifier(strategy="constant", constant="Autre").fit(
        [["x"]], ["Autre"]
    )
    api.state.score_model = DummyRegressor(strategy="constant", constant=4.2).fit(
        [[0]], [4.2]
    )

    # Bypass complet de l'authentification
    from api.security import auth

    api.dependency_overrides[auth.get_current_user] = lambda: {
        "username": "admin",
        "role": "admin",
    }

    with TestClient(api) as c:
        yield c

    # Nettoyer l'override après les tests
    api.dependency_overrides = {}


# ----------------------------
# Token factice
# ----------------------------
def get_token(client, username, password):
    return "fake-token"


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
        assert "label" in r.json()
        assert isinstance(r.json()["label"], str)


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
    # Simuler un client non-admin
    api.dependency_overrides["get_current_user"] = lambda: {
        "username": CLIENT_USERNAME,
        "role": "client",
    }

    token = get_token(client, CLIENT_USERNAME, "pass")
    r = client.post(
        "/predict-score",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403

    # Restaurer l'override admin pour les autres tests
    from api.security import auth

    api.dependency_overrides[auth.get_current_user] = lambda: {
        "username": "admin",
        "role": "admin",
    }


def test_predict_label_unauthenticated(client):
    # Pas de token → 401
    r = client.post("/predict-label", json={"text": "Service rapide"})
    assert r.status_code == 401

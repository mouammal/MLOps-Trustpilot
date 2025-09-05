# tests/test_predict_integration.py
import os
import pytest
from fastapi.testclient import TestClient
from sklearn.dummy import DummyClassifier, DummyRegressor
from unittest.mock import patch

from api.api import api

# Charger les identifiants depuis .env
from dotenv import load_dotenv

load_dotenv()

ADMIN_USERNAME = os.getenv("API_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("API_ADMIN_PASSWORD", "password")
CLIENT_USERNAME = os.getenv("API_CLIENT_USERNAME", "client")
CLIENT_PASSWORD = os.getenv("API_CLIENT_PASSWORD", "password")

SKIP_AUTH = not all([ADMIN_USERNAME, ADMIN_PASSWORD, CLIENT_USERNAME, CLIENT_PASSWORD])
skip_if_no_auth = pytest.mark.skipif(
    SKIP_AUTH, reason="Identifiants API manquants dans .env"
)


# ----------------------------
# Fixture client avec modèles Dummy
# ----------------------------
@pytest.fixture(scope="module")
def client():
    api.router.on_startup = []  # Désactive le startup

    # Injection modèles Dummy
    clf = DummyClassifier(strategy="constant", constant="Autre").fit([["x"]], ["Autre"])
    reg = DummyRegressor(strategy="constant", constant=4.2).fit([[0]], [4.2])
    api.state.label_model = clf
    api.state.score_model = reg

    with TestClient(api) as c:
        yield c


# ----------------------------
# Mock DB et auth
# ----------------------------
@pytest.fixture(autouse=True)
def mock_db_auth():
    """Mock get_user_from_db pour bypass PostgreSQL."""
    with patch("api.security.auth.get_user_from_db") as mocked:
        mocked.return_value = {
            "username": "admin",
            "hashed_password": "fakehash",
            "role": "admin",
        }
        yield


# ----------------------------
# Helper token factice
# ----------------------------
def _get_token(client: TestClient, username: str, password: str) -> str:
    """Retourne un token factice pour bypass l'auth réelle."""
    return "fake-token"


# ----------------------------
# Tests
# ----------------------------
@skip_if_no_auth
def test_predict_endpoints_with_dummy_models(client):
    admin_token = _get_token(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    client_token = _get_token(client, CLIENT_USERNAME, CLIENT_PASSWORD)
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
    assert isinstance(r2.json()["label"], str)

    # Admin → /predict-score OK
    r3 = client.post("/predict-score", json={"text": "Très déçu"}, headers=h_admin)
    assert r3.status_code == 200
    score = r3.json()["score"]
    assert isinstance(score, (int, float))
    assert 0 <= float(score) <= 5  # DummyRegressor constant=4.2

    # Client → /predict-score FORBIDDEN
    r4 = client.post("/predict-score", json={"text": "x"}, headers=h_client)
    assert r4.status_code == 403

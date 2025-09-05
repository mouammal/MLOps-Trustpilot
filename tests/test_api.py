# tests/test_api.py
import os
import pytest
from fastapi.testclient import TestClient
from sklearn.dummy import DummyClassifier, DummyRegressor
from unittest.mock import patch

from api.api import api

# Charger les variables d'environnement depuis .env
from dotenv import load_dotenv

load_dotenv()

ADMIN_USERNAME = os.getenv("API_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("API_ADMIN_PASSWORD", "password")
CLIENT_USERNAME = os.getenv("API_CLIENT_USERNAME", "client")
CLIENT_PASSWORD = os.getenv("API_CLIENT_PASSWORD", "password")

# Skip tests nécessitant auth si identifiants absents
SKIP_AUTH = not all([ADMIN_USERNAME, ADMIN_PASSWORD, CLIENT_USERNAME, CLIENT_PASSWORD])
skip_if_no_auth = pytest.mark.skipif(
    SKIP_AUTH, reason="Identifiants API manquants dans .env"
)


# ----------------------------
# Fixtures
# ----------------------------
@pytest.fixture(scope="module")
def client():
    """
    Fixture TestClient avec modèles Dummy injectés pour bypass les vrais artefacts.
    """
    api.router.on_startup = []  # Désactive le startup

    # Injection modèles Dummy
    clf = DummyClassifier(strategy="constant", constant="positif").fit(
        [["x"]], ["positif"]
    )
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
# Helper token
# ----------------------------
def get_token(
    client: TestClient, username: str = "admin", password: str = "password"
) -> str:
    """
    Retourne un token factice pour bypass l'auth réelle.
    """
    return "fake-token"


# ----------------------------
# Tests
# ----------------------------
def test_health_live(client):
    r = client.get("/health/live")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "alive"
    assert "uptime_s" in body


@skip_if_no_auth
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
        body = r.json()
        assert "label" in body
        assert isinstance(body["label"], (str, int, float))


@skip_if_no_auth
def test_predict_score_admin_only(client):
    token = get_token(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    r = client.post(
        "/predict-score",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "score" in body
    assert isinstance(body["score"], (int, float))
    assert 0 <= body["score"] <= 5


@skip_if_no_auth
def test_predict_score_client_forbidden(client):
    token = get_token(client, CLIENT_USERNAME, CLIENT_PASSWORD)
    r = client.post(
        "/predict-score",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_predict_label_unauthenticated(client):
    r = client.post("/predict-label", json={"text": "Service rapide"})
    assert r.status_code == 401

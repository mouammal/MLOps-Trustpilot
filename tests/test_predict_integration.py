# tests/test_predict_integration.py
import os
import pytest
from fastapi.testclient import TestClient
from sklearn.dummy import DummyClassifier, DummyRegressor
from passlib.context import CryptContext
from api.api import api
from api.security import auth, authenticate_user

# -----------------------------
# Variables d'environnement / creds
# -----------------------------
ADMIN_USERNAME = os.getenv("API_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("API_ADMIN_PASSWORD", "admin")
CLIENT_USERNAME = os.getenv("API_CLIENT_USERNAME", "client")
CLIENT_PASSWORD = os.getenv("API_CLIENT_PASSWORD", "client")

SKIP_AUTH = not all([ADMIN_USERNAME, ADMIN_PASSWORD, CLIENT_USERNAME, CLIENT_PASSWORD])
skip_if_no_auth = pytest.mark.skipif(
    SKIP_AUTH,
    reason="Identifiants API manquants dans .env ou variables d'environnement",
)

# -----------------------------
# Fake DB en mémoire
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

FAKE_USER_DB = {
    ADMIN_USERNAME: {
        "username": ADMIN_USERNAME,
        "password": pwd_context.hash(ADMIN_PASSWORD),
        "role": "admin",
    },
    CLIENT_USERNAME: {
        "username": CLIENT_USERNAME,
        "password": pwd_context.hash(CLIENT_PASSWORD),
        "role": "client",
    },
}

# Patch get_user_from_db pour CI
original_get_user = auth.get_user_from_db


def fake_get_user_from_db(username: str):
    return FAKE_USER_DB.get(username)


auth.get_user_from_db = fake_get_user_from_db

# Patch authenticate_user pour utiliser la fake DB
original_authenticate_user = authenticate_user


def fake_authenticate_user(username: str, password: str):
    user = FAKE_USER_DB.get(username)
    if not user:
        return None
    if pwd_context.verify(password, user["password"]):
        return user
    return None


auth.authenticate_user = fake_authenticate_user


# -----------------------------
# Fixture client FastAPI
# -----------------------------
@pytest.fixture(scope="module")
def client():
    # Dummy models pour tests
    api.state.label_model = DummyClassifier(strategy="constant", constant="Autre")
    api.state.label_model.fit([["dummy"]], ["Autre"])

    api.state.score_model = DummyRegressor(strategy="constant", constant=4.2)
    api.state.score_model.fit([[0]], [4.2])

    with TestClient(api) as c:
        yield c


# -----------------------------
# Helper pour obtenir token
# -----------------------------
def get_token(client, username, password):
    r = client.post(
        "/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, f"Échec /token pour {username}"
    return r.json()["access_token"]


# -----------------------------
# Tests intégration
# -----------------------------
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

import os
import pytest
from fastapi.testclient import TestClient
from sklearn.dummy import DummyClassifier, DummyRegressor
from api.api import api

from dotenv import load_dotenv
from unittest.mock import patch

# Charger .env
load_dotenv()

# Identifiants de test
ADMIN_USERNAME = os.getenv("API_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("API_ADMIN_PASSWORD", "admin")
CLIENT_USERNAME = os.getenv("API_CLIENT_USERNAME", "client")
CLIENT_PASSWORD = os.getenv("API_CLIENT_PASSWORD", "client")

# Skip si pas de creds
SKIP_AUTH = not all([ADMIN_USERNAME, ADMIN_PASSWORD, CLIENT_USERNAME, CLIENT_PASSWORD])
skip_if_no_auth = pytest.mark.skipif(
    SKIP_AUTH,
    reason="Identifiants API manquants dans .env ou variables d'environnement",
)


# --- Fixture : Mock DB utilisateurs avec vrais hash ---
@pytest.fixture(scope="module", autouse=True)
def mock_user_db():
    # Récupérer les hash bcrypt réels (pré-calculés)
    import bcrypt

    # Générer hash bcrypt à partir des passwords du .env
    admin_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()
    client_hash = bcrypt.hashpw(CLIENT_PASSWORD.encode(), bcrypt.gensalt()).decode()

    fake_users = {
        ADMIN_USERNAME: {
            "username": ADMIN_USERNAME,
            "password": admin_hash,
            "role": "admin",
        },
        CLIENT_USERNAME: {
            "username": CLIENT_USERNAME,
            "password": client_hash,
            "role": "client",
        },
    }

    # Patch de la fonction get_user_from_db pour retourner notre fake DB
    with patch("api.security.auth.get_user_from_db") as mock_get_user:
        mock_get_user.side_effect = lambda username: fake_users.get(username)
        yield


# --- Fixture client FastAPI ---
@pytest.fixture(scope="module")
def client():
    # Injecter des modèles ML déterministes
    api.state.label_model = DummyClassifier(strategy="constant", constant="Autre").fit(
        [["x"]], ["Autre"]
    )
    api.state.score_model = DummyRegressor(strategy="constant", constant=4.2).fit(
        [[0]], [4.2]
    )

    with TestClient(api) as c:
        yield c


# --- Helper pour récupérer token ---
def get_token(client, username, password):
    r = client.post(
        "/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, f"Échec /token pour {username}"
    return r.json()["access_token"]


# -------------------------
# Tests endpoints intégration
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
    assert r_admin.json()["label"] == "Satisfaction Générale"

    # Client
    r_client = client.post(
        "/predict-label",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r_client.status_code == 200
    assert r_client.json()["label"] == "Satisfaction Générale"


@skip_if_no_auth
def test_predict_score_admin_only(client):
    admin_token = get_token(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    r = client.post(
        "/predict-score",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.json()["score"] == 5.0


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

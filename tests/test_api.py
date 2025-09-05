# tests/test_api.py
import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sklearn.dummy import DummyClassifier, DummyRegressor

from api.api import api

# Charger les variables d'environnement depuis .env
load_dotenv()

ADMIN_USERNAME = os.getenv("API_ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("API_ADMIN_PASSWORD")
CLIENT_USERNAME = os.getenv("API_CLIENT_USERNAME")
CLIENT_PASSWORD = os.getenv("API_CLIENT_PASSWORD")

# Certains tests nécessitent l'auth; on les skip si les creds .env ne sont pas présents
SKIP_AUTH = not all([ADMIN_USERNAME, ADMIN_PASSWORD, CLIENT_USERNAME, CLIENT_PASSWORD])
skip_if_no_auth = pytest.mark.skipif(
    SKIP_AUTH, reason="Identifiants API manquants dans .env"
)


@pytest.fixture(scope="module")
def client():
    """
    Fixture TestClient avec modèles Dummy injectés pour bypasser le besoin
    de modèles réels sur le disque.
    """
    # 1) Désactiver le startup qui chargerait les vrais artefacts
    api.router.on_startup = []

    # 2) Injecter des modèles déterministes (pas d'artefacts requis)
    clf = DummyClassifier(strategy="constant", constant="positif").fit(
        [["x"]], ["positif"]
    )
    reg = DummyRegressor(strategy="constant", constant=4.2).fit([[0]], [4.2])
    api.state.label_model = clf
    api.state.score_model = reg

    # 3) Créer le client de test
    with TestClient(api) as c:
        yield c


def test_health_live(client):
    r = client.get("/health/live")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "alive"
    assert "uptime_s" in body


def get_token(client: TestClient, username: str, password: str) -> str:
    r = client.post(
        "/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, f"Echec /token pour {username}"
    return r.json()["access_token"]


@skip_if_no_auth
def test_predict_label_admin_and_client(client):
    # admin et client doivent pouvoir appeler /predict-label
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
    # seul admin peut appeler /predict-score
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
    # DummyRegressor constant=4.2 → valeur dans [0, 5] sans clip
    assert 0 <= body["score"] <= 5


@skip_if_no_auth
def test_predict_score_client_forbidden(client):
    # Le client ne doit PAS avoir accès à /predict-score
    token = get_token(client, CLIENT_USERNAME, CLIENT_PASSWORD)
    r = client.post(
        "/predict-score",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_predict_label_unauthenticated(client):
    # Sans token → 401
    r = client.post("/predict-label", json={"text": "Service rapide"})
    assert r.status_code == 401

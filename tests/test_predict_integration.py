# tests/test_predict_integration.py
import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sklearn.dummy import DummyClassifier, DummyRegressor

from api.api import api

# Charger les identifiants depuis .env
load_dotenv()
ADMIN_USERNAME = os.getenv("API_ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("API_ADMIN_PASSWORD")
CLIENT_USERNAME = os.getenv("API_CLIENT_USERNAME")
CLIENT_PASSWORD = os.getenv("API_CLIENT_PASSWORD")

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
    # Empêcher le chargement des vrais artefacts au startup
    api.router.on_startup = []

    # Injecter des modèles déterministes (Dummy)
    clf = DummyClassifier(strategy="constant", constant="positif").fit(
        [["x"]], ["positif"]
    )
    reg = DummyRegressor(strategy="constant", constant=4.2).fit([[0]], [4.2])
    api.state.label_model = clf
    api.state.score_model = reg

    with TestClient(api) as c:
        yield c


def _get_token(client: TestClient, username: str, password: str) -> str:
    r = client.post(
        "/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert (
        r.status_code == 200
    ), f"Echec /token pour {username}: {r.status_code} {r.text}"
    return r.json()["access_token"]


@skip_if_no_auth
def test_predict_endpoints_with_dummy_models(client):
    # Récupérer JWT via /token
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
    assert r1.json()["label"] == "Livraison"

    # Admin → /predict-label OK
    r2 = client.post("/predict-label", json={"text": "okkk"}, headers=h_admin)
    assert r2.status_code == 200
    assert r2.json()["label"] == "Autre"

    # Admin → /predict-score OK
    r3 = client.post("/predict-score", json={"text": "Très déçu"}, headers=h_admin)
    assert r3.status_code == 200
    score = r3.json()["score"]
    assert isinstance(score, (int, float))
    assert 0 <= float(score) <= 5  # DummyRegressor constant=4.2

    # Client → /predict-score FORBIDDEN
    r4 = client.post("/predict-score", json={"text": "x"}, headers=h_client)
    assert r4.status_code == 403

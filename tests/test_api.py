import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from api.api import app
from sklearn.dummy import DummyClassifier, DummyRegressor

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "adminpass"
CLIENT_USERNAME = "client"
CLIENT_PASSWORD = "clientpass"


@pytest.fixture(autouse=True)
def mock_db_auth_and_models():
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

        # Inject dummy models
        app.state.label_model = DummyClassifier(
            strategy="constant", constant="Autre"
        ).fit([["x"]], ["Autre"])
        app.state.score_model = DummyRegressor(strategy="constant", constant=4.2).fit(
            [[0]], [4.2]
        )

        yield


@pytest.fixture
def client():
    return TestClient(app)


def get_token(client, username, password):
    r = client.post(
        "/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, f"Échec /token pour {username}"
    return r.json()["access_token"]


def test_predict_label_admin_and_client(client):
    admin_token = get_token(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    client_token = get_token(client, CLIENT_USERNAME, CLIENT_PASSWORD)

    r_admin = client.post(
        "/predict-label",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r_admin.status_code == 200
    assert r_admin.json()["label"] == "Autre"

    r_client = client.post(
        "/predict-label",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r_client.status_code == 200
    assert r_client.json()["label"] == "Autre"


def test_predict_score_admin_only(client):
    admin_token = get_token(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    r = client.post(
        "/predict-score",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.json()["score"] == 4.2


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

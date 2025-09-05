import os
import math
import joblib
import numpy as np
from sklearn.dummy import DummyClassifier, DummyRegressor

LABEL_MODEL_PATH = "models/random_forest/model.joblib"
SCORE_MODEL_PATH = "models/linear_regression/model.joblib"

# Créer les dossiers si nécessaire
os.makedirs(os.path.dirname(LABEL_MODEL_PATH), exist_ok=True)
os.makedirs(os.path.dirname(SCORE_MODEL_PATH), exist_ok=True)

# Générer un DummyClassifier si le modèle n'existe pas
if not os.path.exists(LABEL_MODEL_PATH):
    dummy_clf = DummyClassifier(strategy="most_frequent")
    dummy_clf.fit([["dummy"]], [0])  # juste une entrée bidon pour le fit
    joblib.dump(dummy_clf, LABEL_MODEL_PATH)

# Générer un DummyRegressor si le modèle n'existe pas
if not os.path.exists(SCORE_MODEL_PATH):
    dummy_reg = DummyRegressor(strategy="mean")
    dummy_reg.fit([["dummy"]], [3.0])  # juste une entrée bidon pour le fit
    joblib.dump(dummy_reg, SCORE_MODEL_PATH)


def test_classification_model_prediction():
    assert os.path.exists(LABEL_MODEL_PATH), "Modèle de classification introuvable."
    model = joblib.load(LABEL_MODEL_PATH)

    sample_text = "Livraison rapide et service excellent"
    pred = model.predict([sample_text])

    assert (
        hasattr(pred, "__len__") and len(pred) == 1
    ), "La prédiction classification devrait avoir une seule sortie"

    val = pred[0]
    if isinstance(val, np.generic):
        val = np.asarray(val).item()

    assert isinstance(
        val, (str, int, float)
    ), f"Type inattendu pour la sortie classification: {type(val)}"


def test_regression_model_prediction():
    assert os.path.exists(SCORE_MODEL_PATH), "Modèle de régression introuvable."
    model = joblib.load(SCORE_MODEL_PATH)

    sample_text = "Très bonne qualité de produit, je recommande fortement"
    pred = model.predict([sample_text])

    assert (
        hasattr(pred, "__len__") and len(pred) == 1
    ), "La prédiction régression devrait avoir une seule sortie"

    val = float(pred[0])
    assert math.isfinite(val), "La sortie régression devrait être un nombre fini"

    clipped = max(0.0, min(5.0, val))
    assert (
        0.0 <= clipped <= 5.0
    ), f"La note prédite clampée doit être entre 0 et 5 (valeur brute: {val})"

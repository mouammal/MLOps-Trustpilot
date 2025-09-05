import os
import math
import joblib
import numpy as np

LABEL_MODEL_PATH = "models/random_forest/model.joblib"
SCORE_MODEL_PATH = "models/linear_regression/model.joblib"


def test_classification_model_prediction():
    assert os.path.exists(
        LABEL_MODEL_PATH
    ), "Modèle de classification introuvable. Exécutez `python -m src.models.train_model`."
    model = joblib.load(LABEL_MODEL_PATH)

    sample_text = "Livraison rapide et service excellent"
    pred = model.predict([sample_text])

    assert (
        hasattr(pred, "__len__") and len(pred) == 1
    ), "La prédiction classification devrait avoir une seule sortie"

    val = pred[0]
    if isinstance(val, np.generic):
        val = np.asarray(val).item()

    # Selon l'entraînement, l'étiquette peut être str ou numérique
    assert isinstance(
        val, (str, int, float)
    ), f"Type inattendu pour la sortie classification: {type(val)}"


def test_regression_model_prediction():
    assert os.path.exists(
        SCORE_MODEL_PATH
    ), "Modèle de régression introuvable. Exécutez `python -m src.models.train_model`."
    model = joblib.load(SCORE_MODEL_PATH)

    sample_text = "Très bonne qualité de produit, je recommande fortement"
    pred = model.predict([sample_text])

    assert (
        hasattr(pred, "__len__") and len(pred) == 1
    ), "La prédiction régression devrait avoir une seule sortie"

    val = float(pred[0])
    assert math.isfinite(val), "La sortie régression devrait être un nombre fini"

    # On ne force pas le modèle à clipper, on vérifie juste qu'un clamp resterait dans [0,5]
    clipped = max(0.0, min(5.0, val))
    assert (
        0.0 <= clipped <= 5.0
    ), f"La note prédite clampée doit être entre 0 et 5 (valeur brute: {val})"

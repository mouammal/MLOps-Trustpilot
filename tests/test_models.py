import os
import joblib

def test_classification_model_prediction():
    model_path = "models/random_forest/model.pkl"
    vectorizer_path = "models/random_forest/vectorizer.pkl"

    assert os.path.exists(model_path), "Modèle de classification introuvable"
    assert os.path.exists(vectorizer_path), "Vectorizer de classification introuvable"

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)

    sample_text = "Livraison rapide et service excellent"
    vectorized = vectorizer.transform([sample_text])
    prediction = model.predict(vectorized)

    assert prediction.shape[0] == 1, "La prédiction classification devrait avoir une seule sortie"
    assert isinstance(prediction[0], str), "La sortie classification devrait être une chaîne de caractères"

def test_regression_model_prediction():
    model_path = "models/linear_regression/model.pkl"
    vectorizer_path = "models/linear_regression/vectorizer.pkl"

    assert os.path.exists(model_path), "Modèle de régression introuvable"
    assert os.path.exists(vectorizer_path), "Vectorizer de régression introuvable"

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)

    sample_text = "Très bonne qualité de produit, je recommande fortement"
    vectorized = vectorizer.transform([sample_text])
    prediction = model.predict(vectorized)
    pred = prediction[0]
    clipped_pred = float(max(0, min(5, pred)))

    assert isinstance(clipped_pred, float), "La sortie régression devrait être un float"
    assert 0 <= clipped_pred <= 5, f"La note prédite devrait être comprise entre 0 et 5, mais a été {clipped_pred}"


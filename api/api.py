# api/api.py

from fastapi import FastAPI
from api.schemas import TextInput, LabelPrediction, ScorePrediction
from api.utils import load_model_and_vectorizer

# Création de l'application FastAPI
api = FastAPI(title="API de prédiction d'avis clients")

# Chargement des modèles via la fonction utilitaire
label_model, label_vectorizer = load_model_and_vectorizer("random_forest")
score_model, score_vectorizer = load_model_and_vectorizer("linear_regression")

@api.get("/")
def home():
    return {"message": "Bienvenue sur l'API de prédiction Trustpilot !"}

@api.post("/predict-label", response_model=LabelPrediction)
def predict_label(data: TextInput):
    text_vectorized = label_vectorizer.transform([data.text])
    prediction = label_model.predict(text_vectorized)[0]
    return LabelPrediction(label=prediction)

@api.post("/predict-score", response_model=ScorePrediction)
def predict_score(data: TextInput):
    text_vectorized = score_vectorizer.transform([data.text])
    raw_score = score_model.predict(text_vectorized)[0]
    clipped_score = max(0, min(5, raw_score))
    return ScorePrediction(score=round(clipped_score, 2))

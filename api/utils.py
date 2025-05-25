# Fonctions de prédiction, chargement de modèles

import os
import joblib

def load_model_and_vectorizer(model_name: str):
    """
    Charge le modèle et le vectorizer correspondant à partir du dossier 'models'.
    
    Args:
        model_name (str): Nom du sous-dossier dans 'models' ('random_forest', 'linear_regression')
    
    Returns:
        Tuple: (model, vectorizer)
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, "..", "models", model_name)

    model = joblib.load(os.path.join(model_dir, "model.pkl"))
    vectorizer = joblib.load(os.path.join(model_dir, "vectorizer.pkl"))

    return model, vectorizer

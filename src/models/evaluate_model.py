import pandas as pd
import numpy as np
import joblib
import os
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    mean_absolute_error,
    mean_squared_error
)

# === Charger les données ===
data_path = "data/processed/processed_data.csv"
data = pd.read_csv(data_path)
X = data["clean_reviews"].fillna("")

# === CLASSIFICATION ===
print("== Évaluation du modèle de classification ==")
y_class = data["category"]
X_train_cls, X_test_cls, y_train_cls, y_test_cls = train_test_split(X, y_class, test_size=0.2, random_state=42)

# Charger modèle et vecteur
classifier = joblib.load("models/random_forest/model.pkl")
vectorizer_cls = joblib.load("models/random_forest/vectorizer.pkl")

X_test_vec_cls = vectorizer_cls.transform(X_test_cls)
y_pred_cls = classifier.predict(X_test_vec_cls)

# Évaluer
accuracy = accuracy_score(y_test_cls, y_pred_cls)
report = classification_report(y_test_cls, y_pred_cls, output_dict=True)

# Sauvegarder les métriques
metrics_class_path = "models/random_forest/metrics.json"
with open(metrics_class_path, "w") as f:
    json.dump({
        "accuracy": accuracy,
        "classification_report": report
    }, f, indent=4)

print(f"Classification accuracy: {accuracy:.2f}")
print(f"Rapport enregistré dans {metrics_class_path}")


# === RÉGRESSION ===
print("== Évaluation du modèle de régression ==")
y_reg = data["score_reviews"]
X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X, y_reg, test_size=0.2, random_state=42)

# Charger modèle et vecteur
regressor = joblib.load("models/linear_regression/model.pkl")
vectorizer_reg = joblib.load("models/linear_regression/vectorizer.pkl")

X_test_vec_reg = vectorizer_reg.transform(X_test_reg)
y_pred_reg = regressor.predict(X_test_vec_reg)
y_pred_clipped = np.clip(y_pred_reg, 0, 5)

# Évaluer
mae = round(mean_absolute_error(y_test_reg, y_pred_clipped),2)
mse = round(mean_squared_error(y_test_reg, y_pred_clipped),2)
rmse = round(np.sqrt(mean_squared_error(y_test_reg, y_pred_clipped)), 2)
# Sauvegarder les métriques
metrics_reg_path = "models/linear_regression/metrics.json"
with open(metrics_reg_path, "w") as f:
    json.dump({
        "MAE": mae,
        "MSE": mse,
        "RMSE": rmse
    }, f, indent=4)

print(f"Régression - MAE: {mae:.2f} | MSE: {mse:.2f}")
print(f"Rapport enregistré dans {metrics_reg_path}")

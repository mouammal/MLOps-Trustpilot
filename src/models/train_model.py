import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression

# 1. Charger les données
data_path = "data/processed/processed_data.csv"
data = pd.read_csv(data_path)

# Features
X_text = data["clean_reviews"].fillna("")

# === Classification ===
print("== Entraînement modèle de classification (catégories) ==")
y_class = data["category"]
X_train_class, X_test_class, y_train_class, y_test_class = train_test_split(X_text, y_class, test_size=0.2, random_state=42)

vectorizer_class = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)
X_train_vec_class = vectorizer_class.fit_transform(X_train_class)
X_test_vec_class = vectorizer_class.transform(X_test_class)

classifier = RandomForestClassifier(n_estimators=100, random_state=42)
classifier.fit(X_train_vec_class, y_train_class)

# Sauvegarde
joblib.dump(classifier, "models/random_forest/model.pkl")
joblib.dump(vectorizer_class, "models/random_forest/vectorizer.pkl")

print("Modèle de classification entraîné et sauvegardé.")


# === Régression ===
print("== Entraînement modèle de régression (score) ==")
y_reg = data["score_reviews"]
X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X_text, y_reg, test_size=0.2, random_state=42)

vectorizer_reg = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)
X_train_vec_reg = vectorizer_reg.fit_transform(X_train_reg)
X_test_vec_reg = vectorizer_reg.transform(X_test_reg)

regressor = LinearRegression()
regressor.fit(X_train_vec_reg, y_train_reg)

# Prédictions
y_pred = regressor.predict(X_test_vec_reg)

# CLIPPING des prédictions entre 0 et 5
y_pred_clipped = np.clip(y_pred, 0, 5)

# Sauvegarde
joblib.dump(regressor, "models/linear_regression/model.pkl")
joblib.dump(vectorizer_reg, "models/linear_regression/vectorizer.pkl")

print("Modèle de régression entraîné et sauvegardé.")

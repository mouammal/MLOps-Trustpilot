from __future__ import annotations
from pathlib import Path
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, root_mean_squared_error, r2_score
from src.models.pipelines import build_label_pipeline, build_score_pipeline

# Colonnes utiles du CSV
TEXT_COL   = "clean_reviews"   # texte d'entrée
LABEL_COL  = "category"        # classe 
SCORE_COL  = "score_reviews"   # score numérique

DATA = Path("data/processed/processed_data.csv")
LABEL_OUT = Path("models/random_forest")
SCORE_OUT = Path("models/linear_regression")
LABEL_OUT.mkdir(parents=True, exist_ok=True)
SCORE_OUT.mkdir(parents=True, exist_ok=True)

def main():
    df = pd.read_csv(DATA)
    for c in [TEXT_COL, LABEL_COL, SCORE_COL]:
        assert c in df.columns, f"Colonne manquante: {c}"

    X = df[TEXT_COL].fillna("")
    X = df[TEXT_COL].astype(str).tolist()

    ###################
    # ----- LABEL -----
    ###################
    y_label = df[LABEL_COL]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y_label, test_size=0.2, random_state=42, stratify=y_label)
    label_pipe = build_label_pipeline().fit(X_tr, y_tr)
    y_pred = label_pipe.predict(X_te)
    metrics_label = {
        "accuracy": float(accuracy_score(y_te, y_pred)),
        "f1_weighted": float(f1_score(y_te, y_pred, average="weighted")),
        "n_train": int(len(X_tr)), "n_test": int(len(X_te)),
    }
    joblib.dump(label_pipe, LABEL_OUT / "model.joblib", compress=("xz", 3))
    (LABEL_OUT / "metrics.json").write_text(json.dumps(metrics_label, indent=2))

    ###################
    # ----- SCORE -----
    ###################
    y_score = df[SCORE_COL].astype(float)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y_score, test_size=0.2, random_state=42)
    score_pipe = build_score_pipeline().fit(X_tr, y_tr)
    y_hat = score_pipe.predict(X_te)
    y_hat = np.clip(y_hat, 0, 5)

    metrics_score = {
        "mae": float(mean_absolute_error(y_te, y_hat)),
        "rmse": float(root_mean_squared_error(y_te, y_hat)),
        "r2": float(r2_score(y_te, y_hat)),
        "n_train": int(len(X_tr)), "n_test": int(len(X_te)),
    }
    joblib.dump(score_pipe, SCORE_OUT / "model.joblib", compress=("xz", 3))
    (SCORE_OUT / "metrics.json").write_text(json.dumps(metrics_score, indent=2))

    print("Saved:", LABEL_OUT / "model.joblib", "|", SCORE_OUT / "model.joblib")

if __name__ == "__main__":
    main()

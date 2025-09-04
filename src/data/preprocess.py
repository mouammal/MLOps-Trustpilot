# src/data/preprocess.py
from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
from ..utils.helpers import clean_text, assign_label


def preprocess(in_csv: str, out_csv: str) -> None:
    """Nettoie les avis et génère un CSV prétraité."""
    in_path = Path(in_csv)
    out_path = Path(out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[preprocess] Lecture: {in_path}")
    df = pd.read_csv(in_path, sep=",", on_bad_lines="skip")

    # -- Colonnes à supprimer si présentes
    cols_to_drop = ["location", "Id_reviews", "published_date"]
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True, errors="ignore")

    # -- Fusion title_reviews -> reviews (si dispo)
    if "reviews" not in df.columns:
        raise KeyError("Colonne 'reviews' absente du fichier d'entrée.")
    if "title_reviews" in df.columns:
        df["reviews"] = df["reviews"].fillna(df["title_reviews"])

    # -- Garder que les lignes avec un texte d'avis
    df.dropna(subset=["reviews"], inplace=True)

    # -- Nettoyage texte
    print("[preprocess] Nettoyage du texte…")
    df["clean_reviews"] = df["reviews"].astype(str).apply(clean_text)
    df.dropna(subset=["clean_reviews"], inplace=True)
    df = df[df["clean_reviews"].str.strip() != ""]

    # -- Attribution de catégories
    print("[preprocess] Attribution des catégories…")
    df["category"] = df["clean_reviews"].apply(assign_label)

    # -- Note: optionnel, si tu veux garder uniquement les lignes avec score
    if "score_reviews" in df.columns:
        df.dropna(subset=["score_reviews"], inplace=True)

    print(f"[preprocess] Écriture: {out_path}")
    df.to_csv(out_path, index=False)
    print("[preprocess] Terminé.")


def main() -> None:
    # Chemins configurables via variables d'env (Docker Compose)
    raw_csv = os.getenv("RAW_CSV", "data/raw/raw_data.csv")
    proc_csv = os.getenv("PROC_CSV", "data/processed/processed_data.csv")
    preprocess(raw_csv, proc_csv)


if __name__ == "__main__":
    main()

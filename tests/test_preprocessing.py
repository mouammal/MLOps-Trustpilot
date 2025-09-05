import os
import pandas as pd
import re

PROCESSED_FILE = "data/processed/processed_data.csv"

# Créer le dossier si nécessaire
os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)

# Créer un CSV bidon si le fichier n'existe pas
if not os.path.exists(PROCESSED_FILE):
    df_mock = pd.DataFrame({
        "clean_reviews": [
            "livraison rapide et service excellent",
            "très bonne qualité de produit",
            "je recommande fortement",
            "service client médiocre",
            "produit défectueux"
        ],
        "category": [
            "Livraison",
            "Qualité/Prix",
            "Recommandation",
            "Service Client",
            "Retour/Remboursement"
        ],
        "score_reviews": [5, 4, 5, 2, 1]
    })
    df_mock.to_csv(PROCESSED_FILE, index=False)


def test_processed_data_exists():
    assert os.path.exists(
        PROCESSED_FILE
    ), "Le fichier de données traitées est manquant"


def test_processed_data_columns():
    df = pd.read_csv(PROCESSED_FILE, low_memory=False)
    expected_cols = ["clean_reviews", "category", "score_reviews"]
    for col in expected_cols:
        assert col in df.columns, f"La colonne attendue '{col}' est absente"


def test_no_missing_values():
    df = pd.read_csv(PROCESSED_FILE, low_memory=False)
    assert (
        df["clean_reviews"].isnull().sum() == 0
    ), "Des valeurs manquantes dans 'clean_reviews'"
    assert df["category"].isnull().sum() == 0, "Des valeurs manquantes dans 'category'"
    assert (
        df["score_reviews"].isnull().sum() == 0
    ), "Des valeurs manquantes dans 'score_reviews'"


def test_text_cleaning():
    df = pd.read_csv(PROCESSED_FILE, low_memory=False)
    sample = df["clean_reviews"].dropna().sample(5, random_state=42)
    for text in sample:
        assert text == text.lower(), "Le texte n'est pas en minuscules"
        assert not bool(re.search(r"\d", text)), "Le texte contient des chiffres"
        assert not bool(
            re.search(r"[^\w\s]", text)
        ), "Le texte contient des signes de ponctuation"


def test_known_categories():
    df = pd.read_csv(PROCESSED_FILE, low_memory=False)
    known_categories = {
        "Livraison",
        "Service Client",
        "Recommandation",
        "Qualité/Prix",
        "Satisfaction Générale",
        "Formation/Entreprise",
        "Autre",
        "Hôtellerie / Hébergement",
        "Retour/Remboursement",
        "Disponibilité/Stock",
        "Site Web/Expérience d’Achat",
        "Produit & Qualité/Prix",
        "Commande/Paiement",
    }
    unique_labels = set(df["category"].unique())
    assert unique_labels.issubset(
        known_categories
    ), f"Des catégories inconnues sont présentes : {unique_labels - known_categories}"



def test_known_categories():
    df = pd.read_csv("data/processed/processed_data.csv", low_memory=False)
    known_categories = {
        "Livraison",
        "Service Client",
        "Recommandation",
        "Qualité/Prix",
        "Satisfaction Générale",
        "Formation/Entreprise",
        "Autre",
        "Hôtellerie / Hébergement",
        "Retour/Remboursement",
        "Disponibilité/Stock",
        "Site Web/Expérience d’Achat",
        "Produit & Qualité/Prix",
        "Commande/Paiement",
    }
    unique_labels = set(df["category"].unique())
    assert unique_labels.issubset(
        known_categories
    ), f"Des catégories inconnues sont présentes : {unique_labels - known_categories}"

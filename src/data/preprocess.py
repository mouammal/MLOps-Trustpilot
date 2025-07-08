import pandas as pd
import nltk
from src.utils.helpers import clean_text, assign_label

# Télécharger les stopwords
nltk.download('stopwords')

# === Étape 1 : Chargement des données brutes ===
raw_path = "data/raw/raw_data.csv"
processed_path = "data/processed/processed_data.csv"

print("Chargement des données...")
df = pd.read_csv(raw_path, sep=',', on_bad_lines='skip')

# === Étape 2 : Nettoyage des colonnes ===
df.drop(columns=["location", "Id_reviews", "published_date"], inplace=True, errors='ignore')

# Fusion des colonnes 'reviews' et 'title_reviews'
df['reviews'] = df['reviews'].fillna(df['title_reviews'])
df.dropna(subset=['reviews'], inplace=True)

# === Étape 3 : Nettoyage du texte ===
print("Nettoyage du texte...")
df['clean_reviews'] = df['reviews'].astype(str).apply(clean_text)

df.dropna(subset=['clean_reviews'], inplace=True)
df = df[df['clean_reviews'].str.strip() != ""]  # Supprime les chaînes vides

# === Étape 4 : Attribution de labels thématiques ===
print("Attribution des catégories...")
df['category'] = df['clean_reviews'].apply(assign_label)

if 'score_reviews' in df.columns:
    df.dropna(subset=['score_reviews'], inplace=True)

# === Étape 5 : Sauvegarde du fichier nettoyé ===
print(f"Enregistrement des données prétraitées dans {processed_path}")
df.to_csv(processed_path, index=False)
print("Prétraitement terminé.")

# Fonctions utilitaires (logs, config, etc.)

import re
from config import CUSTOM_STOPWORDS, CATEGORIES


def clean_text(text: str) -> str:
    """
    Nettoie un texte en supprimant :
    - Les majuscules
    - Les chiffres
    - La ponctuation
    - Les stopwords définis dans le projet
    """
    text = text.lower()
    text = re.sub(r"\d+", " ", text)  # Supprimer les chiffres
    text = re.sub(r"[^\w\s]", " ", text)  # Supprimer la ponctuation
    text = " ".join(word for word in text.split() if word not in CUSTOM_STOPWORDS)
    return text


def handle_negations(text: str) -> str:
    """
    Gère les cas de négation en fusionnant avec le mot suivant.
    Ex : "pas bon" -> "pas_bon"
    """
    text = re.sub(r"\b(pas|ne|n'|jamais|rien|aucun|ni|sans)\s+(\w+)", r"\1_\2", text)
    return text


def apply_negations(texts):
    """Applique handle_negations à une liste de textes"""
    return [handle_negations(t) for t in texts]


def assign_label(review: str) -> str:
    """
    Attribue une catégorie à un avis client en fonction de mots-clés définis.
    """
    review = review.lower()
    for category, keywords in CATEGORIES.items():
        if any(keyword in review for keyword in keywords):
            return category
    return "Autre"

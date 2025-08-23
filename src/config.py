# Paramètres globaux (chemins, hyperparams)
from nltk.corpus import stopwords
from typing import Set

try:
    from nltk.corpus import stopwords as nltk_stopwords
    FR_STOPWORDS: Set[str] = set(nltk_stopwords.words('french'))
except Exception:
    # fallback minimal si NLTK indisponible
    FR_STOPWORDS = {
        "et","ou","de","la","le","les","des","du","un","une","au","aux","en","dans","pour","par","avec","sans",
        "sur","ce","cet","cette","ces","à","a","est","sont","été","être","avoir","plus","moins","très","trop"
    }

FR_STOPWORDS = {w.lower() for w in FR_STOPWORDS}

# Stopwords français de base + custom
CUSTOM_STOPWORDS = FR_STOPWORDS | {'très', 'Très', 'tres', 'Bien', 'bien', 'Bonne', 'bonne', 'Bon', 'bon'}
CUSTOM_STOPWORDS = sorted(CUSTOM_STOPWORDS)

# Les catégories et leurs expressions associées
CATEGORIES = {
        "Livraison": ["colis","livraison","livraison rapide", "envoi rapide","délai livraison","prise charge"],
        "Service Client": ["service","service client", "prise charge", "bons conseils", "service après vente","après vente"
                        ,"service après","site internet"],
        "Recommandation": ["recommande vivement", "yeux fermés", "recommande fortement", "recommande sans", "recommande"
                        "sans hésiter","recommande cette"],
        "Qualité/Prix": ["qualité","prix", "qualité prix", "rapport qualité prix", "produits qualité","produit conforme","qualité produits"
                        ,"grande qualité", "produit"],
        "Satisfaction Générale": ["Excellent","rien dire", "rien redire", "tout parfait", "merci beaucoup","grand merci","merci encore"
                                ,"chaque fois","sans problème","commande passée","expérience"],
        "Formation/Entreprise": ["formation","entreprise","cette formation", "cette entreprise"]
    }


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
'''
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
'''

CATEGORIES = {
    "Livraison": [
        "colis","livraison","livraison rapide","envoi rapide","expédition",
        "délai livraison","transporteur","chronopost","colissimo","dpd",
        "acheminement","reçu rapidement","retard livraison","livraison express","suivi colis"
    ],

    "Service Client": [
        "service","service client","prise en charge","bons conseils","service après vente",
        "support","hotline","assistance","réactif","réponse rapide",
        "à l'écoute","accueil","professionnalisme","amabilité","communication"
    ],

    "Satisfaction Générale": [
        "excellent","rien dire","rien redire","tout parfait","merci beaucoup",
        "grand merci","merci encore","très satisfait","super","parfait",
        "génial","impeccable","ravie","formidable","aucun souci"
    ],

    "Produit & Qualité/Prix": [
        "produit","article","qualité","prix","rapport qualité prix",
        "produit conforme","qualité produits","grande qualité","excellent rapport",
        "prix correct","prix abordable","bon état","description conforme","solide","fragile"
    ],

    "Commande/Paiement": [
        "commande","paiement","facture","erreur commande","modification commande",
        "validation","site sécurisé","transaction","carte bancaire","moyen paiement",
        "problème commande","commande annulée","paiement validé","historique commande","refus paiement"
    ],

    "Retour/Remboursement": [
        "retour","remboursement","remboursé","échange","retourné",
        "sav remboursement","politique retour","retour gratuit","remboursement rapide",
        "remboursement intégral","demande retour","échange produit","remboursement accepté","remboursement refusé","satisfait ou remboursé"
    ],

    "Disponibilité/Stock": [
        "disponible","stock","rupture","réapprovisionnement","produit manquant",
        "pas en stock","indisponible","article épuisé","réassort","stock limité",
        "plus en stock","manque produit","produit disponible","rupture prolongée","attente stock"
    ],

    "Site Web/Expérience d’Achat": [
        "site","navigation","interface","bug","facile d'utilisation",
        "ergonomique","commande en ligne","site lent","site rapide","utilisation simple",
        "interface claire","application","connexion","site pratique","problème technique"
    ],

    "Formation/Entreprise": [
        "formation","entreprise","cette formation","cette entreprise","formateur",
        "pédagogie","session","apprentissage","cours","stage",
        "société","organisme","programme","atelier","séminaire"
    ],

    "Hôtellerie / Hébergement": [
        "hôtel","chambre","lit","hébergement","séjour",
        "réception","concierge","suite","nuitée","confort",
        "propreté","service hôtelier","check-in","check-out","petit déjeuner"
    ]
}
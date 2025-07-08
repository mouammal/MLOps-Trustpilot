# Paramètres globaux (chemins, hyperparams)
from nltk.corpus import stopwords

# Stopwords français de base + custom
CUSTOM_STOPWORDS = list(set(
    stopwords.words('french') +
    ['très', 'Très', 'tres', 'Bien', 'bien', 'Bonne', 'bonne', 'Bon', 'bon']
))

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


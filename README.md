<pre><code>'''
trustpilot-mlops/
├── data/
│   ├── raw/                         # Données brutes (scrapées)
│   │   └── raw_data.csv
│   ├── processed/                   # Données nettoyées, prêtes à l'entraînement
│   │   └── processed_data.csv
│
├── notebooks/                      # Notebooks exploratoires (EDA, tests initiaux)
│   └── eda_trustpilot.ipynb
│
├── src/                            # Code source (modules Python)
│   ├── data/                       # Scripts de traitement et de préparation des données
│   │   └── preprocess.py
│   ├── features/                   # Vectorisation, encodage
│   │   └── vectorizer.py
│   ├── models/                     # Entraînement, évaluation, chargement des modèles
│   │   ├── train_model.py
│   │   └── evaluate_model.py
│   ├── utils/                      # Fonctions utilitaires (logs, config, etc.)
│   │   └── helpers.py
│   └── config.py                   # Paramètres globaux (chemins, hyperparams)
│
├── models/                         # Modèles sauvegardés (versionnés avec DVC/MLflow)
│   ├── random_forest/
│   │   ├── model.pkl
│   │   ├── vectorizer.pkl
│   │   └── metrics.json
│   └── linear_regression/
│       ├── model.pkl
│       ├── vectorizer.pkl
│       └── metrics.json
│
├── api/                            # API FastAPI
│   ├── api.py
│   ├── schemas.py
│   └── utils.py                    # Fonctions de prédiction & chargement modèle
|   └── security/                   # Dossier pour la gestion de la sécurité
│      ├── auth.py                  # Authentification (token JWT, OAuth2, etc.)
│      ├── permissions.py           # Rôles, scopes, accès restreint
│      └── config.py                # Clés secrètes, durée des tokens, etc.
│
├── tests/                          # Tests automatisés
│   ├── test_api.py
│   ├── test_preprocessing.py
│   └── test_models.py
│
├── pipelines/                      # Pipelines (DVC & scripts orchestrés)
│   ├── data_pipeline.py
│   └── train_pipeline.py
│
├── Dockerfile                      # Conteneurisation
├── docker-compose.yml              # Orchestrateur
├── requirements.txt                # Dépendances
├── setup.sh                        # Script d'installation/env automatique
├── dvc.yaml                        # Pipelines versionnés DVC
├── .gitignore
├── README.md                       # Documentation du projet
'''</code></pre>
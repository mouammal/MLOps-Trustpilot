<pre><code> 
MLOps-Trustpilot/
├── airflow/                                        # Orchestration de pipelines (Airflow)
│   ├── dags/                                       # DAGs (pipelines) Airflow
│   │   ├── scrape_process_train_save_dag.py        # Scraping + preprocessing + entraînement + sauvegarde modèle
│   │   ├── scraping_and_preprocessing_dag_test.py  # Test DAG scraping + preprocessing
│   │   └── train_save_dag_test.py                  # Test DAG entraînement + sauvegarde
│   ├── airflow.sh                                  # Script de lancement Airflow
│   └── requirements.txt                            # Dépendances spécifiques Airflow
│
├── api/                                            # API FastAPI
│   └── security/                                   # Gestion sécurité et utilisateurs
│       ├── __init__.py
│       ├── auth.py                                 # Authentification (JWT, OAuth2…)
│       ├── db_users.py                             # Gestion des utilisateurs stockés (DB / mémoire)
│       ├── permissions.py                          # Vérification des rôles & droits d’accès
│       └── users.py                                # Modèles et services liés aux utilisateurs
│   ├── __init__.py
│   ├── api.py                                      # Définition des endpoints (predict, health, docs…)
│   └── schemas.py                                  # Schémas Pydantic (validation des données I/O)
│
├── data/                                           # Données versionnées avec DVC
│   ├── processed/                                  # Données traitées (pour entraînement)
│   │   └── processed_data.csv
│   └── raw/                                        # Données brutes (scraping Trustpilot)
│       ├── companies_links.csv.dvc
│       ├── raw_data.csv.dvc
│       ├── scrape_state.json                       # État du scraping (checkpoint)
│       ├── trustpilot_data.csv.dvc
│       ├── trustpilot_data_raw_2025-08-12.csv.dvc
│       ├── trustpilot_data_raw_2025-09-05__061005.csv.dvc
│       └── trustpilot_data_raw_2025-09-05__083004.csv.dvc
│
├── db/                                             # Base de données
│   └── users.sql                                   # Script SQL pour table utilisateurs
│
├── models/                                         # Modèles entraînés (joblib) versionnés par DVC
│   ├── linear_regression/
│   │   └── model.joblib
│   ├── random_forest/
│   │   └── model.joblib
│   └── __init__.py
│
├── prometheus/                                     # Monitoring (Prometheus)
│   └── prometheus.yml                              # Config Prometheus (scraping API, metrics)
│
├── src/                                            # Code source (librairie interne)
│   ├── data/                                       # Préparation et scraping des données
│   │   ├── __init__.py
│   │   ├── preprocess.py                           # Nettoyage, encodage, features engineering
│   │   └── scraping.py                             # Scraping Trustpilot (collecte des avis)
│   ├── models/                                     # Entraînement et pipeline ML
│   │   ├── __init__.py
│   │   ├── pipelines.py                            # Pipelines ML (prétraitement + modèle)
│   │   └── train_model.py                          # Script d’entraînement
│   └── utils/                                      # Outils & fonctions génériques
│       ├── __init__.py
│       ├── helpers.py                              # Fonctions utilitaires diverses
│       └── logging.py                              # Configuration logging centralisé
│   ├── __init__.py
│   └── config.py                                   # Paramètres globaux (chemins, hyperparams…)
│
├── tests/                                          # Tests unitaires & d’intégration
│   ├── __init__.py
│   ├── test_api.py                                 # Tests API FastAPI
│   ├── test_health.py                              # Tests endpoints health
│   ├── test_models.py                              # Tests entraînement et chargement modèles
│   ├── test_predict_integration.py                 # Tests intégrés (requête → prédiction)
│   ├── test_preprocessing.py                       # Tests data preprocessing
│   └── test_scraping.py                            # Tests scraping Trustpilot
│
├── Dockerfile                                      # Image principale (API + services)
├── Dockerfile.airflow                              # Image spécifique pour Airflow
├── README.md                                       # Documentation du projet
├── docker-compose.yml                              # Orchestration multi-services (API, DB, Airflow, Prometheus…)
├── dvc.lock                                        # Fichier de verrouillage DVC 
├── dvc.yaml                                        # Définition des pipelines DVC (scraping, preprocessing, training…)
├── requirements.txt                                # Dépendances principales du projet
├── servers.json                                    # Configuration des serveurs (API / workers)
└── setup.sh                                        # Script d’installation/env automatique
</code></pre>

### 1. Cloner le projet 
``` 
cd ~
git clone <URL_DU_REPO>
cd MLOps-Trustpilot
```

### 2. Créer un environnement virtuel (PYTHON 3.11 ONLY)
```
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances Python locales
```
pip install --upgrade pip
pip install -r requirements.txt
```  
  
### 4. DVC : Récuperer les data dagshub
```
- https://dagshub.com/mouammal.ziadah/MLOps-Trustpilot
- remote > data > DVC :  
    - dvc remote modify origin --local access_key_id  TOKEN
    - dvc remote modify origin --local secret_access_key TOKEN
- DVC pull
``` 

### 5. Construire les images Docker

Cette commande va créer les images pour :  
- mlops_trustpilot_api (API FastAPI)    
- airflow + airflow_postgres  
```
docker compose build 
```

### 6. Lancer les services avec Docker Compose :  
- API FastAPI : http://localhost:8000   
- Airflow Web UI : http://localhost:8080  
- Airflow Postgres : port 5432  
- pgAdmin : http://localhost:5050
- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000  
```
docker compose up --build -d
```

### 7. Utiliser l’API (exemple prediction label)
Il faut se connecter d'abord via "Authorize" ou obtenir un "Access Token" via le endpoint /token  
```   
curl -X POST "http://localhost:8000/predict-label" 
-H "accept: application/json" 
-H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" 
-H "Content-Type: application/json" 
-d '{
        "text": "La livraison a été rapide et le produit est conforme, très satisfait !"
    }'
```
sur Powershell Windows : 
```   
Invoke-RestMethod -Uri "http://localhost:8000/predict-label" `
-Method POST `
-Headers @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer YOUR_ACCESS_TOKEN_HERE"
} `
-Body '{ "text": "la livraison est rapide et efficace" }'
```

### 8. Utiliser Airflow  
- Se connecter à l’UI : http://localhost:8080
- Username / Password par défaut : airflow / airflow  
- DAGs disponible :  
    - scrape_process_train_save : Scraping → concat → preprocessing → training → save 
    - dags de test
- Exécution manuelle d’un DAG :
    Aller sur Airflow UI → DAG → Trigger DAG
- Exécution automatique du DAG :
    - scrping pendant 3 jrs, puis training des modèles ML le 4e jour, puis saving.  
  
### 9. Accès aux données et modèles  
- Données raw : ./data/raw/
- Données processed : ./data/processed/
- Modèles ML :
    - Random Forest : ./models/random_forest/model.joblib  
    - Linear Regression : ./models/linear_regression/model.joblib

### 10. Nettoyer l’environnement (arret des conteneurs) 
``` 
docker compose down 
```
 
### 11. Docker Compose Services
- API + Jobs
    - api : API FastAPI
    - preprocess : job preprocessing
    - train : job training

- Airflow
    - airflow_postgres : base Airflow
    - airflow : scheduler + webserver

- Postgres + pgAdmin
    - trustpilot_postgres : base utilisateurs
    - pgadmin : interface web pour les DB

- Monitoring
    - prometheus : collecte métriques
    - grafana : dashboard métriques + Postgres

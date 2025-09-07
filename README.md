<pre><code>'''
trustpilot-mlops/
├── airflow/
│   ├── dags/                         
│   │   └── scrape_process_train_save_dag.py           # DAGs Airflow
│   │   └── scraping_and_preprocessing_dag_test.py     # DAGs Airflow    
│   │   └── train_save_dag_test.py                     # DAGs Airflow
│   ├── logs/                  
│   └── plugings/  
│ 
├── data/
│   ├── raw/                         # Données brutes (scrapées)
│   │   └── raw_data.csv
│   ├── processed/                   # Données nettoyées, prêtes à l'entraînement
│   │   └── processed_data.csv
│
├── src/                            # Code source (modules Python)
│   ├── data/                       # Scripts de traitement et de préparation des données
│   │   └── preprocess.py
│   ├── models/                     # Entraînement, évaluation, chargement des modèles
│   │   ├── train_model.py
│   │   └── evaluate_model.py
│   ├── utils/                      # Fonctions utilitaires (logs, config, etc.)
│   │   └── helpers.py
│   └── config.py                   # Paramètres globaux (chemins, hyperparams)
│
├── models/                         # Modèles sauvegardés (versionnés avec DVC/MLflow)
│   ├── random_forest/
│   │   ├── model.joblib
│   │   └── metrics.json
│   └── linear_regression/
│       ├── model.joblib
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
├── Dockerfile.airflow
├── .env
├── requirements.txt                # Dépendances
├── setup.sh                        # Script d'installation/env automatique
├── dvc.yaml                        # Pipelines versionnés DVC
├── .gitignore
├── README.md                       # Documentation du projet
'''</code></pre>

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

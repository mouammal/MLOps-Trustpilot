#!/bin/bash
airflow db init

# Crée un utilisateur admin par défaut
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com

# Lancer scheduler en arrière-plan et webserver en avant-plan
airflow scheduler &
exec airflow webserver
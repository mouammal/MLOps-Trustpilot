import sys
import os
#from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from models.train_model import main as train_main 

# Ensure src is in Python path
SRC_PATH = "/opt/airflow/src"
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# --- Config ---
PROCESSED_FOLDER = "/opt/airflow/data/processed"
PROCESSED_FILE = os.path.join(PROCESSED_FOLDER, "processed_data.csv")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'train_model',
    default_args=default_args,
    description='Train ML models only when processed_data.csv exists',
    schedule_interval=None,  # manual trigger or external trigger
    start_date=datetime(2025, 9, 1),
    catchup=False,
)

def train_model_if_ready(**kwargs):
    # Check if processed CSV exists
    if not os.path.exists(PROCESSED_FILE):
        print(f"{PROCESSED_FILE} does not exist, skipping training.")
        return

    # Call train_model.main()
    print(f"{PROCESSED_FILE} found, starting training...")
    
    # Change working directory to /opt/airflow so que paths relatifs dans train_model.py pointent sur le volume monté
    current_dir = os.getcwd()
    os.chdir("/opt/airflow")
    try:
        train_main()
    finally:
        os.chdir(current_dir)

    print("Training complete!")

# --- Airflow task ---
train_task = PythonOperator(
    task_id='train_model_task',
    python_callable=train_model_if_ready,
    provide_context=True,
    dag=dag,
)


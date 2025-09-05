import json
import os
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator 
from datetime import datetime, timedelta
import pandas as pd

from data.scraping import run_scraping_pipeline
from data.preprocess import preprocess

# Ensure src is in Python path
SRC_PATH = "/opt/airflow/src"
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


# --- Config ---
INPUT_FOLDER = "/opt/airflow/data/raw"
STATE_FILE = os.path.join(INPUT_FOLDER, "scrape_state.json")
OUTPUT_FILE = os.path.join(INPUT_FOLDER, "concatenated_data.csv")

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
    'scraping_and_preprocessing',
    default_args=default_args,
    description='Scrape daily and concatenate after 3 runs and process',
    schedule_interval='0 0 */2 * *',  # daily for testing, adjust as needed
    start_date=datetime(2025, 9, 1),
    catchup=False,
)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    else:
        return {"counter": 0, "files": []}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


# --- Task 1: Scraping ---
def scrape_one_day(**kwargs):
    state = load_state()
    df_companies = pd.read_csv(os.path.join(INPUT_FOLDER,"companies_links.csv"))

    _, raw_filename, total_reviews, error_rate = run_scraping_pipeline(df_companies)

    # Add timestamp to filename
    timestamp = datetime.now().strftime("_%H%M%S")
    new_filename = os.path.basename(raw_filename).replace(".csv", f"_{timestamp}.csv")
    new_path = os.path.join(INPUT_FOLDER, new_filename)
    os.rename(raw_filename, new_path)

    # Update persistent state
    state["counter"] += 1
    state["files"].append(new_filename)
    save_state(state)

    print(f"Scrape run #{state['counter']} done. File: {new_filename}, total reviews: {total_reviews}, error rate: {error_rate:.2%}")


# --- Task 2: Concaténation ---
def concatenate_files(**kwargs):
    state = load_state()
    print(f"Current scrape counter: {state['counter']}")

    if state["counter"] < 3:
        print("Not enough scrapes yet, skipping concatenation")
        return

    filenames = state["files"]

    # If no files in state (manual test), scan folder
    if not filenames:
        filenames = [f for f in os.listdir(INPUT_FOLDER) if f.startswith("trustpilot_data_raw_")]

    all_data = []
    for file in filenames:
        file_path = os.path.join(INPUT_FOLDER, file)
        if os.path.isfile(file_path):
            df = pd.read_csv(file_path)
            all_data.append(df)

    if all_data:
        concatenated_df = pd.concat(all_data, ignore_index=True).drop_duplicates()
        concatenated_df.to_csv(OUTPUT_FILE, index=False)
        print(f"Concatenated data saved to {OUTPUT_FILE} with {len(concatenated_df)} rows.")

        # --- Reset state ---
        save_state({"counter": 0, "files": []})
        print("scrape_state.json has been reset for next cycle.")
    else:
        print("No files to concatenate.")


# --- Task 3: Preprocessing ---
def preprocess_data(**kwargs):
    if not os.path.exists(OUTPUT_FILE):
        print(f"No concatenated file found at {OUTPUT_FILE}, skipping preprocessing")
        return

    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    preprocess(OUTPUT_FILE, PROCESSED_FILE)
    print(f"Preprocessing complete. File saved at {PROCESSED_FILE}")


# --- Airflow tasks ---
scrape_task = PythonOperator(
    task_id='scrape_one_day',
    python_callable=scrape_one_day,
    provide_context=True,
    dag=dag,
)

concat_task = PythonOperator(
    task_id='concatenate_files',
    python_callable=concatenate_files,
    provide_context=True,
    dag=dag,
)

preprocess_task = PythonOperator(
    task_id='preprocess_data',
    python_callable=preprocess_data,
    provide_context=True,
    dag=dag,
)

# --- Dependencies ---
scrape_task >> concat_task >> preprocess_task
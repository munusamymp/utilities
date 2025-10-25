from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import boto3
import pandas as pd
import io

# ---- Configuration ----
SOURCE_BUCKET = "data-bucket"
SOURCE_KEY = "input/data.csv"
DEST_BUCKET = "etl-bucket"
DEST_KEY = "output/cleaned_data.csv"
AWS_REGION = "us-east-1"

# ---- Define ETL Functions ----
def extract_from_s3(**kwargs):
    """Extract CSV file from S3"""
    s3 = boto3.client("s3", region_name=AWS_REGION)
    response = s3.get_object(Bucket=SOURCE_BUCKET, Key=SOURCE_KEY)
    df = pd.read_csv(response["Body"])
    kwargs["ti"].xcom_push(key="raw_data", value=df.to_json())

def transform_data(**kwargs):
    """Transform the extracted data"""
    ti = kwargs["ti"]
    df_json = ti.xcom_pull(task_ids="extract", key="raw_data")
    df = pd.read_json(df_json)

    # Example transformation: filter + rename columns
    df = df[df["status"] == "active"]
    df = df.rename(columns={"name": "customer_name", "amount": "purchase_amount"})

    # Push transformed data
    ti.xcom_push(key="transformed_data", value=df.to_json())

def load_to_s3(**kwargs):
    """Load the transformed data back into S3"""
    ti = kwargs["ti"]
    df_json = ti.xcom_pull(task_ids="transform", key="transformed_data")
    df = pd.read_json(df_json)

    # Save CSV to memory and upload
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    s3 = boto3.client("s3", region_name=AWS_REGION)
    s3.put_object(Bucket=DEST_BUCKET, Key=DEST_KEY, Body=csv_buffer.getvalue())
    print(f"Uploaded cleaned data to s3://{DEST_BUCKET}/{DEST_KEY}")

# ---- Define the DAG ----
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="basic_s3_etl",
    default_args=default_args,
    description="Basic ETL job using Airflow and S3",
    schedule_interval="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_from_s3,
        provide_context=True,
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_data,
        provide_context=True,
    )

    load = PythonOperator(
        task_id="load",
        python_callable=load_to_s3,
        provide_context=True,
    )

    extract >> transform >> load


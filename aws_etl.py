import boto3
import pandas as pd
import json
from io import StringIO

# --- Load Config ---
with open('config.json', 'r') as f:
    config = json.load(f)

SOURCE_BUCKET = config['source_bucket']
SOURCE_KEY = config['source_key']
DEST_BUCKET = config['destination_bucket']
DEST_KEY = config['destination_key']

# --- AWS S3 Client ---
s3 = boto3.client('s3')

def extract():
    """Extract CSV file from S3"""
    print(f"Extracting data from s3://{SOURCE_BUCKET}/{SOURCE_KEY}...")
    response = s3.get_object(Bucket=SOURCE_BUCKET, Key=SOURCE_KEY)
    csv_content = response['Body'].read().decode('utf-8')
    df = pd.read_csv(StringIO(csv_content))
    print(f"Extracted {len(df)} rows.")
    return df

def transform(df):
    """Transform data (drop missing values)"""
    print("Transforming data...")
    df_clean = df.dropna()
    print(f"Rows after transformation: {len(df_clean)}")
    return df_clean

def load(df):
    """Load data to S3"""
    print(f"Loading data to s3://{DEST_BUCKET}/{DEST_KEY}...")
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3.put_object(Bucket=DEST_BUCKET, Key=DEST_KEY, Body=csv_buffer.getvalue())
    print("Upload complete.")

def main():
    df = extract()
    df_clean = transform(df)
    load(df_clean)

if __name__ == '__main__':
    main()


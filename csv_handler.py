import os
import pandas as pd
from config import DOWNLOAD_DIR, ORDER_ID_COLUMN

def get_latest_csv():
    files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".csv")]
    if not files:
        raise Exception("No CSV file found in downloads folder")

    files.sort(key=lambda x: os.path.getmtime(os.path.join(DOWNLOAD_DIR, x)), reverse=True)
    return os.path.join(DOWNLOAD_DIR, files[0])


def extract_order_ids():
    latest_csv = get_latest_csv()
    df = pd.read_csv(latest_csv)

    if ORDER_ID_COLUMN not in df.columns:
        raise Exception(f"{ORDER_ID_COLUMN} column not found in CSV")

    order_ids = df[ORDER_ID_COLUMN].dropna().astype(str).tolist()

    return order_ids

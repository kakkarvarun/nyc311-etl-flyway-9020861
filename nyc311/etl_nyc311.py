#!/usr/bin/env python3

"""
NYC 311 ETL (chunked) — inserts into MySQL in 10k-row chunks and logs progress.

Environment variables:
- MYSQL_HOST (default: localhost)
- MYSQL_PORT (default: 3306)
- MYSQL_USER (default: root)
- MYSQL_PASSWORD (required if not using socket auth)
- MYSQL_DB (default: nyc311)

Run:
  python nyc311/etl_nyc311.py
"""

import os
import sys
import time
import logging
import pandas as pd
from sqlalchemy import create_engine, text

# --- Config ---
API_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.csv?$limit=50000"  # manageable size
CHUNK_SIZE = 10_000

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Secret5555")
MYSQL_DB = os.getenv("MYSQL_DB", "nyc311")

LOG_FILE = os.path.join(os.path.dirname(__file__), "etl_log.txt")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

def get_engine():
    url = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    return create_engine(url, pool_pre_ping=True)

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    # Select and rename columns to match schema
    cols = {
        "unique_key": "unique_key",
        "created_date": "created_date",
        "closed_date": "closed_date",
        "agency": "agency",
        "complaint_type": "complaint_type",
        "descriptor": "descriptor",
        "borough": "borough",
        "latitude": "latitude",
        "longitude": "longitude",
    }
    # Some rows may lack columns; select intersection
    available = [c for c in cols if c in df.columns]
    df = df[available].copy()

    # Parse datetimes if present
    for c in ["created_date", "closed_date"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    # Numeric lat/lon
    for c in ["latitude", "longitude"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # unique_key as int
    if "unique_key" in df.columns:
        df["unique_key"] = pd.to_numeric(df["unique_key"], errors="coerce").astype("Int64")

    # Drop dupes on primary key if present
    if "unique_key" in df.columns:
        df = df.dropna(subset=["unique_key"]).drop_duplicates(subset=["unique_key"])
        df["unique_key"] = df["unique_key"].astype("int64")

    return df

def main():
    start = time.time()
    logger.info("Starting NYC311 ETL from %s", API_URL)
    try:
        engine = get_engine()
        # Quick connectivity check
        with engine.begin() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Connected to MySQL at %s:%s db=%s", MYSQL_HOST, MYSQL_PORT, MYSQL_DB)
    except Exception as e:
        logger.exception("Failed to connect to MySQL: %s", e)
        sys.exit(1)

    total_rows = 0
    chunk_idx = 0

    try:
        for chunk in pd.read_csv(API_URL, chunksize=CHUNK_SIZE, low_memory=False):
            chunk_idx += 1
            logger.info("Read raw chunk %d with %d rows", chunk_idx, len(chunk))
            df = normalize_df(chunk)
            if df.empty:
                logger.warning("Chunk %d normalized to 0 rows; skipping", chunk_idx)
                continue

            # Append chunk
            try:
                df.to_sql("service_requests", con=engine, if_exists="append", index=False, method="multi", chunksize=1000)
                total_rows += len(df)
                logger.info("Inserted chunk %d with %d rows (cumulative %d)", chunk_idx, len(df), total_rows)
            except Exception as e:
                logger.exception("Insert failed on chunk %d: %s", chunk_idx, e)

    except Exception as e:
        logger.exception("Streaming read failed: %s", e)

    elapsed = time.time() - start
    logger.info("ETL complete. Total rows inserted: %d in %.2fs", total_rows, elapsed)
    print(f"ETL complete. Total rows inserted: {total_rows} in {elapsed:.2f}s. See log: {LOG_FILE}")

if __name__ == "__main__":
    main()
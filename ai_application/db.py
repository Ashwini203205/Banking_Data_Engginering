"""
Database helper — read-only access to the Banking PostgreSQL database.
"""

import warnings
import pandas as pd
import psycopg2
from config import DB_CONFIG

warnings.filterwarnings("ignore", category=UserWarning, module="pandas")


def get_connection():
    """Return a new psycopg2 connection."""
    return psycopg2.connect(**DB_CONFIG)


def run_query(sql: str) -> pd.DataFrame:
    """
    Execute a SELECT query and return a pandas DataFrame.
    Returns an empty DataFrame on error.
    """
    conn = None
    try:
        conn = get_connection()
        df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()





def test_connection() -> bool:
    """Return True if the database is reachable."""
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception:
        return False


def get_table_counts() -> dict:
    """Return row counts for key tables."""
    tables = {
        "bronze.customer_raw": "SELECT COUNT(*) FROM bronze.customer_raw",
        "silver.customer_clean": "SELECT COUNT(*) FROM silver.customer_clean",
        "gold.customer_summary": "SELECT COUNT(*) FROM gold.customer_summary",
        "gold.education_summary": "SELECT COUNT(*) FROM gold.education_summary",
        "gold.job_summary": "SELECT COUNT(*) FROM gold.job_summary",
        "gold.marital_summary": "SELECT COUNT(*) FROM gold.marital_summary",
        "gold.month_summary": "SELECT COUNT(*) FROM gold.month_summary",
    }
    counts = {}
    for name, sql in tables.items():
        try:
            df = run_query(sql)
            counts[name] = int(df.iloc[0, 0]) if not df.empty else 0
        except Exception:
            counts[name] = 0
    return counts

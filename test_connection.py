"""
Test connection script to verify PostgreSQL database accessibility.
"""

import os, sys
import psycopg2

sys.stdout.reconfigure(encoding='utf-8')

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "banking_analytics")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    cur.execute("SELECT version();")
    db_version = cur.fetchone()[0]
    print(f"✅ Successfully connected to PostgreSQL Database '{DB_NAME}' on {DB_HOST}:{DB_PORT}!")
    print(f"PostgreSQL Version: {db_version}\n")
    
    # Query sample tables
    cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema IN ('gold', 'silver', 'bronze');")
    tables = cur.fetchall()
    print("Available Data Tables:")
    for schema, tbl in tables:
        cur.execute(f"SELECT COUNT(*) FROM {schema}.{tbl};")
        cnt = cur.fetchone()[0]
        print(f"  - {schema}.{tbl}: {cnt:,} records")
        
    cur.close()
    conn.close()
    print("\n✅ All connection checks passed successfully!")

except Exception as e:
    print(f"❌ Connection failed: {e}")
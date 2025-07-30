import os
from dotenv import load_dotenv
import psycopg2

# Load .env variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

def get_pg_connection():
    conn = psycopg2.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    )
    return conn

if __name__ == "__main__":
    try:
        conn = get_pg_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print("PostgreSQL version:", version[0])
        cur.close()
        conn.close()
    except Exception as e:
        print("Connection failed:", e)
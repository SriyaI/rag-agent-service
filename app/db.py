# db.py
import os
import psycopg2
from psycopg2 import sql, extras
from dotenv import load_dotenv

load_dotenv()

db_config = {
    "user": "",
    "password": "",
    "host": "",
    "port": "",
    "database": "",
    "sslmode": "",
    "sslrootcert": "" 
}

def get_db_connection():
    conn = psycopg2.connect(**db_config)
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255),
                    name VARCHAR(255),
                    company VARCHAR(255)
                );
            """)
            conn.commit()
    print("Ensured 'users' table exists")
    conn.close()

init_db()

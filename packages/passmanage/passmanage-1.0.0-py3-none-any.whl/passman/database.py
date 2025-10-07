from ast import Tuple
import sqlite3
from typing import Optional

DB_PATH = "storage.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS master(
            id INT PRIMARY KEY CHECK (id = 1),
            hash BLOB NOT NULL
        );
        """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS secrets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT NOT NULL,
        username TEXT,
        ciphertext BLOB NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def store_hash(hash_bytes:bytes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO master (id , hash) VALUES(1 , ?)",(hash_bytes,))
    conn.commit()
    conn.close()

def get_hash() -> Optional[bytes]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT hash FROM master WHERE id =1")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def store_secrets(service: str , username:str , ciphertext:bytes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO secrets (service , username , ciphertext) VALUES(?,?,?)",(service, username , ciphertext))
    conn.commit()
    conn.close()

def get_secrets(service:str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id,service,username,ciphertext FROM secrets WHERE service = ?",(service,))
    row = cur.fetchone()
    conn.close()
    return row


def get_all_secrets() -> list[tuple[int , str , str , bytes]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM secrets ORDER BY service")
    row = cur.fetchall()
    conn.close()
    return row

def delete_service(service:str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM secrets WHERE service = ?",(service,))
    conn.commit()
    conn.close()

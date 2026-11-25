import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'urls.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_code TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                clicks INTEGER DEFAULT 0
            )
        ''')
        conn.commit()

def insert_url(original_url, short_code):
    with get_db_connection() as conn:
        try:
            conn.execute(
                'INSERT INTO urls (original_url, short_code) VALUES (?, ?)',
                (original_url, short_code)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def get_url_by_code(short_code):
    with get_db_connection() as conn:
        row = conn.execute(
            'SELECT * FROM urls WHERE short_code = ?',
            (short_code,)
        ).fetchone()
        return dict(row) if row else None

def increment_clicks(short_code):
    with get_db_connection() as conn:
        conn.execute(
            'UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?',
            (short_code,)
        )
        conn.commit()

def get_all_urls():
    with get_db_connection() as conn:
        rows = conn.execute(
            'SELECT id, original_url, short_code, created_at, clicks FROM urls ORDER BY created_at DESC'
        ).fetchall()
        return [dict(row) for row in rows]

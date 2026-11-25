"""
SQLite Database Layer for Encrypted Local Password Vault
"""

import sqlite3
import os
import time
from crypto_utils import encrypt_data, decrypt_data, hashlib, base64

DB_FILE = os.path.join(os.path.dirname(__file__), "vault_data.db")

class VaultDatabase:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Master password config table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS master_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL
                )
            """)
            # Vault entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vault_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    username TEXT,
                    encrypted_password TEXT NOT NULL,
                    website TEXT,
                    category TEXT DEFAULT 'General',
                    notes TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            """)
            conn.commit()

    def is_master_set(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM master_config")
            count = cursor.fetchone()[0]
            return count > 0

    def set_master_password(self, master_password):
        salt = base64.b64encode(os.urandom(16)).decode('utf-8')
        pwd_hash = hashlib.sha256((master_password + salt).encode('utf-8')).hexdigest()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM master_config")
            cursor.execute("INSERT INTO master_config (password_hash, salt) VALUES (?, ?)", (pwd_hash, salt))
            conn.commit()

    def verify_master_password(self, master_password):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash, salt FROM master_config LIMIT 1")
            row = cursor.fetchone()
            if not row:
                return False
            stored_hash, salt = row
            check_hash = hashlib.sha256((master_password + salt).encode('utf-8')).hexdigest()
            return check_hash == stored_hash

    def add_entry(self, title, username, raw_password, website, category, notes, master_password):
        enc_pwd = encrypt_data(raw_password, master_password)
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO vault_entries (title, username, encrypted_password, website, category, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, username, enc_pwd, website, category, notes, now, now))
            conn.commit()
            return cursor.lastrowid

    def update_entry(self, entry_id, title, username, raw_password, website, category, notes, master_password):
        enc_pwd = encrypt_data(raw_password, master_password)
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE vault_entries
                SET title = ?, username = ?, encrypted_password = ?, website = ?, category = ?, notes = ?, updated_at = ?
                WHERE id = ?
            """, (title, username, enc_pwd, website, category, notes, now, entry_id))
            conn.commit()

    def delete_entry(self, entry_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vault_entries WHERE id = ?", (entry_id,))
            conn.commit()

    def get_all_entries(self, master_password, search_query="", category_filter="All"):
        entries = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, title, username, encrypted_password, website, category, notes, created_at, updated_at FROM vault_entries"
            params = []
            conditions = []

            if category_filter and category_filter != "All":
                conditions.append("category = ?")
                params.append(category_filter)

            if search_query:
                conditions.append("(title LIKE ? OR username LIKE ? OR website LIKE ?)")
                q = f"%{search_query}%"
                params.extend([q, q, q])

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY updated_at DESC"
            cursor.execute(query, params)

            for row in cursor.fetchall():
                eid, title, uname, enc_pwd, site, cat, notes, cat_at, up_at = row
                dec_pwd = decrypt_data(enc_pwd, master_password) or "[Decryption Failed]"
                entries.append({
                    "id": eid,
                    "title": title,
                    "username": uname,
                    "password": dec_pwd,
                    "website": site,
                    "category": cat,
                    "notes": notes,
                    "created_at": cat_at,
                    "updated_at": up_at
                })
        return entries

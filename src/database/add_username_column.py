import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance', 'imdb_movies.db'))

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users);")
    columns = [col[1] for col in cursor.fetchall()]
    if 'username' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN username TEXT;")
        print("Added 'username' column to users table.")
    else:
        print("'username' column already exists.")

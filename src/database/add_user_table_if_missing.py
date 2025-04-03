import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'imdb_movies.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the 'users' table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
table_exists = cursor.fetchone()

if table_exists:
    print("'users' table already exists.")
else:
    print("Creating 'users' table...")
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    print("'users' table created successfully.")

conn.close()

#!/usr/bin/env python
import os
import sys
from filter_data import store_tmdb_data, create_app
from models import db

def reset_database():
    """Remove old database and create a new one."""
    app = create_app()
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

    if os.path.exists(db_path):
        print(f"🗑 Removing old database: {db_path}")
        os.remove(db_path)

    with app.app_context():
        print("📂 Creating new database schema...")
        db.create_all()
        print("✅ Database schema created.")

def main():
    """Reset database and import fresh TMDb data."""
    try:
        print("🔄 Resetting database...")
        reset_database()

        print("📡 Fetching and importing TMDb data...")
        store_tmdb_data()
        
        print("🎉 Database setup complete!")
        return 0  # Success
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1  # Failure


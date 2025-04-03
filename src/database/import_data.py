#!/usr/bin/env python
import os
import sys
from filter_data import store_tmdb_data, create_app
from models import db, Movie

def reset_database():
    """Remove old database and create a new one."""
    app = create_app()
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

    print(f"[import_data.py] DB path: {db_path}")

    if os.path.exists(db_path):
        print(f"[import_data.py] Removing old database: {db_path}")
        os.remove(db_path)

    with app.app_context():
        print("[import_data.py] Creating new database schema...")
        db.create_all()
        print("[import_data.py] ✅ Database schema created.")
        print("[import_data.py] Tables:", list(db.metadata.tables.keys()))

def verify_inserted_data():
    """Check how many movies were stored"""
    app = create_app()
    with app.app_context():
        movie_count = Movie.query.count()
        print(f"[import_data.py] ✅ Total movies stored in DB: {movie_count}")
        if movie_count == 0:
            print("[import_data.py] ⚠️ No movies stored. Something went wrong in store_tmdb_data().")

def main():
    """Reset database and import fresh TMDb data."""
    try:
        print("[import_data.py] 🔄 Resetting database...")
        reset_database()

        print("[import_data.py] 📡 Fetching and importing TMDb data...")
        store_tmdb_data()

        print("[import_data.py] ✅ Finished importing data.")
        verify_inserted_data()

        print("[import_data.py] 🎉 Database setup complete!")
        return 0  # Success
    except Exception as e:
        print(f"[import_data.py] ❌ Error during import: {e}")
        return 1  # Failure

if __name__ == "__main__":
    sys.exit(main())

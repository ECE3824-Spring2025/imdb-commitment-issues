#!/usr/bin/env python
import sys
import os

from flask import Flask
from models import db, Movie
from filter_data import store_tmdb_data  # Make sure this is still correct

# --- Setup Flask + SQLAlchemy ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://comp3_webapp:imdbcomp3proj@imdb-commitment-issues.cxnec0l3uyax.us-east-1.rds.amazonaws.com:3306/imdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def reset_database():
    """Drop and recreate all tables in the database."""
    with app.app_context():
        print("[import_data.py] Dropping all existing tables...")
        db.drop_all()
        print("[import_data.py] Creating fresh tables...")
        db.create_all()
        print("[import_data.py] ✅ Database schema reset complete.")

def verify_inserted_data():
    """Check how many movies were stored."""
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
        return 0
    except Exception as e:
        print(f"[import_data.py] ❌ Error during import: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

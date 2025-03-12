#!/usr/bin/env python
"""
Simple command-line script to import filtered data CSV into the database.
Always replaces the existing database with fresh data.
"""
import sys
import argparse
import os
from filter_data import import_filtered_csv_to_db, create_app
from models import db

def reset_database():
    """
    Remove the existing database file and create a new empty one.
    """
    # Create the app to get database path
    app = create_app()
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    # Get the full path to the database file
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
    
    db_file = os.path.join(instance_dir, 'imdb_movies.db')
    
    # Delete existing database if it exists
    if os.path.exists(db_file):
        print(f"Removing existing database file: {db_file}")
        os.remove(db_file)
        print("Database file removed successfully.")
    
    # Create a new empty database with the schema
    with app.app_context():
        print("Creating new database schema...")
        db.create_all()
        print("Database schema created successfully.")

def main():
    parser = argparse.ArgumentParser(description='Import filtered IMDb data from CSV to database')
    parser.add_argument('--csv', type=str, default='./data/filtered_data.csv',
                        help='Path to filtered CSV file (default: ./data/filtered_data.csv)')
    parser.add_argument('--batch-size', type=int, default=200,
                        help='Batch size for database operations (default: 1000)')
    args = parser.parse_args()
    
    # Always reset the database before import
    try:
        print("Resetting database...")
        reset_database()
    except Exception as e:
        print(f"Error resetting database: {str(e)}")
        return 1
    
    print(f"Starting import from {args.csv} with batch size {args.batch_size}")
    try:
        record_count = import_filtered_csv_to_db(args.csv, args.batch_size)
        print(f"Success! Imported {record_count} records to the database.")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
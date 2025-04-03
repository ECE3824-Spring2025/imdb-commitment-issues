from models import db, User  # Ensure User class is defined in models.py
from flask import Flask
from sqlalchemy import inspect
import os

# Setup Flask and DB path
app = Flask(__name__)
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance', 'imdb_movies.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    engine = db.engine  # Use db.engine directly instead of get_engine()
    inspector = inspect(engine)

    if not inspector.has_table('users'):
        print("'users' table not found. Creating it now...")
        User.__table__.create(bind=engine)
        print("'users' table created.")
    else:
        print("'users' table already exists.")

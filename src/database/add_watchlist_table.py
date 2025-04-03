from flask import Flask
from sqlalchemy import inspect
from models import db, Watchlist, User  # User must be imported so FK is valid
import os

app = Flask(__name__)
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance', 'imdb_movies.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    engine = db.engine
    inspector = inspect(engine)

    if not inspector.has_table('watchlist'):
        Watchlist.__table__.create(bind=engine)
        print("'watchlist' table created.")
    else:
        print("'watchlist' table already exists.")

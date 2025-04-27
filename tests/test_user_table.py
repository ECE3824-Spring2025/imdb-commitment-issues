import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/database')))
import pytest
from flask import Flask
from models import db, User
from sqlalchemy import inspect

# Setup test app using the actual database
@pytest.fixture(scope='module')
def app():
    app = Flask(__name__)
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'database', 'instance', 'imdb_movies.db'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def test_users_table_exists(app):
    with app.app_context():
        inspector = inspect(db.engine)
        assert inspector.has_table('users'), "'users' table does not exist"

def test_create_and_read_user(app):
    test_email = 'pytest_user@example.com'
    with app.app_context():
        # Remove if user already exists (re-runs of test)
        User.query.filter_by(email=test_email).delete()
        db.session.commit()

        # Add new user
        user = User(email=test_email, password_hash='fakehash')
        db.session.add(user)
        db.session.commit()

        # Fetch user from DB
        retrieved = User.query.filter_by(email=test_email).first()
        assert retrieved is not None, "User not found after insert"
        assert retrieved.email == test_email

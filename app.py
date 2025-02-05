import os
from flask import Flask
from models import db

# Configuration settings
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Register routes
    from routes.movie_routes import movie_bp
    app.register_blueprint(movie_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

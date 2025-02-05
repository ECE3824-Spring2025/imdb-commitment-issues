from flask import Flask
from config import Config
from models import db

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

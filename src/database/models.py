from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

# Association table for many-to-many between movies and genres
movie_genre_association = db.Table(
    'movie_genre',
    db.Column('movie_id', db.String(255), db.ForeignKey('movies.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    def __repr__(self):
        return f"<Genre(name='{self.name}')>"

class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.String(255), primary_key=True)
    title_type = db.Column(db.String(255))
    primary_title = db.Column(db.String(255))
    original_title = db.Column(db.String(255))
    start_year = db.Column(db.Integer, nullable=True)
    poster_url = db.Column(db.String(512), nullable=True)
    description = db.Column(db.Text, nullable=True)
    runtime = db.Column(db.Integer, nullable=True)
    actors = db.Column(db.Text, nullable=True)  # Stored as JSON string

    genres = db.relationship("Genre", secondary=movie_genre_association, backref="movies")
    rating = db.relationship("Rating", back_populates="movie", uselist=False)

    def to_dict(self):
        try:
            parsed_actors = json.loads(self.actors) if self.actors else []
        except Exception:
            parsed_actors = []
        return {
            'id': self.id,
            'title_type': self.title_type,
            'primary_title': self.primary_title,
            'original_title': self.original_title,
            'start_year': self.start_year,
            'poster_url': self.poster_url,
            'description': self.description,
            'runtime': self.runtime,
            'actors': parsed_actors,
            'genres': [genre.name for genre in self.genres],
            'rating': self.rating.to_dict() if self.rating else None
        }

class Rating(db.Model):
    __tablename__ = 'ratings'

    movie_id = db.Column(db.String(255), db.ForeignKey('movies.id'), primary_key=True)
    average_rating = db.Column(db.Float)
    num_votes = db.Column(db.Integer)

    movie = db.relationship("Movie", back_populates="rating")

    def to_dict(self):
        return {
            'average_rating': self.average_rating,
            'num_votes': self.num_votes
        }

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)  # ✅ username must NOT be nullable
    profile_image = db.Column(db.String(512), nullable=True)

    watchlist = db.relationship('Watchlist', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'profile_image': self.profile_image
        }

    def __repr__(self):
        return f"<User(email='{self.email}', username='{self.username}')>"

class Watchlist(db.Model):
    __tablename__ = 'watchlist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.String(255), nullable=False)  # Optional FK to movies.id

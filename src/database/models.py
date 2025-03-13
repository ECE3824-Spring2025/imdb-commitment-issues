from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

movie_genre_association = db.Table(
    'movie_genre',
    db.Column('movie_id', db.String, db.ForeignKey('movies.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'))
)

class Genre(db.Model):
    __tablename__ = 'genres'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Genre(name='{self.name}')>"

class Movie(db.Model):
    __tablename__ = 'movies'
    
    id = db.Column(db.String, primary_key=True)
    title_type = db.Column(db.String)
    primary_title = db.Column(db.String)
    original_title = db.Column(db.String)
    start_year = db.Column(db.Integer, nullable=True)
    poster_url = db.Column(db.String, nullable=True)

    genres = db.relationship("Genre", secondary=movie_genre_association, backref="movies")
    rating = db.relationship("Rating", back_populates="movie", uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title_type': self.title_type,
            'primary_title': self.primary_title,
            'original_title': self.original_title,
            'start_year': self.start_year,
            'poster_url': self.poster_url,
            'genres': [genre.name for genre in self.genres],
            'rating': self.rating.to_dict() if self.rating else None
        }

class Rating(db.Model):
    __tablename__ = 'ratings'
    
    movie_id = db.Column(db.String, db.ForeignKey('movies.id'), primary_key=True)
    average_rating = db.Column(db.Float)
    num_votes = db.Column(db.Integer)

    movie = db.relationship("Movie", back_populates="rating")

    def to_dict(self):
        return {
            'average_rating': self.average_rating,
            'num_votes': self.num_votes
        }

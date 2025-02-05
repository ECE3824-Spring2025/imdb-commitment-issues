from models import db

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, nullable=True)  # Nullable rating
    votes = db.Column(db.Integer, nullable=True)  # Nullable votes
    genre = db.Column(db.String(50), nullable=False)  # Action, Comedy, Drama
    category = db.Column(db.String(50), nullable=False)  # Top by Votes or Rating

    def __repr__(self):
        return f"<Movie {self.title} - {self.genre} - {self.category}>"

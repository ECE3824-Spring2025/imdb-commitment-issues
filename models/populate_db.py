import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import db
from models.movie import Movie
from data.movie_data import (
    ListWithRatingDrama, ListWithRatingAction, ListWithRatingComedy,
    ListWithLikesDrama, ListWithLikesAction, ListWithLikesComedy
)
from app import create_app  # Import existing app

def populate_database():
    """Populates the database with initial movie data."""
    app = create_app()
    with app.app_context():
        db.create_all()  # Ensure tables exist

        movie_data = [
            (ListWithRatingAction, "action", "Top by Rating"),
            (ListWithLikesAction, "action", "Top by Votes"),
            (ListWithRatingComedy, "comedy", "Top by Rating"),
            (ListWithLikesComedy, "comedy", "Top by Votes"),
            (ListWithRatingDrama, "drama", "Top by Rating"),
            (ListWithLikesDrama, "drama", "Top by Votes"),
        ]

        for movie_list, genre, category in movie_data:
            for movie in movie_list:
                new_movie = Movie(
                    title=movie["name"],  # Adjusted to match your data
                    rating=movie.get("rating"),  # None if missing
                    votes=movie.get("votes"),  # None if missing
                    genre=genre,
                    category=category
                )
                db.session.add(new_movie)

        db.session.commit()
        print("Database populated successfully!")

if __name__ == "__main__":
    populate_database()

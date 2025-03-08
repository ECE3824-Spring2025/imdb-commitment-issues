import sys
import os
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import db
from models.movie import Movie
from app import create_app  # Import Flask app

# TMDB API Details
API_KEY = "61c678e1170ca246fbfbdeecc7aa373b"
TMDB_DISCOVER_URL = "https://api.themoviedb.org/3/discover/movie"

# Genre mapping (TMDB ID → Local genre name)
GENRES = {
    "action": 28,
    "comedy": 35,
    "drama": 18
}

# Database Path
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database.db"))

def delete_old_database():
    """Deletes the existing database file if it exists."""
    if os.path.exists(DB_PATH):
        print("Deleting old database...")
        os.remove(DB_PATH)

def fetch_movies_by_genre(genre_id, sort_by):
    """
    Fetch movies from TMDB API based on genre and sorting method.
    
    :param genre_id: TMDB genre ID
    :param sort_by: Sorting parameter ('vote_average.desc' or 'vote_count.desc')
    :return: List of top 10 unique movie dictionaries
    """
    try:
        response = requests.get(
            TMDB_DISCOVER_URL,
            params={
                "api_key": API_KEY,
                "language": "en-US",
                "with_genres": genre_id,
                "sort_by": sort_by,
                "vote_count.gte": 100,  # Avoid movies with very few votes
                "page": 1
            }
        )
        response.raise_for_status()
        data = response.json()

        # Debugging: Print the first few movies to verify API response
        print(f"Fetching movies for genre {genre_id}, sorted by {sort_by}:")
        print([movie["title"] for movie in data["results"][:10]])

        # Step 1: Remove duplicates using a set
        unique_movies = []
        seen_titles = set()

        for movie in data.get("results", []):
            normalized_title = movie["title"].lower().strip()  # Normalize title
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_movies.append(movie)

        # Step 2: Return only the top 10 unique movies
        return unique_movies[:10]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching movies: {e}")
        return []

def populate_database():
    """Deletes existing database and populates it with fresh data from TMDB."""
    
    # Step 1: Delete old database
    delete_old_database()

    # Step 2: Create a new Flask app instance
    app = create_app()

    with app.app_context():
        # Step 3: Drop all tables and recreate them
        db.drop_all()
        db.create_all()

        for genre_name, genre_id in GENRES.items():
            # Keep track of movies we've already added for this genre
            seen_movies = set()

            # Fetch **Top 10 Rated** and **Top 10 Most Voted** movies
            top_rated_movies = fetch_movies_by_genre(genre_id, "vote_average.desc")
            most_voted_movies = fetch_movies_by_genre(genre_id, "vote_count.desc")

            # Insert Top Rated Movies
            for movie in top_rated_movies:
                normalized_title = movie["title"].lower().strip()
                if normalized_title not in seen_movies:
                    seen_movies.add(normalized_title)
                    new_movie = Movie(
                        title=movie["title"],
                        rating=movie.get("vote_average"),
                        votes=movie.get("vote_count"),
                        genre=genre_name,
                        category="Top by Rating"
                    )
                    db.session.add(new_movie)

            # Insert Most Voted Movies
            for movie in most_voted_movies:
                normalized_title = movie["title"].lower().strip()
                if normalized_title not in seen_movies:
                    seen_movies.add(normalized_title)
                    new_movie = Movie(
                        title=movie["title"],
                        rating=movie.get("vote_average"),
                        votes=movie.get("vote_count"),
                        genre=genre_name,
                        category="Top by Votes"
                    )
                    db.session.add(new_movie)

        # Step 4: Commit changes to database
        db.session.commit()
        print("✅ Database successfully created and populated with TMDB data!")

        # Step 5: Verify database contents
        movies = Movie.query.all()
        print("\nMovies in database:")
        for movie in movies:
            print(f"{movie.title} - Rating: {movie.rating} - Genre: {movie.genre}")

if __name__ == "__main__":
    populate_database()

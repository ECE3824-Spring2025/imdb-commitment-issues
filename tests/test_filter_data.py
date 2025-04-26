import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/database')))
import pytest
import json
from unittest.mock import patch, MagicMock
from filter_data import store_tmdb_data, fetch_top_rated_movies, create_app, redis_client
from models import db, Movie, Genre, Rating

# ---- Fixtures ----
# Pytest fixtures allow us to create reusable test setup logic.

@pytest.fixture
def app():
    """
    Fixture to create a Flask test application.
    
    This initializes an in-memory database to avoid affecting real data.
    """
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Use an in-memory database
    with app.app_context():
        db.create_all()  # Create database tables for testing
        yield app


@pytest.fixture
def client(app):
    """
    Fixture to create a test client for the Flask application.
    
    This allows us to send HTTP requests to the API without running the actual server.
    """
    return app.test_client()


@pytest.fixture
def mock_redis():
    """
    Fixture to mock the Redis client.
    
    This prevents actual Redis caching during testing.
    """
    with patch("filter_data.redis_client") as mock_redis:
        mock_redis.get.return_value = None  # Simulate cache miss
        yield mock_redis


@pytest.fixture
def mock_requests():
    """
    Fixture to mock TMDb API requests.
    
    This prevents external API calls and provides a controlled response.
    """
    fake_response = {
        "results": [
            {
                "id": 12345,
                "title": "Mock Movie",
                "original_title": "Mock Movie Original",
                "release_date": "2024-01-01",
                "poster_path": "/mock_poster.jpg",
                "vote_average": 8.5,
                "vote_count": 200,
                "genre_ids": [28, 12]  # Action, Adventure
            }
        ]
    }
    
    with patch("filter_data.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = fake_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        yield mock_get


# ---- Unit Tests ----

def test_fetch_top_rated_movies(mock_requests, mock_redis):
    """
    Test Case: Fetch top-rated movies from TMDb.

    Scenario:
    - The `fetch_top_rated_movies` function is called.

    Expectations:
    - The function should return movie data.
    - If Redis caching is enabled, data should be stored in the cache.
    """
    movies = fetch_top_rated_movies()
    
    # Validate response
    assert len(movies) > 0
    assert movies[0]["title"] == "Mock Movie"


def test_store_tmdb_data(app, mock_requests, mock_redis):
    """
    Test Case: Store TMDb data in the database.

    Scenario:
    - The `store_tmdb_data` function is called.
    - The database should be updated with movies, genres, and ratings.

    Expectations:
    - The function should insert movies into the database.
    - Associated genres and ratings should also be stored.
    """
    with app.app_context():
        store_tmdb_data()

        # Validate that the movie was inserted correctly
        movie = Movie.query.filter_by(primary_title="Mock Movie").first()
        assert movie is not None
        assert movie.original_title == "Mock Movie Original"
        assert movie.start_year == 2024

        # Validate that the rating was linked correctly
        rating = Rating.query.filter_by(movie_id=movie.id).first()
        assert rating is not None
        assert rating.average_rating == 8.5

        # Validate that genres were associated correctly
        genres = [genre.name for genre in movie.genres]
        assert "Action" in genres
        assert "Adventure" in genres

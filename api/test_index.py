import pytest
import json
from mock import patch, MagicMock
from index import app

# ---- Fixtures ----
# Pytest fixtures allow us to create reusable test setup logic.

@pytest.fixture
def client():
    """
    Fixture to create a test client for the Flask application.
    This allows us to send HTTP requests to the API without running the actual server.
    """

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_db_connection():
    """
    Fixture to mock the database connection.
    This prevents actual database queries during testing. 
    """

    with patch("index.db_connection") as mock_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value.__enter__.return_value = mock_conn
        yield mock_cursor

@pytest.fixture
def mock_redis():
    """
    Fixture to mock the Redis client.
    This prevents actual Redis caching during testing.
    """
    with patch("index.redis_client") as mock_redis:
        mock_redis.get.return_value = None  # Simulate cache miss
        yield mock_redis

# ---- Unit Tests ----

def test_get_movie_images(client, mock_db_connection, mock_redis):
    """
    Test Case: Retrieve movie images from TMDb.

    Scenario:
    - The `/api/movies/<movie_id>/images` endpoint is called.

    Expectations:
    - The response should return status `200 OK` if the movie is found.
    - The response JSON should contain `images` with `poster_url` and `backdrop_url`.
    """

    mock_db_connection.execute.return_value = None
    mock_db_connection.fetchone.return_value = {"primary_title": "Test Movie", "start_year": 2003}

    with patch("index.search_tmdb_movie") as mock_tmdb:
        mock_tmdb.return_value = {
            "id": 12345,
            "poster_path": "/test_poster.jpg",
            "backdrop_path": "/test_backdrop.jpg"
        }

        response = client.get("/api/movies/tt0000001/images")
        assert response.status_code == 200

        data = response.get_json()
        assert "images" in data
        assert data["images"]["poster_url"] is not None
        assert data["images"]["backdrop_url"] is not None

def test_get_movie_poster(client, mock_db_connection, mock_redis):
    """
    Test Case: Retrieve a movie poster with different sizes.

    Scenario:
    - The `/api/movies/<movie_id>/poster` endpoint is called.

    Expectations:
    - The response should return status `200 OK` if the movie is found.
    - The response JSON should contain `posterUrl` and `size`.
    - If an invalid size is provided, it should default to `w500`.
    """
    # Mock database query to return movie details
    mock_db_connection.execute.return_value = None
    mock_db_connection.fetchone.return_value = {"primary_title": "Test Movie", "start_year": 2010}

    # Mock the TMDb API response
    with patch("index.search_tmdb_movie") as mock_tmdb:
        mock_tmdb.return_value = {
            "id": 12345,
            "poster_path": "/test_poster.jpg"
        }

        # Test with default size
        response = client.get("/api/movies/tt0000001/poster")
        assert response.status_code == 200
        data = response.get_json()
        assert "posterUrl" in data
        assert "size" in data
        assert data["size"] == "w500"  # Default size

        # Test with a valid size parameter
        response = client.get("/api/movies/tt0000001/poster?size=w185")
        assert response.status_code == 200
        data = response.get_json()
        assert data["size"] == "w185"

        # Test with an invalid size (should default to `w500`)
        response = client.get("/api/movies/tt0000001/poster?size=invalid")
        assert response.status_code == 200
        data = response.get_json()
        assert data["size"] == "w500"  # Default value for invalid input

        # Test when no poster is found
        mock_tmdb.return_value = {"id": 12345, "poster_path": None}
        response = client.get("/api/movies/tt0000001/poster")
        assert response.status_code == 200
        data = response.get_json()
        assert data["posterUrl"] is None
        assert data["message"] == "No poster found for this movie"

def test_get_movies(client, mock_db_connection, mock_redis):
    """
    Test Case: Retrieve a paginated list of movies.

    Scenario:
    - The `/api/movies` endpoint is called with default parameters.

    Expectations:
    - The response should return status `200 OK`.
    - The response JSON should contain `movies`, `total`, `page`, `pageSize`, and `query_time_ms`.
    """
    # Mock database response
    mock_db_connection.execute.return_value = None
    mock_db_connection.fetchone.side_effect = [(200,)] # Simulate total movie count
    mock_db_connection.fetchall.return_value = [
        {
            "id": "tt0000001",
            "primary_title": "Test Movie",
            "title_type": "movie",
            "average_rating": 8.5,
            "num_votes": 1000,
            "genres": "Drama,Action"
        }
    ]

    response = client.get("/api/movies")
    assert response.status_code == 200

    data = response.get_json()
    assert "movies" in data
    assert "total" in data
    assert "page" in data
    assert "pageSize" in data
    assert len(data["movies"]) > 0

def test_health_check(client):
    """
    Test Case: Health check endpoint returns expected response.

    Scenario:
    - The `/api/health` endpoint is called.

    Expectations:
    - The response should return status `200 OK`.
    - The response JSON should contain keys `status`, `timestamp`, `redis_available`, `db_exists`, and `tmdb_configured`.
    """
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.get_json()
    assert "status" in data
    assert "timestamp" in data
    assert "redis_available" in data
    assert "db_exists" in data
    assert "tmdb_configured" in data

def test_cache_clear(client, mock_redis):
    """
    Test Case: Clear cache keys.

    Scenario:
    - The `/api/cache/clear` endpoint is called with a pattern.

    Expectations:
    - The response should return status `200 OK`.
    - The response JSON should indicate success and the number of cleared keys.
    """

    mock_redis.keys.return_value = ["cache_key_1", "cache_key_2"]
    mock_redis.delete.return_value = 2  # Simulate deletion of 2 keys

    response = client.post("/api/cache/clear", json={"pattern": "*"})
    assert response.status_code == 200

    data = response.get_json()
    assert data["success"] is True
    assert "Cleared" in data["message"]

def test_invalid_movie_request(client):
    """
    Test Case: Requesting a movie that does not exist.

    Scenario:
    - The `/api/movies/<movie_id>` endpoint is called with a non-existent movie ID.

    Expectations:
    - The response should return status `404 NOT FOUND`.
    - The response JSON should indicate an error message.
    """
    with patch("index.db_connection") as mock_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Simulate no movie found
        mock_db.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/movies/invalid_id")
        assert response.status_code == 404

        data = response.get_json()
        assert "error" in data
        assert data["error"] == "Movie not found"

def test_get_genres(client, mock_db_connection, mock_redis):
    """
    Test Case: Retrieve a list of genres.

    Scenario:
    - The `/api/genres` endpoint is called.

    Expectations:
    - The response should return status `200 OK`.
    - The response JSON should contain a list of `genres` and a `total` count.
    """
    mock_db_connection.execute.return_value = None
    mock_db_connection.fetchall.return_value = [
        {"id": 1, "name": "Drama", "movie_count": 50},
        {"id": 2, "name": "Action", "movie_count": 40}
    ]

    response = client.get("/api/genres")
    assert response.status_code == 200

    data = response.get_json()
    assert "genres" in data
    assert "total" in data
    assert len(data["genres"]) > 0
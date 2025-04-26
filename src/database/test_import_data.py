import pytest
from unittest.mock import patch, MagicMock
from import_data import main, reset_database, verify_inserted_data

# ---- Fixtures ----

@pytest.fixture
def mock_db():
    """Fixture to mock SQLAlchemy `db.drop_all` and `db.create_all`."""
    with patch("import_data.db") as mock_db:
        yield mock_db

@pytest.fixture
def mock_store_tmdb_data():
    """Fixture to mock `store_tmdb_data`."""
    with patch("import_data.store_tmdb_data") as mock_func:
        yield mock_func

@pytest.fixture
def mock_movie_query():
    """Fixture to mock `Movie.query.count()`."""
    with patch("import_data.Movie") as mock_movie:
        yield mock_movie

# ---- Unit Tests ----

def test_reset_database(mock_db):
    """
    Test Case: Reset database by dropping and creating all tables.
    """
    reset_database()

    mock_db.drop_all.assert_called_once()
    mock_db.create_all.assert_called_once()

def test_verify_inserted_data_with_movies(mock_movie_query):
    """
    Test Case: Verify inserted data when movies exist.
    """
    mock_movie_query.query.count.return_value = 10

    verify_inserted_data()

    mock_movie_query.query.count.assert_called_once()

def test_verify_inserted_data_no_movies(mock_movie_query):
    """
    Test Case: Verify inserted data when no movies exist.
    """
    mock_movie_query.query.count.return_value = 0

    verify_inserted_data()

    mock_movie_query.query.count.assert_called_once()

def test_main_success(mock_store_tmdb_data, mock_db, mock_movie_query):
    """
    Test Case: Successful execution of `main()`.
    """
    mock_movie_query.query.count.return_value = 5  # Simulate movies exist

    result = main()

    assert result == 0
    mock_db.drop_all.assert_called_once()
    mock_db.create_all.assert_called_once()
    mock_store_tmdb_data.assert_called_once()
    mock_movie_query.query.count.assert_called_once()

def test_main_failure_in_reset(monkeypatch):
    """
    Test Case: Exception raised during `reset_database()`.
    """
    monkeypatch.setattr("import_data.reset_database", lambda: (_ for _ in ()).throw(Exception("Reset error")))

    result = main()
    assert result == 1

def test_main_failure_in_store(monkeypatch, mock_db):
    """
    Test Case: Exception raised during `store_tmdb_data()`.
    """
    monkeypatch.setattr("import_data.store_tmdb_data", lambda: (_ for _ in ()).throw(Exception("Store error")))

    result = main()
    assert result == 1
    mock_db.drop_all.assert_called_once()
    mock_db.create_all.assert_called_once()

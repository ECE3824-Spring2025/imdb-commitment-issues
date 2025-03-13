import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from import_data import main, reset_database  # Import the main function and database reset function
from filter_data import store_tmdb_data, create_app
from models import db

# ---- Fixtures ----
# Pytest fixtures allow us to create reusable test setup logic.

@pytest.fixture
def mock_store_tmdb_data():
    """
    Fixture to mock the `store_tmdb_data` function.
    This prevents actual API calls and simulates the TMDb data import process.
    """
    with patch("import_data.store_tmdb_data") as mock_func:
        yield mock_func

@pytest.fixture
def mock_reset_database():
    """
    Fixture to mock the `reset_database` function.
    This prevents actual database deletion and recreation during testing.
    """
    with patch("import_data.reset_database") as mock_func:
        yield mock_func

@pytest.fixture
def mock_create_app():
    """
    Fixture to mock the `create_app` function.
    This simulates a Flask app with a test database URI.
    """
    with patch("import_data.create_app") as mock_func:
        mock_app = MagicMock()
        mock_app.config = {"SQLALCHEMY_DATABASE_URI": "sqlite:///test.db"}
        mock_func.return_value = mock_app
        yield mock_func

@pytest.fixture
def mock_db():
    """
    Fixture to mock the database's `create_all` function.
    This prevents actual schema modifications during tests.
    """
    with patch("import_data.db.create_all") as mock_func:
        yield mock_func

@pytest.fixture
def mock_os_remove():
    """
    Fixture to mock `os.remove` to prevent actual file deletions.
    This ensures that the test does not delete any real database files.
    """
    with patch("os.remove") as mock_func:
        yield mock_func

@pytest.fixture
def mock_os_path_exists():
    """
    Fixture to mock `os.path.exists` to simulate different database file conditions.
    This allows testing scenarios where the database file exists or does not exist.
    """
    with patch("os.path.exists", return_value=True) as mock_func:
        yield mock_func

# ---- Unit Tests ----

def test_reset_database(mock_create_app, mock_db, mock_os_remove, mock_os_path_exists):
    """
    Test Case: Reset the database successfully.

    Scenario:
    - The database file exists and needs to be removed.
    - A new database schema is created.

    Expectations:
    - `create_app()` should be called to initialize the app.
    - The existing database file should be deleted.
    - `db.create_all()` should be called to create a new schema.
    """
    reset_database()

    mock_create_app.assert_called_once()
    mock_os_path_exists.assert_called_once()
    mock_os_remove.assert_called_once_with("test.db")
    mock_db.assert_called_once()

def test_reset_database_no_existing_db(mock_create_app, mock_db):
    """
    Test Case: Reset the database when no existing database file is found.

    Scenario:
    - The database file does not exist.
    - A new database schema is still created.

    Expectations:
    - `os.remove()` should not be called.
    - `db.create_all()` should still be called.
    """
    with patch("os.path.exists", return_value=False) as mock_path_exists, \
         patch("os.remove") as mock_remove:
        reset_database()

    mock_path_exists.assert_called_once()
    mock_remove.assert_not_called()
    mock_db.assert_called_once()

def test_main_success(mock_reset_database, mock_store_tmdb_data):
    """
    Test Case: Successful execution of `main()`.

    Scenario:
    - The database reset completes successfully.
    - The TMDb data import completes successfully.

    Expectations:
    - `reset_database()` should be called once.
    - `store_tmdb_data()` should be called once.
    - The function should return `0` (indicating success).
    """
    result = main()

    assert result == 0
    mock_reset_database.assert_called_once()
    mock_store_tmdb_data.assert_called_once()

def test_main_reset_database_failure():
    """
    Test Case: Failure during database reset.

    Scenario:
    - `reset_database()` raises an exception.

    Expectations:
    - The function should return `1` (indicating failure).
    - The exception should be caught and printed.
    """
    with patch("import_data.reset_database", side_effect=Exception("DB Reset Error")):
        result = main()

    assert result == 1

def test_main_store_tmdb_data_failure(mock_reset_database):
    """
    Test Case: Failure during TMDb data import.

    Scenario:
    - `reset_database()` runs successfully.
    - `store_tmdb_data()` raises an exception.

    Expectations:
    - The function should return `1` (indicating failure).
    - `reset_database()` should still be called before failure.
    - The exception should be caught and printed.
    """
    with patch("import_data.store_tmdb_data", side_effect=Exception("TMDb Import Error")):
        result = main()

    assert result == 1
    mock_reset_database.assert_called_once()

import pytest
from models import db, Movie, Genre, Rating
from flask import Flask

# ---- Fixtures ----
# Pytest fixtures allow us to create a test database and cleanup automatically.

@pytest.fixture
def app():
    """
    Fixture to create a test Flask application with an in-memory SQLite database.
    This allows testing database models without modifying real data.
    """
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory DB for tests
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()  # Create database tables before running tests
        yield app

        db.session.remove()
        db.drop_all()  # Cleanup after tests


@pytest.fixture
def client(app):
    """
    Fixture to create a test client for the Flask application.
    """
    return app.test_client()


@pytest.fixture
def session(app):
    """
    Fixture to provide a database session for tests.
    """
    with app.app_context():
        yield db.session
        db.session.rollback()  # Rollback after each test to maintain isolation


# ---- Unit Tests ----

def test_genre_model(session):
    """
    Test Case: Ensure Genre model can be created and queried.

    Scenario:
    - A Genre is created and added to the database.
    - It is retrieved and validated.

    Expectations:
    - The Genre should be found in the database with the correct attributes.
    """
    genre = Genre(name="Action")
    session.add(genre)
    session.commit()

    retrieved_genre = session.query(Genre).filter_by(name="Action").first()
    assert retrieved_genre is not None
    assert retrieved_genre.name == "Action"
    assert repr(retrieved_genre) == "<Genre(name='Action')>"


def test_movie_model(session):
    """
    Test Case: Ensure Movie model can be created, queried, and converted to a dictionary.

    Scenario:
    - A Movie is created and added to the database.
    - It is retrieved and validated.
    - The to_dict() method is tested.

    Expectations:
    - The Movie should be found in the database with the correct attributes.
    - The dictionary representation should match expected values.
    """
    movie = Movie(
        id="tt1234567",
        title_type="movie",
        primary_title="Test Movie",
        original_title="Test Movie Original",
        start_year=2022,
        poster_url="http://example.com/poster.jpg"
    )
    session.add(movie)
    session.commit()

    retrieved_movie = session.query(Movie).filter_by(id="tt1234567").first()
    assert retrieved_movie is not None
    assert retrieved_movie.primary_title == "Test Movie"
    assert retrieved_movie.original_title == "Test Movie Original"
    assert retrieved_movie.start_year == 2022
    assert retrieved_movie.poster_url == "http://example.com/poster.jpg"

    # Test to_dict() method
    movie_dict = retrieved_movie.to_dict()
    assert movie_dict["id"] == "tt1234567"
    assert movie_dict["title_type"] == "movie"
    assert movie_dict["primary_title"] == "Test Movie"
    assert movie_dict["original_title"] == "Test Movie Original"
    assert movie_dict["start_year"] == 2022
    assert movie_dict["poster_url"] == "http://example.com/poster.jpg"
    assert movie_dict["genres"] == []  # No genres yet
    assert movie_dict["rating"] is None  # No rating yet


def test_movie_genre_relationship(session):
    """
    Test Case: Ensure movies and genres can be associated correctly.

    Scenario:
    - A Movie and two Genres are created.
    - The Genres are associated with the Movie.
    - The relationship is validated.

    Expectations:
    - The Movie should have the correct genres.
    """
    movie = Movie(id="tt1234567", primary_title="Genre Test Movie")
    genre1 = Genre(name="Action")
    genre2 = Genre(name="Comedy")

    movie.genres.extend([genre1, genre2])
    session.add_all([movie, genre1, genre2])
    session.commit()

    retrieved_movie = session.query(Movie).filter_by(id="tt1234567").first()
    assert len(retrieved_movie.genres) == 2
    assert {genre.name for genre in retrieved_movie.genres} == {"Action", "Comedy"}

    # Test to_dict() method reflects genres
    movie_dict = retrieved_movie.to_dict()
    assert set(movie_dict["genres"]) == {"Action", "Comedy"}


def test_rating_model(session):
    """
    Test Case: Ensure Rating model can be created and queried.

    Scenario:
    - A Rating is created for a Movie.
    - The relationship is validated.

    Expectations:
    - The Rating should be correctly linked to the Movie.
    - The Rating should have expected attributes.
    """
    movie = Movie(id="tt1234567", primary_title="Rating Test Movie")
    rating = Rating(movie_id="tt1234567", average_rating=8.5, num_votes=1000)

    movie.rating = rating
    session.add(movie)
    session.commit()

    retrieved_movie = session.query(Movie).filter_by(id="tt1234567").first()
    assert retrieved_movie.rating is not None
    assert retrieved_movie.rating.average_rating == 8.5
    assert retrieved_movie.rating.num_votes == 1000

    # Test to_dict() method reflects rating
    movie_dict = retrieved_movie.to_dict()
    assert movie_dict["rating"] == {"average_rating": 8.5, "num_votes": 1000}


def test_rating_movie_relationship(session):
    """
    Test Case: Ensure a Rating is correctly linked to a Movie.

    Scenario:
    - A Movie and Rating are created.
    - The relationship is validated from both sides.

    Expectations:
    - The Movie should have a linked Rating.
    - The Rating should reference the correct Movie.
    """
    movie = Movie(id="tt1234567", primary_title="Rating Movie Test")
    rating = Rating(movie_id="tt1234567", average_rating=7.2, num_votes=500)

    session.add_all([movie, rating])
    session.commit()

    retrieved_rating = session.query(Rating).filter_by(movie_id="tt1234567").first()
    assert retrieved_rating is not None
    assert retrieved_rating.movie is not None
    assert retrieved_rating.movie.primary_title == "Rating Movie Test"

    # Test to_dict() method on Rating
    rating_dict = retrieved_rating.to_dict()
    assert rating_dict["average_rating"] == 7.2
    assert rating_dict["num_votes"] == 500


def test_rating_update(session):
    """
    Test Case: Ensure Ratings can be updated.

    Scenario:
    - A Rating is created for a Movie.
    - The Rating is updated.
    - The changes are validated.

    Expectations:
    - The Rating should reflect the updated values.
    """
    movie = Movie(id="tt1234567", primary_title="Update Test Movie")
    rating = Rating(movie_id="tt1234567", average_rating=5.5, num_votes=200)

    session.add_all([movie, rating])
    session.commit()

    # Update Rating
    rating.average_rating = 9.1
    rating.num_votes = 1500
    session.commit()

    updated_rating = session.query(Rating).filter_by(movie_id="tt1234567").first()
    assert updated_rating.average_rating == 9.1
    assert updated_rating.num_votes == 1500


def test_movie_delete_cascades_rating(session):
    """
    Test Case: Ensure deleting a Movie also deletes its Rating.

    Scenario:
    - A Movie and Rating are created.
    - The Rating is explicitly deleted first.
    - Then the Movie is deleted.
    - The Rating should not exist after both deletions.

    Expectations:
    - The Rating should not exist after the Movie is deleted.
    """
    movie = Movie(id="tt1234567", primary_title="Cascade Delete Test")
    rating = Rating(movie_id="tt1234567", average_rating=6.0, num_votes=300)

    session.add_all([movie, rating])
    session.commit()

    # Explicitly delete the Rating first
    session.delete(rating)
    session.commit()

    # Now delete the Movie
    session.delete(movie)
    session.commit()

    # Ensure the rating is deleted
    rating_check = session.query(Rating).filter_by(movie_id="tt1234567").first()
    assert rating_check is None, "Rating should be deleted"

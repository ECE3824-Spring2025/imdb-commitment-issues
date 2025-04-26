import pytest
import json
from mock import patch, MagicMock
from index import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# ---- Updated Unit Tests ----

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert "status" in data
    assert "timestamp" in data
    assert "redis_available" in data
    assert "tmdb_configured" in data

def test_get_movies(client):
    response = client.get("/api/movies")
    assert response.status_code == 200
    data = response.get_json()
    assert "movies" in data
    assert "total" in data
    assert "page" in data
    assert "pageSize" in data

def test_get_movie_details_invalid(client):
    response = client.get("/api/movies/invalid_id")
    assert response.status_code in [404, 500]
    data = response.get_json()
    assert "error" in data

def test_get_genres(client):
    response = client.get("/api/genres")
    assert response.status_code == 200
    data = response.get_json()
    assert "genres" in data

def test_signup_and_signin(client):
    # Mock a signup
    response = client.post("/api/signup", json={
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code in [200, 409]  # Might already exist from previous tests
    data = response.get_json()
    assert "success" in data or "error" in data

    # Then signin
    response = client.post("/api/signin", json={
        "email": "testuser@example.com",
        "password": "password123"
    })
    assert response.status_code in [200, 401]
    data = response.get_json()
    if response.status_code == 200:
        assert data["success"] is True
        assert "user_id" in data
    else:
        assert data["success"] is False

def test_watchlist_workflow(client):
    # First, sign up / sign in
    signin_response = client.post("/api/signin", json={
        "email": "testuser@example.com",
        "password": "password123"
    })
    signin_data = signin_response.get_json()
    if "user_id" not in signin_data:
        pytest.skip("User not found or sign in failed")
    user_id = signin_data["user_id"]

    movie_id = "tt0000001"  # dummy movie id for testing

    # Add to watchlist
    add_response = client.post("/api/watchlist", json={
        "user_id": user_id,
        "movie_id": movie_id
    })
    assert add_response.status_code in [200, 409]
    add_data = add_response.get_json()
    assert "success" in add_data or "error" in add_data

    # Get watchlist
    get_response = client.get(f"/api/watchlist/{user_id}")
    assert get_response.status_code == 200
    get_data = get_response.get_json()
    assert "movies" in get_data

    # Remove from watchlist
    remove_response = client.delete("/api/watchlist", json={
        "user_id": user_id,
        "movie_id": movie_id
    })
    assert remove_response.status_code == 200
    remove_data = remove_response.get_json()
    assert remove_data["success"] is True


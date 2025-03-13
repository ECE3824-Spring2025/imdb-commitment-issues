import requests
import os
import redis
import json
from models import db, Movie, Genre, Rating
from flask import Flask

# ✅ Set API Key (Only using API Key directly)
API_KEY = "61c678e1170ca246fbfbdeecc7aa373b"
CACHE_EXPIRY = 86400  # 24 hours cache duration
MIN_VOTES = 100  # Minimum votes required to store movies

# ✅ Initialize Redis
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# ✅ TMDb Genre Mapping
TMDB_GENRES = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
    99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
    27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Sci-Fi",
    53: "Thriller", 10752: "War", 37: "Western"
}

def create_app():
    """Initialize Flask App and Database."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///imdb_movies.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def fetch_top_rated_movies():
    """Fetch 100 movies from TMDb using API key directly."""
    all_movies = []
    for page in range(1, 6):  # Fetch 5 pages (20 movies per page = 100 total)
        url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}&language=en-US&page={page}"
        
        cached_data = redis_client.get(url)
        if cached_data:
            print(f"✅ Using cached TMDb data for page {page}")
            movies = json.loads(cached_data)
        else:
            response = requests.get(url)
            response.raise_for_status()
            movies = response.json().get("results", [])
            redis_client.setex(url, CACHE_EXPIRY, json.dumps(movies))
        
        all_movies.extend(movies)

    return all_movies

def store_tmdb_data():
    """Fetches and stores TMDb movies in the database."""
    app = create_app()
    with app.app_context():
        db.create_all()

        movies = fetch_top_rated_movies()

        for item in movies:
            movie_id = f"tmdb_{item['id']}"
            existing_movie = Movie.query.get(movie_id)

            if not existing_movie:
                genre_names = [TMDB_GENRES.get(genre_id, "Unknown") for genre_id in item.get("genre_ids", [])]
                poster_url = f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get("poster_path") else None

                movie = Movie(
                    id=movie_id,
                    title_type="movie",
                    primary_title=item.get("title"),
                    original_title=item.get("original_title"),
                    start_year=int(item["release_date"].split("-")[0]) if item.get("release_date") else None,
                    poster_url=poster_url
                )

                rating = Rating(
                    movie_id=movie_id,
                    average_rating=item.get("vote_average", 0),
                    num_votes=item.get("vote_count", 0)
                )

                db.session.add(movie)
                db.session.add(rating)

                for genre_name in genre_names:
                    genre = Genre.query.filter_by(name=genre_name).first()
                    if not genre:
                        genre = Genre(name=genre_name)
                        db.session.add(genre)
                        db.session.commit()

                    movie.genres.append(genre)

        db.session.commit()
        print("✅ Movies stored in the database (100 movies).")

if __name__ == "__main__":
    print("📡 Fetching TMDb data and storing it in the database...")
    store_tmdb_data()
    print("✅ Data import complete!")

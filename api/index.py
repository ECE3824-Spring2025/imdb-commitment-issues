from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sqlite3
import time
import functools
import json
from contextlib import contextmanager

# TMDB API configuration
TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '')  # Set this environment variable
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Try importing Redis but don't fail if not available
try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure database path
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(os.path.dirname(current_dir), 'src', 'database', 'instance', 'imdb_movies.db')
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# In-memory cache
memory_cache = {}

# Redis setup
redis_client = None
if HAS_REDIS:
    try:
        redis_client = redis.Redis(
            host='localhost', 
            port=6379, 
            db=0, 
            decode_responses=True, 
            socket_connect_timeout=3
        )
        redis_client.ping()
        print("Redis connected successfully")
    except Exception as e:
        print(f"Redis connection failed: {e}. Falling back to in-memory caching.")
        redis_client = None

# Cache decorator with Redis/memory fallback
def cached(timeout=300):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            current_time = time.time()
            # Try Redis first if available
            if redis_client:
                try:
                    cached_data = redis_client.get(cache_key)
                    if cached_data:
                        print(f"Redis cache hit for {cache_key}")
                        return json.loads(cached_data)
                    # No cache hit, execute function
                    result = func(*args, **kwargs)
                    redis_client.setex(
                        cache_key,
                        timeout,
                        json.dumps(result, default=str)
                    )
                    return result
                except Exception as e:
                    print(f"Redis error: {e}. Falling back to memory cache.")
            # Memory cache fallback
            if cache_key in memory_cache:
                result, timestamp = memory_cache[cache_key]
                if current_time - timestamp < timeout:
                    print(f"Memory cache hit for {cache_key}")
                    return result
            # Execute and cache in memory
            result = func(*args, **kwargs)
            memory_cache[cache_key] = (result, current_time)
            return result
        return wrapper
    return decorator

# Database connection context manager for safer handling
@contextmanager
def db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Performance optimizations
    cursor = conn.cursor()
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.execute("PRAGMA temp_store = MEMORY")
    cursor.execute("PRAGMA cache_size = 10000")
    try:
        yield conn
    finally:
        conn.close()

# New function to search TMDb for movie details
@cached(timeout=86400)  # Cache for 24 hours
def search_tmdb_movie(title, year=None):
    if not TMDB_API_KEY:
        print("Warning: TMDB_API_KEY not set")
        return None
    params = {
        'api_key': TMDB_API_KEY,
        'query': title,
        'include_adult': 'false',
        'language': 'en-US',
        'page': 1
    }
    if year:
        params['year'] = year
    try:
        response = request.get(f"{TMDB_BASE_URL}/search/movie", params=params)
        data = response.json()
        if response.status_code == 200 and data.get('results') and len(data['results']) > 0:
            return data['results'][0]
        return None
    except Exception as e:
        print(f"TMDb API error: {e}")
        return None

# Add TMDb image info to movie details
@app.route('/api/movies/<movie_id>/images', methods=['GET'])
@cached(timeout=86400)  # Cache for 24 hours since images rarely change
def get_movie_images(movie_id):
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            # Get basic movie info
            cursor.execute("SELECT primary_title, start_year FROM movies WHERE id = ?", (movie_id,))
            movie = cursor.fetchone()
            if not movie:
                return jsonify({'error': 'Movie not found'}), 404
            # Search TMDb for the movie
            tmdb_movie = search_tmdb_movie(movie['primary_title'], movie.get('start_year'))
            if not tmdb_movie:
                return jsonify({
                    'message': 'No TMDb match found',
                    'images': {
                        'poster_path': None,
                        'backdrop_path': None
                    }
                })
            # Construct full image URLs
            poster_path = tmdb_movie.get('poster_path')
            backdrop_path = tmdb_movie.get('backdrop_path')
            images = {
                'tmdb_id': tmdb_movie.get('id'),
                'poster_url': f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None,
                'backdrop_url': f"{TMDB_IMAGE_BASE_URL}{backdrop_path}" if backdrop_path else None,
                'poster_path': poster_path,
                'backdrop_path': backdrop_path
            }
            return jsonify({
                'images': images,
                'tmdb_data': {
                    'title': tmdb_movie.get('title'),
                    'original_title': tmdb_movie.get('original_title'),
                    'release_date': tmdb_movie.get('release_date'),
                    'popularity': tmdb_movie.get('popularity'),
                    'vote_average': tmdb_movie.get('vote_average'),
                    'overview': tmdb_movie.get('overview')
                }
            })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': f'Failed to retrieve images for movie with ID {movie_id}'
        }), 500

# Add a new endpoint to get images with different sizes
@app.route('/api/movies/<movie_id>/poster', methods=['GET'])
@cached(timeout=86400)
def get_movie_poster(movie_id):
    size = request.args.get('size', 'w500')  # Default size is w500
    # Validate size parameter (TMDb supported sizes)
    valid_sizes = ['w92', 'w154', 'w185', 'w342', 'w500', 'w780', 'original']
    if size not in valid_sizes:
        size = 'w500'  # Default to w500 if invalid size
    try:
        # Get image data from our existing endpoint
        image_data = get_movie_images(movie_id)
        if isinstance(image_data, tuple):  # Error response
            return image_data
        data = json.loads(image_data.data)
        poster_path = data.get('images', {}).get('poster_path')
        if not poster_path:
            return jsonify({
                'message': 'No poster found for this movie',
                'posterUrl': None
            })
        # Construct URL with requested size
        poster_url = f"https://image.tmdb.org/t/p/{size}{poster_path}"
        return jsonify({
            'posterUrl': poster_url,
            'size': size
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': f'Failed to retrieve poster for movie with ID {movie_id}'
        }), 500
        
@app.route('/api/movies', methods=['GET'])
@cached(timeout=60)  # Cache results for 1 minute
def get_movies():
    try:
        start_time = time.time()
        # Get parameters from request for pagination
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 100, type=int)
        with db_connection() as conn:
            cursor = conn.cursor()
            # Get total count efficiently
            cursor.execute("SELECT COUNT(*) FROM movies")
            total_count = cursor.fetchone()[0]
            # Calculate offset for pagination
            offset = (page - 1) * page_size
            # Query with all needed data in one go
            query = """
                SELECT 
                    m.id, 
                    m.primary_title, 
                    m.title_type,
                    r.average_rating,
                    r.num_votes,
                    GROUP_CONCAT(g.name) as genres
                FROM 
                    movies m
                LEFT JOIN 
                    ratings r ON m.id = r.movie_id
                LEFT JOIN 
                    movie_genre mg ON m.id = mg.movie_id
                LEFT JOIN 
                    genres g ON mg.genre_id = g.id
                GROUP BY 
                    m.id
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (page_size, offset))
            # Process results
            movies = []
            for row in cursor.fetchall():
                # Parse genres from GROUP_CONCAT result
                genres = row['genres'].split(',') if row['genres'] else []
                movies.append({
                    'id': row['id'],
                    'primary_title': row['primary_title'],
                    'title_type': row['title_type'],
                    'rating': {
                        'average_rating': row['average_rating'] or 0,
                        'num_votes': row['num_votes'] or 0
                    },
                    'genres': genres
                })
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        # Return response
        return jsonify({
            'movies': movies,
            'total': total_count,
            'page': page,
            'pageSize': page_size,
            'pages': (total_count + page_size - 1) // page_size,
            'query_time_ms': round(elapsed_time * 1000, 2),
            'cache_type': 'redis' if redis_client else 'memory'
        })
    except Exception as e:
        print(f"Error in get_movies: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to retrieve movies',
            'movies': []
        }), 500
        
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'timestamp': time.time(),
        'redis_available': redis_client is not None,
        'db_exists': os.path.exists(db_path),
        'tmdb_configured': bool(TMDB_API_KEY)
    })

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    try:
        # Get pattern from request
        pattern = '*'
        if request.is_json:
            pattern = request.json.get('pattern', '*')
        else:
            pattern = request.form.get('pattern', '*')
        # Clear Redis cache if available
        cleared_count = 0
        cache_type = 'memory'
        if redis_client:
            try:
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
                cleared_count = len(keys)
                cache_type = 'redis'
            except Exception as e:
                print(f"Redis error during cache clear: {e}. Falling back to memory cache clear.")
        # Clear memory cache if Redis failed or not available
        if cache_type == 'memory':
            before_count = len(memory_cache)
            if pattern == '*':
                memory_cache.clear()
                cleared_count = before_count
            else:
                import re
                pattern_regex = re.compile(pattern.replace('*', '.*'))
                keys_to_remove = [k for k in memory_cache.keys() if pattern_regex.match(k)]
                for k in keys_to_remove:
                    del memory_cache[k]
                cleared_count = len(keys_to_remove)
        return jsonify({
            'success': True,
            'message': f'Cleared {cleared_count} {cache_type} cache keys matching pattern "{pattern}"',
            'cache_type': cache_type
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to clear cache'
        }), 500

@app.route('/api/movies/<movie_id>', methods=['GET'])
def get_movie_details(movie_id):  # 🚨 REMOVE @cached(timeout=300)
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.*, r.average_rating, r.num_votes, 
                GROUP_CONCAT(g.name) as genres_list
                FROM movies m
                LEFT JOIN ratings r ON m.id = r.movie_id
                LEFT JOIN movie_genre mg ON m.id = mg.movie_id
                LEFT JOIN genres g ON mg.genre_id = g.id
                WHERE m.id = ?
                GROUP BY m.id
            """, (movie_id,))

            movie = cursor.fetchone()
            if not movie:
                return jsonify({'error': 'Movie not found'}), 404  # 🚨 Ensure 404 isn't cached

            # Convert to dictionary
            movie_dict = dict(movie)
            movie_dict['genres'] = movie_dict.get('genres_list', '').split(',') if movie_dict.get('genres_list') else []
            if 'genres_list' in movie_dict:
                del movie_dict['genres_list']

            movie_dict['rating'] = {
                'average_rating': movie_dict.pop('average_rating', 0) or 0,
                'num_votes': movie_dict.pop('num_votes', 0) or 0
            }

        return jsonify(movie_dict)

    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': f'Failed to retrieve movie with ID {movie_id}'
        }), 500


@app.route('/api/genres', methods=['GET'])
@cached(timeout=3600)  # Cache for 1 hour since genres don't change often
def get_genres():
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            # Fetch all genres with movie counts
            query = """
                SELECT 
                    g.id,
                    g.name,
                    COUNT(mg.movie_id) as movie_count
                FROM 
                    genres g
                LEFT JOIN 
                    movie_genre mg ON g.id = mg.genre_id
                GROUP BY 
                    g.id
                ORDER BY 
                    movie_count DESC
            """
            cursor.execute(query)
            genres = [{
                'id': row['id'],
                'name': row['name'],
                'count': row['movie_count']
            } for row in cursor.fetchall()]

        return jsonify({
            'genres': genres,
            'total': len(genres)
        })

    except Exception as e:
        print(f"Error in get_genres: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to retrieve genres',
            'genres': []
        }), 500

if __name__ == '__main__':
    print(f"Starting server on port 8000")
    print(f"API will be available at http://localhost:8000/api/")
    app.run(debug=True, host='0.0.0.0', port=8000)
from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS
import os
import time
import functools
import json
import sys
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Allow imports from /src/database/models.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'database')))
from models import db, Movie, Genre, Rating, User, Watchlist

# TMDb setup
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Redis (optional)
try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Connect to AWS RDS MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', '')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'public', 'uploads'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

memory_cache = {}
redis_client = None
if HAS_REDIS:
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, socket_connect_timeout=3)
        redis_client.ping()
    except Exception:
        redis_client = None

# --- Caching decorator ---
def cached(timeout=300):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            if redis_client:
                try:
                    cached = redis_client.get(cache_key)
                    if cached:
                        return jsonify(json.loads(cached))
                    result = func(*args, **kwargs)
                    if isinstance(result, Response):
                        return result
                    redis_client.setex(cache_key, timeout, json.dumps(result, default=str))
                    return jsonify(result)
                except Exception:
                    pass
            if cache_key in memory_cache:
                result, timestamp = memory_cache[cache_key]
                if time.time() - timestamp < timeout:
                    return jsonify(result)
            result = func(*args, **kwargs)
            if isinstance(result, Response):
                return result
            memory_cache[cache_key] = (result, time.time())
            return jsonify(result)
        return wrapper
    return decorator

# --- API Routes ---

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'timestamp': time.time(),
        'redis_available': redis_client is not None,
        'tmdb_configured': bool(TMDB_API_KEY)
    })

@app.route('/api/movies', methods=['GET'])
@cached(timeout=60)
def get_movies():
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 100, type=int)
        movies_query = Movie.query.paginate(page=page, per_page=page_size, error_out=False)
        movies = [movie.to_dict() for movie in movies_query.items]
        return {
            'movies': movies,
            'total': movies_query.total,
            'page': page,
            'pageSize': page_size,
            'pages': movies_query.pages
        }
    except Exception as e:
        return {
            'error': str(e),
            'message': 'Failed to retrieve movies',
            'movies': []
        }

@app.route('/api/movies/<movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    try:
        movie = db.session.get(Movie, movie_id)
        if not movie:
            return jsonify({'error': 'Movie not found'}), 404
        return movie.to_dict()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/genres', methods=['GET'])
@cached(timeout=3600)
def get_genres():
    try:
        genres = Genre.query.all()
        return jsonify({
            'genres': [{'id': genre.id, 'name': genre.name, 'count': len(genre.movies)} for genre in genres]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()

        email = data.get('email', '').strip().lower()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not email or not username or not password:
            return jsonify({'error': 'Missing required fields'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400

        if User.query.filter((User.email == email) | (User.username == username)).first():
            return jsonify({'error': 'Email or username already exists'}), 409

        new_user = User(email=email, username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'success': True}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signin', methods=['POST'])
def signin():
    try:
        data = request.get_json()

        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({'error': 'Missing email or password'}), 400

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return jsonify({
                'success': True,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'profile_image': user.profile_image
            })
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/watchlist', methods=['POST'])
def add_to_watchlist():
    try:
        data = request.get_json()
        if Watchlist.query.filter_by(user_id=data['user_id'], movie_id=data['movie_id']).first():
            return jsonify({'error': 'Already in watchlist'}), 409

        entry = Watchlist(user_id=data['user_id'], movie_id=data['movie_id'])
        db.session.add(entry)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/watchlist/<int:user_id>', methods=['GET'])
def get_watchlist(user_id):
    try:
        entries = Watchlist.query.filter_by(user_id=user_id).all()
        return jsonify({'movies': [entry.movie_id for entry in entries]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/watchlist', methods=['DELETE'])
def remove_from_watchlist():
    try:
        data = request.get_json()
        entry = Watchlist.query.filter_by(user_id=data['user_id'], movie_id=data['movie_id']).first()
        if entry:
            db.session.delete(entry)
            db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload_profile_image/<int:user_id>', methods=['POST'])
def upload_profile_image(user_id):
    try:
        file = request.files['image']
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        user = User.query.get(user_id)
        if user:
            user.profile_image = f"uploads/{filename}"
            db.session.commit()

        return jsonify({'success': True, 'profile_image': f"uploads/{filename}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

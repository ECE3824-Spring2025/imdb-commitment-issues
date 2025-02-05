from flask import jsonify, Blueprint, render_template, request 
from controllers.movie_controller import get_movies_by_genre_and_sort

# Create a Blueprint for movie-related routes
movie_bp = Blueprint('movie_bp', __name__)

@movie_bp.route('/')
def home():
  return render_template('index.html')

@movie_bp.route('/movies', methods=['GET'])
def get_movies():
  genre = request.args.get('genre')
  sort_by = request.args.get('sortBy')

  movies = get_movies_by_genre_and_sort(genre, sort_by)

  if movies is None:
    return jsonify({"error": "Invalid genre or sort criteria"})
  
  movie_list = [{
    'id': movie.id,
    'name': movie.title,
    'rating': movie.rating,
    'votes': movie.votes
  } for movie in movies]

  return jsonify(movie_list)

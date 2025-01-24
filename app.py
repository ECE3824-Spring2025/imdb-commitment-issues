import json
from flask import Flask, jsonify, request, render_template
from movie_data import ListWithRatingDrama, ListWithRatingAction, ListWithRatingComedy, ListWithLikesDrama, ListWithLikesAction, ListWithLikesComedy
import imdb

app = Flask(__name__)

FAVORITES_FILE = 'favorites.json'

def load_favorites():
    """Load favorites from the JSON file."""
    try:
        with open(FAVORITES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_favorites(favorites):
    """Save favorites to the JSON file."""
    with open(FAVORITES_FILE, 'w') as f:
        json.dump(favorites, f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/movies', methods=['GET'])
def get_movies():
    genre = request.args.get('genre')
    sort_by = request.args.get('sortBy')

    if genre == 'drama':
        movies = ListWithRatingDrama
        votes = ListWithLikesDrama
    elif genre == 'action':
        movies = ListWithRatingAction
        votes = ListWithLikesAction
    elif genre == 'comedy':
        movies = ListWithRatingComedy
        votes = ListWithLikesComedy
    else:
        return jsonify({"error": "Invalid genre"}), 400

    for i, movie in enumerate(movies):
        movie['votes'] = votes[i]['votes']

    if sort_by == 'score':
        movies = sorted(movies, key=lambda x: x['rating'], reverse=True)
    elif sort_by == 'votes':
        # Ensure `votes` field is properly parsed into integers
        movies = sorted(movies, key=lambda x: int(x['votes'].replace('M', '000000').replace('K', '000').replace('.', '')), reverse=True)
    else:
        return jsonify({"error": "Invalid sort criteria"}), 400

    return jsonify(movies[:10])


@app.route('/favorites', methods=['GET', 'POST', 'DELETE'])
def manage_favorites():
    if request.method == 'GET':
        return jsonify(load_favorites())

    if request.method == 'POST':
        movie = request.json
        favorites = load_favorites()
        if movie not in favorites:
            favorites.append(movie)
            save_favorites(favorites)
        return jsonify(favorites)

    if request.method == 'DELETE':
        movie_id = request.json.get('id')
        favorites = load_favorites()
        favorites = [fav for fav in favorites if fav['id'] != movie_id]
        save_favorites(favorites)
        return jsonify(favorites)

if __name__ == '__main__':
    app.run(debug=True)

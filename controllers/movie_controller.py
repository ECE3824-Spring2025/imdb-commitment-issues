from models.movie import Movie
from models import db

def get_movies_by_genre_and_sort(genre, sort_by):
    """Fetches movies from the database based on genre and sorting"""
    if genre not in ['action', 'comedy', 'drama']:
        return None
    
    query = Movie.query.filter_by(genre=genre)

    if sort_by == 'score':
        query = query.filter(Movie.rating.isnot(None))
        query = query.order_by(Movie.rating.desc())

        return query.limit(10).all()

    elif sort_by == 'votes':
        query = query.filter(Movie.votes.isnot(None))
        movies = query.all()

        # Apply manual sorting since votes are stored as strings like "1.7M"
        movies = sorted(
            movies,
            key=lambda x: int(str(x.votes).replace('M', '000000').replace('K', '000').replace('.', '')),
            reverse=True
        )

        return movies[:10]

    else:
        return None
    
def get_all_movies():
    """Returns all movies in the database."""
    return Movie.query.all()

def get_movie_by_id(movie_id):
    """Fetches a single movie by ID"""
    return Movie.query.get(movie_id)
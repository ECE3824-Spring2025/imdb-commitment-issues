import pandas as pd
import sys
from pathlib import Path
import time

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

from models import db, Movie, Genre, Rating
from flask import Flask

def create_app():
    app = Flask(__name__)
    # Use SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///imdb_movies.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def filter_media(basics_file, ratings_file, output_file=None, min_rating=5.0, min_votes=1000, store_db=True):
    """
    Filters IMDb datasets for top 100 movies and top 100 TV shows by number of votes.
    
    Args:
        basics_file (str): Path to title.basics.tsv
        ratings_file (str): Path to title.ratings.tsv
        output_file (str, optional): Path to save filtered results (CSV)
        min_rating (float): Minimum rating threshold
        min_votes (int): Minimum number of votes required
        store_db (bool): Whether to store filtered results in the database
    """
    start_time = time.time()
    print(f"Loading data files...")
    
    # Load title.basics.tsv with proper handling of IMDb's null values
    df_basics = pd.read_csv(
        basics_file, 
        sep='\t',
        na_values=['\\N'],
        dtype={
            'tconst': str,
            'titleType': str,
            'primaryTitle': str,
            'originalTitle': str,
            'isAdult': object,
            'startYear': object,
            'endYear': object,
            'runtimeMinutes': object,
            'genres': str
        }
    )
    
    # Load title.ratings.tsv
    df_ratings = pd.read_csv(
        ratings_file,
        sep='\t',
        na_values=['\\N'],
        dtype={
            'tconst': str,
            'averageRating': float,
            'numVotes': int
        }
    )
    
    # Convert numeric columns properly
    df_basics['startYear'] = pd.to_numeric(df_basics['startYear'], errors='coerce')
    df_basics['endYear'] = pd.to_numeric(df_basics['endYear'], errors='coerce')
    df_basics['runtimeMinutes'] = pd.to_numeric(df_basics['runtimeMinutes'], errors='coerce')
    df_basics['isAdult'] = df_basics['isAdult'].fillna(0).astype(int).astype(bool)
    
    print(f"Files loaded. Filtering data...")
    
    # Filter to only keep movies and TV series
    media_filter = df_basics['titleType'].isin(['movie', 'tvSeries'])
    filtered_basics = df_basics[media_filter].copy()
    
    # Merge with ratings data
    merged_data = pd.merge(filtered_basics, df_ratings, on='tconst', how='inner')
    
    # Apply rating filter but keep min_votes filter just as a baseline
    quality_filter = (merged_data['averageRating'] >= min_rating) & (merged_data['numVotes'] >= min_votes)
    filtered_data = merged_data[quality_filter].copy()
    
    # Split data into movies and TV series
    movies_data = filtered_data[filtered_data['titleType'] == 'movie'].copy()
    tvseries_data = filtered_data[filtered_data['titleType'] == 'tvSeries'].copy()
    
    # Sort by number of votes (highest first)
    movies_data = movies_data.sort_values('numVotes', ascending=False)
    tvseries_data = tvseries_data.sort_values('numVotes', ascending=False)
    
    # Get top 100 movies and top 100 TV series
    top_movies = movies_data.head(100)
    top_tvseries = tvseries_data.head(100)
    
    # Combine the results
    output_data = pd.concat([top_movies, top_tvseries])
    
    # Create a more readable output with selected columns
    output_data = output_data[[
        'tconst', 'titleType', 'primaryTitle', 'originalTitle', 'isAdult', 'startYear', 'endYear', 
        'runtimeMinutes', 'genres', 'averageRating', 'numVotes'
    ]].copy()
    
    # Save the filtered data to CSV
    if output_file:
        output_data.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")
    else:
        # Always save to filtered_data.csv as requested
        output_data.to_csv('./data/filtered_data.csv', index=False)
        print(f"Results saved to ./data/filtered_data.csv")
    
    # Print some stats
    movie_count = len(output_data[output_data['titleType'] == 'movie'])
    series_count = len(output_data[output_data['titleType'] == 'tvSeries'])
    
    print(f"Filtering complete!")
    print(f"Selected top {movie_count} movies and top {series_count} TV series by number of votes")
    
    # Store in database if requested
    if store_db:
        print("Storing filtered data in database...")
        store_filtered_data_in_db(output_data)
    
    # Return counts for potential further use
    return {
        'total': len(output_data),
        'movies': movie_count,
        'series': series_count
    }

def store_filtered_data_in_db(df, batch_size=1000):
    """
    Stores the filtered data in the database.
    
    Args:
        df (DataFrame): Pandas DataFrame with the filtered data
        batch_size (int): Number of records to insert in a batch
    """
    start_time = time.time()
    
    # Create Flask app context for database operations
    app = create_app()
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        
        # Extract unique genres and create a mapping
        print("Processing genres...")
        all_genres = set()
        for genres_str in df['genres'].dropna():
            all_genres.update(genres_str.split(','))
        
        # Add genres to the database
        for genre_name in all_genres:
            genre = Genre.query.filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                db.session.add(genre)
        db.session.commit()
        
        # Fetch all genres to use for movies
        all_db_genres = {genre.name: genre for genre in Genre.query.all()}
        
        # Process movies and ratings in batches
        print(f"Processing movies and ratings in batches of {batch_size}...")
        total_records = len(df)
        num_batches = (total_records + batch_size - 1) // batch_size
        
        movies_added = 0
        movies_updated = 0
        
        for batch in range(num_batches):
            start_idx = batch * batch_size
            end_idx = min((batch + 1) * batch_size, total_records)
            
            batch_data = df.iloc[start_idx:end_idx]
            
            for _, row in batch_data.iterrows():
                # Check if movie already exists
                existing_movie = Movie.query.get(row['tconst'])
                
                if existing_movie:
                    # Update the existing movie
                    existing_movie.title_type = row['titleType']
                    existing_movie.primary_title = row['primaryTitle']
                    existing_movie.original_title = row['originalTitle']
                    existing_movie.is_adult = row['isAdult']
                    existing_movie.start_year = row['startYear'] if pd.notna(row['startYear']) else None
                    existing_movie.end_year = row['endYear'] if pd.notna(row['endYear']) else None
                    existing_movie.runtime_minutes = row['runtimeMinutes'] if pd.notna(row['runtimeMinutes']) else None
                    
                    # Update genres - first clear existing ones
                    existing_movie.genres = []
                    
                    # Add new genres
                    if pd.notna(row['genres']):
                        movie_genres = row['genres'].split(',')
                        for genre_name in movie_genres:
                            if genre_name in all_db_genres:
                                existing_movie.genres.append(all_db_genres[genre_name])
                    
                    # Update rating if it exists
                    if existing_movie.rating:
                        existing_movie.rating.average_rating = row['averageRating']
                        existing_movie.rating.num_votes = row['numVotes']
                    else:
                        # Create new rating
                        rating = Rating(
                            movie_id=row['tconst'],
                            average_rating=row['averageRating'],
                            num_votes=row['numVotes']
                        )
                        db.session.add(rating)
                    
                    movies_updated += 1
                else:
                    # Create a new movie
                    movie = Movie(
                        id=row['tconst'],
                        title_type=row['titleType'],
                        primary_title=row['primaryTitle'],
                        original_title=row['originalTitle'],
                        is_adult=row['isAdult'],
                        start_year=row['startYear'] if pd.notna(row['startYear']) else None,
                        end_year=row['endYear'] if pd.notna(row['endYear']) else None,
                        runtime_minutes=row['runtimeMinutes'] if pd.notna(row['runtimeMinutes']) else None,
                    )
                    
                    # Add genres
                    if pd.notna(row['genres']):
                        movie_genres = row['genres'].split(',')
                        for genre_name in movie_genres:
                            if genre_name in all_db_genres:
                                movie.genres.append(all_db_genres[genre_name])
                    
                    db.session.add(movie)
                    
                    # Create rating
                    rating = Rating(
                        movie_id=row['tconst'],
                        average_rating=row['averageRating'],
                        num_votes=row['numVotes']
                    )
                    db.session.add(rating)
                    
                    movies_added += 1
            
            db.session.commit()
            print(f"Processed batch {batch+1}/{num_batches}, records {start_idx+1}-{end_idx}")
        
        end_time = time.time()
        print(f"Database import completed in {end_time - start_time:.2f} seconds")
        print(f"Movies added: {movies_added}, Movies updated: {movies_updated}")

def import_filtered_csv_to_db(csv_file, batch_size=1000):
    """
    Imports a previously filtered CSV file into the database.
    
    Args:
        csv_file (str): Path to the filtered CSV file
        batch_size (int): Number of records to insert in a batch
    """
    print(f"Loading filtered data from {csv_file}...")
    
    # Load the CSV file
    df = pd.read_csv(
        csv_file,
        dtype={
            'tconst': str,
            'titleType': str,
            'primaryTitle': str,
            'startYear': float,
            'endYear': float,
            'runtimeMinutes': float,
            'genres': str,
            'averageRating': float,
            'numVotes': int
        }
    )
    
    # If originalTitle is missing, add it from primaryTitle
    if 'originalTitle' not in df.columns:
        df['originalTitle'] = df['primaryTitle']
    
    # If isAdult is missing, set it to False
    if 'isAdult' not in df.columns:
        df['isAdult'] = False
    
    print(f"Loaded {len(df)} records from CSV. Storing in database...")
    store_filtered_data_in_db(df, batch_size)
    return len(df)

def main():
    # Get command line arguments or use defaults
    basics_file = "./data/title.basics.tsv"
    ratings_file = "./data/title.ratings.tsv"
    output_file = "./data/filtered_data.csv"
    
    # Run the filter process
    min_rating = 5.0
    min_votes = 1000
    
    if len(sys.argv) > 1 and sys.argv[1] != "--store-db":
        min_rating = float(sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2] != "--store-db":
        min_votes = int(sys.argv[2])
    
    # Check if we should store in database
    store_db = "--store-db" in sys.argv
    
    print(f"Starting media filter with min_rating={min_rating}, min_votes={min_votes}")
    stats = filter_media(basics_file, ratings_file, output_file, min_rating, min_votes, store_db)
    
    # Print summary
    print("\nSummary:")
    print(f"Total items: {stats['total']} (expected: 200)")
    print(f"Movies: {stats['movies']} (expected: 100)")
    print(f"TV Series: {stats['series']} (expected: 100)")

if __name__ == "__main__":
    main()
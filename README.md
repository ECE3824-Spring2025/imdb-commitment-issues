# IMDb Top 10 Movie Viewer

This project is a simple Flask-based web application that allows users to view the top 10 movies in different genres (Drama, Action, Comedy) sorted by IMDb score or the number of votes. Users can also add movies to their favorites list and manage them easily.

---

## Features
- Browse top 10 movies by genre.
- Sort movies by IMDb score or the number of votes.
- Add and remove movies from a personalized favorites list.
- Favorites are saved locally in a JSON file (`favorites.json`).

---

## Installation

### Prerequisites
Ensure you have the following installed on your system:
1. Python 3.7 or higher
2. pip (Python package manager)

### Required Python Libraries
- Flask

---

### Install Instructions
1. Clone this repository to your local machine:
    ```bash
    cd ~
    https://github.com/ECE3824-Spring2025/imdb-commitment-issues.git
    ```

2. Install the required dependencies:
    ```bash
    pip install flask imdb
    ```

---

## How to Run
1. Navigate to the project directory.
2. Start the Flask application:
    ```bash
    cd ~/imdb-commitment-issues
    python app.py
    ```

3. Open your web browser and go to:
    ```
    http://127.0.0.1:5000/
    ```

---

## Project Instructions
### Basic Usage
1. Select a **genre** from the dropdown (Drama, Action, or Comedy).
2. Select a **sorting option** (IMDb score or number of votes).
3. Browse the top 10 movies for the selected genre and sorting criteria.
4. Click the **Favorite** button to add a movie to your favorites.
5. Click the **Unfavorite** button to remove a movie from your favorites.

---

## Notes
- The favorites list is stored in `favorites.json`. Ensure this file is writable in the project directory.
- If you wish to pre-populate movie data, update the `movie_data.py` file with the desired movie lists.

---


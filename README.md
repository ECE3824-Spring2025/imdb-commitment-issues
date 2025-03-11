## Description
This project is a movie library webapp that allows users to view the top 100 movies and tv shows found in IMDb Non-Commerical Dataset. Users are able to search for a specific movie or tv show and favorite it. They also can sort by the IMDb score and number of votes and the choose which movie genres to display.

## Installation
### Prerequisites
- NPM: To run the client
- PIP: To install main dependencies
- WSL/MacOS/Linux: To run Redis server

### Steps
Clone the repository:
```
git clone https://github.com/ECE3824-Spring2025/imdb-commitment-issues.git
```

Create the environment
```
cd imdb-commitment-issues
python3 -m venv .venv
```

Activate the environment
```
. .venv/bin/activate
```

Install dependencies
```
npm install
pip install -r requirements.txt
```

Install Redis
```
sudo apt install redis-server
```

Activate Redis server
```
redis-server
```

Start the development server
```
npm run dev
```

Open browser and visit
```
http://localhost:3000/
```

## Project Instructions
### Basic Usage
1. Select a **format** (Movie/TV Show)
2. Select a **sorting option** (Most Popular/Top Rated/Favorited)
3. Select a **genre** from the dropdown
4. Browse the movie list
5. Click the **favorite** button to add movie to favorited or remove it from the list
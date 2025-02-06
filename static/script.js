document.addEventListener('DOMContentLoaded', () => {
    const genreSelect = document.getElementById('genre-select');
    const sortSelect = document.getElementById('sort-select');
    const movieTableBody = document.getElementById('movie-table-body');
    const scoreHeader = document.getElementById('score-header');
    const votesHeader = document.getElementById('votes-header');

    const API_KEY = '61c678e1170ca246fbfbdeecc7aa373b'; // TMDb API key
    const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'; // Adjust the size if needed

    const updateTable = async (movies, favoriteIds) => {
        movieTableBody.innerHTML = '';
        const sortBy = sortSelect.value;

        // Hide or show IMDb Score and Votes columns
        if (sortBy === "score") {
            scoreHeader.style.display = "table-cell";
            votesHeader.style.display = "none";
        } else if (sortBy === "votes") {
            scoreHeader.style.display = "none";
            votesHeader.style.display = "table-cell";
        }

        for (const [index, movie] of movies.entries()) {
            const posterPath = await fetchMoviePoster(movie.name);

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${movie.name}</td>
                <td><img src="${posterPath}" alt="${movie.name} Poster" width="50"></td> <!-- Poster Column -->
                <td class="score-column">${movie.rating || ''}</td>
                <td class="votes-column">${movie.votes || ''}</td>
                <td>
                    <button class="favorite-btn ${favoriteIds.has(movie.id) ? 'favorited' : ''}" 
                            data-id="${movie.id}">
                        ${favoriteIds.has(movie.id) ? '❤️' : '🤍'}
                    </button>
                </td>            
            `;

            // Hide/show values in each row based on sorting
            if (sortBy === "score") {
                row.querySelector('.score-column').style.display = "table-cell";
                row.querySelector('.votes-column').style.display = "none";
            } else if (sortBy === "votes") {
                row.querySelector('.score-column').style.display = "none";
                row.querySelector('.votes-column').style.display = "table-cell";
            }

            movieTableBody.appendChild(row);
        }

        document.querySelectorAll('.favorite-btn').forEach(button => {
            button.addEventListener('click', toggleFavorite);
        });

    };

    async function fetchMoviePoster(title) {
        try {
            const response = await fetch(`https://api.themoviedb.org/3/search/movie?api_key=${API_KEY}&query=${encodeURIComponent(title)}`);
            const data = await response.json();
            return data.results.length > 0 ? `${IMAGE_BASE_URL}${data.results[0].poster_path}` : 'placeholder.jpg';
        } catch (error) {
            console.error('Error fetching movie poster:', error);
            return 'placeholder.jpg';
        }
    }

    const fetchMovies = async () => {
        const genre = genreSelect.value;
        const sortBy = sortSelect.value;

        try {
         // Fetch movies and favorites in parallel
         const [moviesResponse, favoritesResponse] = await Promise.all([
            fetch(`/movies?genre=${genre}&sortBy=${sortBy}`),
            fetch(`/favorites`)
        ]);

        const movies = await moviesResponse.json();
        const favoriteMovies = await favoritesResponse.json();
        const favoriteIds = new Set(favoriteMovies.map(movie => movie.id));

        await updateTable(movies, favoriteIds);
        } catch (error) {
            console.error('Failed to fetch movies:', error);
        }
    };

    const toggleFavorite = async (event) => {
        const movieId = event.target.getAttribute('data-id');
        const isFavorited = event.target.classList.contains('favorited');
        const url = isFavorited ? `/unfavorite/${movieId}` : `/favorite/${movieId}`;
        const method = isFavorited ? 'DELETE' : 'POST';

        try {
            const response = await fetch(url, { method });

            // Check if the response is actually JSON
            const text = await response.text();
            try {
                const result = JSON.parse(text);
                if (response.ok) {
                    event.target.classList.toggle('favorited');
                    event.target.textContent = isFavorited ? '🤍' : '❤️';
                } else {
                    console.error('Failed:', result.message);
                }
            } catch (jsonError) {
                console.error('Server returned non-JSON:', text);
            }
        } catch (error) {
            console.error('Failed to update favorite:', error);
        }
    };

    genreSelect.addEventListener('change', fetchMovies);
    sortSelect.addEventListener('change', fetchMovies);

    fetchMovies();
});

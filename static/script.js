document.addEventListener('DOMContentLoaded', () => {
    const genreSelect = document.getElementById('genre-select');
    const sortSelect = document.getElementById('sort-select');
    const movieTableBody = document.getElementById('movie-table-body');

    const API_KEY = '61c678e1170ca246fbfbdeecc7aa373b'; // TMDb API key
    const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'; // Adjust the size if needed

    const loadFavorites = async () => {
        const response = await fetch('/favorites');
        return response.ok ? await response.json() : [];
    };

    const addFavorite = async (movie) => {
        await fetch('/favorites', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(movie),
        });
    };

    const removeFavorite = async (movieId) => {
        await fetch('/favorites', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: movieId }),
        });
    };

    const updateTable = async (movies) => {
        const favorites = await loadFavorites();
        movieTableBody.innerHTML = '';

        for (const [index, movie] of movies.entries()) {
            const isFavorite = favorites.some(fav => fav.id === movie.id);
            const posterPath = await fetchMoviePoster(movie.name);

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${movie.name}</td>
                <td><img src="${posterPath}" alt="${movie.name} Poster" width="50"></td> <!-- Poster Column -->
                <td>${movie.rating || ''}</td>
                <td>${movie.votes || ''}</td>
                <td>
                    <button class="favorite-btn" data-id="${movie.id}" data-name="${movie.name}" data-rating="${movie.rating}">
                        ${isFavorite ? 'Unfavorite' : 'Favorite'}
                    </button>
                </td>
            `;

            movieTableBody.appendChild(row);
        }

        document.querySelectorAll('.favorite-btn').forEach(button => {
            button.addEventListener('click', async (event) => {
                const button = event.target;
                const movie = {
                    id: button.dataset.id,
                    name: button.dataset.name,
                    rating: button.dataset.rating,
                };

                if (button.textContent === 'Favorite') {
                    await addFavorite(movie);
                    button.textContent = 'Unfavorite';
                } else {
                    await removeFavorite(movie.id);
                    button.textContent = 'Favorite';
                }
            });
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
            const response = await fetch(`/movies?genre=${genre}&sortBy=${sortBy}`);
            const movies = await response.json();
            await updateTable(movies);
        } catch (error) {
            console.error('Failed to fetch movies:', error);
        }
    };

    genreSelect.addEventListener('change', fetchMovies);
    sortSelect.addEventListener('change', fetchMovies);

    fetchMovies();
    pass
});

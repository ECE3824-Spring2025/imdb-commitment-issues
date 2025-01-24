document.addEventListener('DOMContentLoaded', () => {
    const genreSelect = document.getElementById('genre-select');
    const sortSelect = document.getElementById('sort-select');
    const movieTableBody = document.getElementById('movie-table-body');

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
        movies.forEach((movie, index) => {
            const isFavorite = favorites.some(fav => fav.id === movie.id);
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${movie.name}</td>
                <td>${movie.rating || ''}</td>
                <td>${movie.votes || ''}</td>
                <td>
                    <button class="favorite-btn" data-id="${movie.id}" data-name="${movie.name}" data-rating="${movie.rating}">
                        ${isFavorite ? 'Unfavorite' : 'Favorite'}
                    </button>
                </td>
            `;

            movieTableBody.appendChild(row);
        });

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
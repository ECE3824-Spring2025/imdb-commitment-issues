document.addEventListener('DOMContentLoaded', () => {
    const genreSelect = document.getElementById('genre-select');
    const sortSelect = document.getElementById('sort-select');
    const movieTableBody = document.getElementById('movie-table-body');

    const API_KEY = '61c678e1170ca246fbfbdeecc7aa373b'; // TMDb API key
    const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'; // Adjust the size if needed

    const updateTable = async (movies) => {
        movieTableBody.innerHTML = '';

        for (const [index, movie] of movies.entries()) {
            const posterPath = await fetchMoviePoster(movie.name);

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${movie.name}</td>
                <td><img src="${posterPath}" alt="${movie.name} Poster" width="50"></td> <!-- Poster Column -->
                <td>${movie.rating || ''}</td>
                <td>${movie.votes || ''}</td>
            `;

            movieTableBody.appendChild(row);
        }
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
});

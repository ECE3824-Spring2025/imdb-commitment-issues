'use client';

import { useState, useEffect, useCallback } from 'react';
import { Alert, Loader, Center } from '@mantine/core';
import { IconInfoCircle } from '@tabler/icons-react';
import Content from '@/containers/content';
import { Movie } from '@/components/movie_list';
import { MovieSortProvider, useMovieSort } from '@/components/discover';
import { MovieFilterProvider, useMovieFilter } from '@/components/filter';
import { MovieFormatProvider, useMovieFormat, FormatType } from '@/components/format';
import { MovieSearchProvider, useMovieSearch } from '@/components/search';

function MovieContent() {
  const { sortBy, favorites } = useMovieSort();
  const { selectedGenres } = useMovieFilter();
  const { formatType } = useMovieFormat();
  const { searchState } = useMovieSearch();

  const [allMovies, setAllMovies] = useState<Movie[]>([]);
  const [displayedMovies, setDisplayedMovies] = useState<Movie[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);

  const fetchMovies = useCallback(async () => {
    try {
        setIsLoading(true);
        setError(null);

        const res = await fetch('/api/movies?pageSize=200');
        if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);

        const data = await res.json();
        if (data && data.movies) {
            const transformedMovies: Movie[] = data.movies.map((movie: any, index: number) => ({
                id: movie.id,
                title: movie.primary_title,
                imageUrl: movie.poster_url || '',
                rating: movie.rating?.average_rating || 0,
                votes: movie.rating?.num_votes || 0,
                type: movie.title_type,
                genres: movie.genres || [],
                rank: index + 1,
                description: movie.description || 'N/A',
                releaseDate: movie.start_year ? `${movie.start_year}` : 'N/A',
                runtime: movie.runtime || 0,
                actors: movie.actors ? JSON.parse(movie.actors) : []
            }));
            setAllMovies(transformedMovies);
        } else {
            throw new Error("Movies data is undefined");
        }
    } catch (err: any) {
        console.error('Failed to fetch movies:', err);
        setError(err.message || 'An unknown error occurred');
    } finally {
        setIsLoading(false);
    }
}, []);


  

  useEffect(() => {
    fetchMovies();
  }, [fetchMovies]);

  useEffect(() => {
    let filtered = [...allMovies];

    if (formatType !== 'Any') {
      const map: Partial<Record<FormatType, string>> = { Movie: 'movie' };
      const value = map[formatType];
      if (value) filtered = filtered.filter(m => m.type?.toLowerCase() === value.toLowerCase());
    }

    if (selectedGenres.length > 0) {
      filtered = filtered.filter(movie =>
        selectedGenres.some(genre => movie.genres?.includes(genre))
      );
    }

    if (searchState.query) {
      const query = searchState.query.toLowerCase();
      filtered = filtered.filter(m => m.title.toLowerCase().includes(query));
    }

    if (sortBy === 'Top Rated') {
      filtered.sort((a, b) => b.rating - a.rating);
    } else if (sortBy === 'Most Popular') {
      filtered.sort((a, b) => (b.votes || 0) - (a.votes || 0));
    } else if (sortBy === 'Favorited') {
      filtered = filtered.filter(m => favorites.includes(m.id));
    }

    const ranked = filtered.map((movie, idx) => ({ ...movie, rank: idx + 1 }));
    setDisplayedMovies(ranked);
    setTotalCount(ranked.length);
  }, [allMovies, sortBy, formatType, searchState.query, selectedGenres, favorites]);

  if (error) {
    return (
      <Alert
        icon={<IconInfoCircle size="1rem" />}
        title="Error loading movies"
        color="red"
        variant="filled"
      >
        {error}
      </Alert>
    );
  }

  if (isLoading && displayedMovies.length === 0) {
    return (
      <Center style={{ height: '200px' }}>
        <Loader size="xl" />
      </Center>
    );
  }

  return <Content movies={displayedMovies} isLoading={isLoading} width={1250} />;
}

export default function Page() {
  return (
    <MovieSortProvider>
      <MovieFilterProvider>
        <MovieFormatProvider>
          <MovieSearchProvider>
            <main className="px-4 md:px-2">
              <MovieContent />
            </main>
          </MovieSearchProvider>
        </MovieFormatProvider>
      </MovieFilterProvider>
    </MovieSortProvider>
  );
}

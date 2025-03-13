'use client';

import { useState, useEffect, useCallback } from 'react';
import { Movie } from '@/components/movie_list';
import Content from '@/containers/content';
import { Alert, Loader, Center } from '@mantine/core';
import { IconInfoCircle } from '@tabler/icons-react';
import { MovieSortProvider, useMovieSort } from '@/components/discover';
import { MovieFilterProvider, useMovieFilter } from '@/components/filter';
import { MovieFormatProvider, useMovieFormat, FormatType } from '@/components/format';
import { MovieSearchProvider, useMovieSearch } from '@/components/search';

// Wrapper component to use the context hooks
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

  // Fetch all movies once
  const fetchMovies = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch('/api/movies?pageSize=200');
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (!data.movies || data.movies.length === 0) {
        throw new Error('No movies returned from API');
      }
      
      // Transform API data
      const transformedMovies: Movie[] = data.movies.map((movie: any, index: number) => ({
        id: movie.id,
        title: movie.primary_title,
        imageUrl: movie.primary_title, // We'll use the title for TMDB search
        rating: movie.rating?.average_rating || 0,
        votes: movie.rating?.num_votes || 0,
        type: movie.title_type,
        genres: movie.genres || [],
        rank: index + 1
      }));
      
      setAllMovies(transformedMovies);
    } catch (err: any) {
      console.error('Failed to fetch movies:', err);
      setError(err.message || 'An unknown error occurred');
      setAllMovies([]);
      setDisplayedMovies([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Apply filtering and sorting whenever any filter options change
  useEffect(() => {
    if (allMovies.length > 0) {
      // First apply all filters to get the filtered movie set
      let filteredMovies = [...allMovies];
      
      // Apply format filter
      if (formatType !== 'Any') {
        const formatMap: Partial<Record<FormatType, string>> = {
          'Movie': 'movie',
        };
        
        const formatValue = formatMap[formatType];
        if (formatValue) {
          filteredMovies = filteredMovies.filter(movie => 
            movie.type?.toLowerCase() === formatValue.toLowerCase()
          );
        }
      }
      
      // Apply genre filter
      if (selectedGenres.length > 0) {
        filteredMovies = filteredMovies.filter(movie => 
          selectedGenres.some(genre => movie.genres?.includes(genre))
        );
      }
      
      // Apply search filter
      if (searchState.query) {
        const query = searchState.query.toLowerCase();
        filteredMovies = filteredMovies.filter(movie => 
          movie.title.toLowerCase().includes(query)
        );
      }
      
      // Apply sort
      if (sortBy === 'Top Rated') {
        filteredMovies.sort((a, b) => b.rating - a.rating);
      } else if (sortBy === 'Most Popular') {
        filteredMovies.sort((a, b) => (b.votes || 0) - (a.votes || 0));
      } else if (sortBy === 'Favorited') {
        filteredMovies = filteredMovies.filter(movie => favorites.includes(movie.id));
      }
      
      // Update ranks after filtering and sorting
      const rankedMovies = filteredMovies.map((movie, index) => ({
        ...movie,
        rank: index + 1
      }));
      
      setDisplayedMovies(rankedMovies);
      setTotalCount(rankedMovies.length);
    }
  }, [allMovies, sortBy, formatType, searchState.query, selectedGenres, favorites]);

  // Initial fetch
  useEffect(() => {
    fetchMovies();
  }, [fetchMovies]);

  if (error) {
    return (
      <Alert 
        icon={<IconInfoCircle size="1rem" />}
        title="Error loading movies" 
        color="red"
        variant="filled"
      >
        {error}. Please make sure the Flask API is running and connected to the database.
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

  return (
    <Content 
      movies={displayedMovies} 
      isLoading={isLoading} 
      width={1250}
    />
  );
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
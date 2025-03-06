'use client';
import { useCallback } from 'react';
import { useMovieSort } from '../components/discover';
import { Container } from '@mantine/core';
import MovieListComponent, { Movie } from '../components/movie_list';
import Header from './menu';

export interface MovieListContainerProps {
  movies: Movie[];
  isLoading?: boolean;
  width?: number;
}

// Container component - handles state and business logic
export default function Content({
  movies,
  isLoading = false,
  width = 1250,
}: MovieListContainerProps) {
  const { sortBy, favorites, toggleFavorite } = useMovieSort();

  // Handle favorite toggling through the context
  const handleToggleFavorite = useCallback((id: string, event?: React.MouseEvent) => {
    if (event) {
      event.stopPropagation();
      event.preventDefault();
    }
    toggleFavorite(id);
  }, [toggleFavorite]);

  // Determine if rank badges should be shown (only when not in favorites view)
  const showRanks = sortBy !== 'Favorited';

  return (
    <Container size={width} px={0}>
      {/* Pass the width prop correctly to Header */}
      <Header width={width} />
      <MovieListComponent
        movies={movies}
        isLoading={isLoading}
        width={width}
        favoriteMovies={favorites}
        showRanks={showRanks}
        onToggleFavorite={handleToggleFavorite}
      />
    </Container>
  );
}
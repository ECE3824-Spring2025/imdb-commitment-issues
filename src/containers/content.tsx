'use client';

import { useState, useEffect, useCallback } from 'react';
import { Container } from '@mantine/core';
import { useMovieSort } from '../components/discover';
import MovieListComponent, { Movie } from '../components/movie_list';
import Header from './menu';

export interface MovieListContainerProps {
  movies: Movie[];
  isLoading?: boolean;
  width?: number;
}

export default function Content({
  movies,
  isLoading = false,
  width = 1100,
}: MovieListContainerProps) {
  const { sortBy, favorites, toggleFavorite } = useMovieSort();
  const [watchlist, setWatchlist] = useState<string[]>([]);

  useEffect(() => {
    const stored = localStorage.getItem('movieWatchlist');
    if (stored) setWatchlist(JSON.parse(stored));
  }, []);

  useEffect(() => {
    localStorage.setItem('movieWatchlist', JSON.stringify(watchlist));
  }, [watchlist]);

  const handleToggleFavorite = useCallback(
    (id: string, event?: React.MouseEvent) => {
      if (event) {
        event.stopPropagation();
        event.preventDefault();
      }
      toggleFavorite(id);
    },
    [toggleFavorite]
  );

  const handleToggleWatchlist = useCallback(
    (id: string, event?: React.MouseEvent) => {
      if (event) {
        event.stopPropagation();
        event.preventDefault();
      }
      setWatchlist((prev) =>
        prev.includes(id) ? prev.filter((m) => m !== id) : [...prev, id]
      );
    },
    []
  );

  const showRanks = sortBy !== 'Favorited' && sortBy !== 'Watchlist';

  const filteredMovies = sortBy === 'Watchlist'
    ? movies.filter((movie) => watchlist.includes(movie.id))
    : movies;

  const handleMovieClick = useCallback((movie: any) => {
    alert(`Title: ${movie.title}\n\nDescription: ${movie.description || 'N/A'}\nGenres: ${movie.genres?.join(', ') || 'N/A'}\nRelease Date: ${movie.releaseDate || 'N/A'}\nRuntime: ${movie.runtime || 'N/A'} minutes\nActors: ${movie.actors?.join(', ') || 'N/A'}`);
  }, []);

  return (
    <Container size={width} px={0} style={{ margin: '0 auto' }}>
      <Header width={width} />
      <MovieListComponent
        movies={filteredMovies}
        isLoading={isLoading}
        width={width}
        favoriteMovies={favorites}
        watchlistMovies={watchlist}
        showRanks={showRanks}
        onToggleFavorite={handleToggleFavorite}
        onToggleWatchlist={handleToggleWatchlist}
        onMovieClick={handleMovieClick}
      />
    </Container>
  );
}
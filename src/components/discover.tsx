'use client';
import { useState, createContext, useContext, useEffect } from 'react';
import { Box, Select, Text } from '@mantine/core';
import { IconChevronDown } from '@tabler/icons-react';

export type SortOption = 'Most Popular' | 'Top Rated' | 'Favorited' | 'Watchlist';

export const MovieSortContext = createContext<{
  sortBy: SortOption;
  setSortBy: (option: SortOption) => void;
  favorites: string[];
  toggleFavorite: (movieId: string) => void;
  watchlist: string[];
  setWatchlist: (ids: string[]) => void;
}>({
  sortBy: 'Most Popular',
  setSortBy: () => {},
  favorites: [],
  toggleFavorite: () => {},
  watchlist: [],
  setWatchlist: () => {}
});

export const useMovieSort = () => useContext(MovieSortContext);

export function MovieSortProvider({ children }: { children: React.ReactNode }) {
  const [sortBy, setSortBy] = useState<SortOption>('Most Popular');
  const [favorites, setFavorites] = useState<string[]>([]);
  const [watchlist, setWatchlist] = useState<string[]>([]);

  useEffect(() => {
    const storedFavorites = localStorage.getItem('movieFavorites');
    if (storedFavorites) {
      setFavorites(JSON.parse(storedFavorites));
    }

    const userId = localStorage.getItem('userId');
    if (userId) {
      fetch(`/api/watchlist/${userId}`)
        .then(res => res.json())
        .then(data => {
          if (Array.isArray(data.movies)) {
            setWatchlist(data.movies);
          }
        });
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('movieFavorites', JSON.stringify(favorites));
  }, [favorites]);

  const toggleFavorite = (movieId: string) => {
    setFavorites(prev => {
      if (prev.includes(movieId)) {
        return prev.filter(id => id !== movieId);
      } else {
        return [...prev, movieId];
      }
    });
  };

  return (
    <MovieSortContext.Provider value={{ sortBy, setSortBy, favorites, toggleFavorite, watchlist, setWatchlist }}>
      {children}
    </MovieSortContext.Provider>
  );
}

export default function SortBy() {
  const { sortBy, setSortBy } = useMovieSort();

  return (
    <Box>
      <Text size="md" mb={8}>Discover</Text>
      <Select
        value={sortBy}
        onChange={(value) => {
          if (value) setSortBy(value as SortOption);
        }}
        data={[
          { value: 'Most Popular', label: 'Most Popular' },
          { value: 'Top Rated', label: 'Top Rated' },
          { value: 'Favorited', label: 'Favorited' },
          { value: 'Watchlist', label: 'Watchlist' }
        ]}
        rightSection={<IconChevronDown size={16} />}
        styles={(theme) => ({
          rightSection: { pointerEvents: 'none' },
          input: {
            fontWeight: 500,
            minWidth: '200px'
          }
        })}
      />
    </Box>
  );
}

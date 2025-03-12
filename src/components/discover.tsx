'use client';
import { useState, createContext, useContext, useEffect } from 'react';
import { Box, Select, Text } from '@mantine/core';
import { IconChevronDown } from '@tabler/icons-react';

export type SortOption = 'Most Popular' | 'Top Rated' | 'Favorited';

// Create a context to share the sort state across components
export const MovieSortContext = createContext<{
  sortBy: SortOption;
  setSortBy: (option: SortOption) => void;
  favorites: string[];
  toggleFavorite: (movieId: string) => void;
}>({
  sortBy: 'Most Popular',
  setSortBy: () => {},
  favorites: [],
  toggleFavorite: () => {}
});

// Custom hook to use the context
export const useMovieSort = () => useContext(MovieSortContext);

// Provider component that will wrap the app
export function MovieSortProvider({ children }: { children: React.ReactNode }) {
  const [sortBy, setSortBy] = useState<SortOption>('Most Popular');
  const [favorites, setFavorites] = useState<string[]>([]);
  
  // Load favorites from localStorage on initial mount
  useEffect(() => {
    const storedFavorites = localStorage.getItem('movieFavorites');
    if (storedFavorites) {
      setFavorites(JSON.parse(storedFavorites));
    }
  }, []);
  
  // Save favorites to localStorage whenever they change
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
    <MovieSortContext.Provider value={{ sortBy, setSortBy, favorites, toggleFavorite }}>
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
          if (value) {
            setSortBy(value as SortOption);
          }
        }}
        data={[
          { value: 'Most Popular', label: 'Most Popular' },
          { value: 'Top Rated', label: 'Top Rated' },
          { value: 'Favorited', label: 'Favorited' }
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
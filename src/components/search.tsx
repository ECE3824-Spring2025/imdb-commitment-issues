'use client';
import { useState, createContext, useContext, useEffect } from 'react';
import { Box, TextInput, Text } from '@mantine/core';
import { IconSearch } from '@tabler/icons-react';

// Define the type for search state
export type SearchState = {
  query: string;
  isSearching: boolean;
};

// Create a context to share the search state across components
export const MovieSearchContext = createContext<{
  searchState: SearchState;
  setSearchQuery: (query: string) => void;
}>({
  searchState: { query: '', isSearching: false },
  setSearchQuery: () => {}
});

// Custom hook to use the context
export const useMovieSearch = () => useContext(MovieSearchContext);

// Provider component that will wrap the app
export function MovieSearchProvider({ children }: { children: React.ReactNode }) {
  const [searchState, setSearchState] = useState<SearchState>({ 
    query: '', 
    isSearching: false 
  });
  
  const setSearchQuery = (query: string) => {
    setSearchState({ 
      query, 
      isSearching: query.length > 0 
    });
  };
  
  return (
    <MovieSearchContext.Provider value={{ searchState, setSearchQuery }}>
      {children}
    </MovieSearchContext.Provider>
  );
}

export default function Search() {
  const { searchState, setSearchQuery } = useMovieSearch();
  const [inputValue, setInputValue] = useState('');
  
  // Debounce search input to prevent excessive API calls
  useEffect(() => {
    const handler = setTimeout(() => {
      setSearchQuery(inputValue);
    }, 300); // 300ms delay
    
    return () => {
      clearTimeout(handler);
    };
  }, [inputValue, setSearchQuery]);
  
  return (
    <Box>
      <Text size="md" mb={8}>Search</Text>
      <TextInput
        value={inputValue}
        onChange={(event) => setInputValue(event.currentTarget.value)}
        leftSection={<IconSearch size={16} />}
        styles={{
          input: {
            fontWeight: 500,
            minWidth: '200px'
          }
        }}
      />
    </Box>
  );
}
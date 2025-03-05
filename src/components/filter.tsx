'use client';
import { useState, createContext, useContext, useEffect } from 'react';
import { Box, MultiSelect, Text, Loader, MantineTheme } from '@mantine/core';
import { IconChevronDown } from '@tabler/icons-react';

// Create a context to share the filter state across components
export const MovieFilterContext = createContext<{
  selectedGenres: string[];
  setSelectedGenres: (genres: string[]) => void;
}>({
  selectedGenres: [],
  setSelectedGenres: () => {}
});

// Custom hook to use the context
export const useMovieFilter = () => useContext(MovieFilterContext);

// Provider component that will wrap the app
export function MovieFilterProvider({ children }: { children: React.ReactNode }) {
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  
  return (
    <MovieFilterContext.Provider value={{ selectedGenres, setSelectedGenres }}>
      {children}
    </MovieFilterContext.Provider>
  );
}

// Define genre interface
interface Genre {
  name: string;
  count: number;
}

// Define transformed genre interface for MultiSelect
interface GenreOption {
  value: string;
  label: string;
  count?: number;
}

export default function Filter() {
  const { selectedGenres, setSelectedGenres } = useMovieFilter();
  const [genres, setGenres] = useState<GenreOption[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch genres from the API
  useEffect(() => {
    const fetchGenres = async () => {
      try {
        setIsLoading(true);
        
        const response = await fetch('/api/genres');
        
        if (!response.ok) {
          throw new Error(`Failed to fetch genres: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.genres || !Array.isArray(data.genres)) {
          throw new Error('Invalid genres data from API');
        }
        
        // Transform API data to MultiSelect format with explicit type
        const transformed = data.genres.map((genre: Genre) => ({
          value: genre.name,
          label: `${genre.name}`,
          count: genre.count
        }));
        
        // Sort by count (descending) with explicit types
        transformed.sort((a: GenreOption, b: GenreOption) => (b.count || 0) - (a.count || 0));
        
        setGenres(transformed);
        setError(null);
      } catch (err: any) {
        console.error('Error fetching genres:', err);
        setError(err.message || 'Failed to load genres');
        
        // Fallback to hardcoded genres if API fails
        setGenres([
          { value: 'Drama', label: 'Drama' },
          { value: 'Comedy', label: 'Comedy' },
          { value: 'Action', label: 'Action' },
          { value: 'Thriller', label: 'Thriller' },
          { value: 'Romance', label: 'Romance' },
          { value: 'Horror', label: 'Horror' },
          { value: 'Sci-Fi', label: 'Sci-Fi' },
          { value: 'Adventure', label: 'Adventure' },
          { value: 'Fantasy', label: 'Fantasy' },
          { value: 'Crime', label: 'Crime' },
          { value: 'Mystery', label: 'Mystery' },
          { value: 'Family', label: 'Family' },
          { value: 'Biography', label: 'Biography' }
        ]);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchGenres();
  }, []);
  
  return (
    <Box>
      <Text size="md" mb={8}>Genres</Text>
      {isLoading ? (
        <Box style={{ minHeight: '38px', display: 'flex', alignItems: 'center' }}>
          <Loader size="sm" />
        </Box>
      ) : (
        <div style={{ position: 'relative' }}>
          {/* The actual MultiSelect that powers selection */}
          <MultiSelect
            data={genres}
            value={selectedGenres}
            onChange={setSelectedGenres}
            placeholder="Any"
            searchable
            clearable
            rightSection={<IconChevronDown size={16} />}
            styles={(theme) => ({
              input: {
                fontWeight: 500,
                width: '200px',
                minWidth: '200px',
                maxWidth: '200px',
                // Make the actual text transparent when genres are selected
                color: selectedGenres.length > 0 ? 'transparent' : undefined
              },
              rightSection: { pointerEvents: 'none' },
              dropdown: { width: '200px' },
              pill: { display: 'none' } // Hide all Mantine's pills
            })}
            maxDropdownHeight={280}
          />
          
          {/* Overlay to show exactly what we want */}
          {selectedGenres.length > 0 && (
            <div style={{
              position: 'absolute', 
              top: '50%',
              left: '12px',
              transform: 'translateY(-50%)',
              zIndex: 2,
              pointerEvents: 'auto',
              display: 'flex',
              alignItems: 'center'
            }}>
              {/* Show first genre as a badge */}
              <div 
                style={{
                  background: '#f1f3f5',
                  borderRadius: '4px',
                  padding: '2px 8px',
                  fontSize: '14px',
                  fontWeight: 500,
                  display: 'flex',
                  alignItems: 'center',
                  cursor: 'pointer'
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  // Remove the first genre when clicked
                  const updatedGenres = [...selectedGenres];
                  updatedGenres.splice(0, 1);
                  setSelectedGenres(updatedGenres);
                }}
              >
                {genres.find(g => g.value === selectedGenres[0])?.label || selectedGenres[0]}
              </div>
              
              {/* For multiple genres, show "+N" beside the first genre */}
              {selectedGenres.length > 1 && (
                <div style={{
                  marginLeft: '6px',
                  background: '#f1f3f5',
                  borderRadius: '4px',
                  padding: '2px 8px',
                  fontSize: '12px',
                  fontWeight: 500
                }}>
                  +{selectedGenres.length - 1}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </Box>
  );
}
'use client';
import { useState, createContext, useContext, useEffect } from 'react';
import { Box, MultiSelect, Text, Loader, Badge } from '@mantine/core';
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
                color: selectedGenres.length > 0 ? 'transparent' : undefined,
                position: 'relative',
                zIndex: 0
              },
              rightSection: { pointerEvents: 'none' },
              dropdown: { 
                width: '200px',
                zIndex: 10 // Ensure dropdown is above other elements
              },
              pill: { display: 'none' }, // Hide all Mantine's pills
              item: {
                // Just highlight selected items but don't hide them 
                '&[data-selected]': {
                  backgroundColor: theme.colors.blue[0]
                }
              }
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
              zIndex: 1, // Lower z-index to allow clicks to pass through
              pointerEvents: 'none', // Ensure clicks pass through to the MultiSelect
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}>
              {/* First genre as a badge */}
              <Badge 
                variant="light" 
                color="gray" 
                radius="sm"
                styles={(theme) => ({
                  root: {
                    border: '1px solid #e9ecef',
                    background: '#f8f9fa'
                  }
                })}
              >
                {selectedGenres[0]}
              </Badge>
              
              {/* For multiple genres, show "+N" beside the first genre */}
              {selectedGenres.length > 1 && (
                <Badge 
                  variant="light" 
                  color="gray" 
                  radius="sm"
                  styles={(theme) => ({
                    root: {
                      border: '1px solid #e9ecef',
                      background: '#f8f9fa'
                    }
                  })}
                >
                  +{selectedGenres.length - 1}
                </Badge>
              )}
            </div>
          )}
        </div>
      )}
    </Box>
  );
}
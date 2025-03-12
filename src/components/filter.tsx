'use client';
import { useState, createContext, useContext, useEffect, useCallback } from 'react';
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
                const transformed: GenreOption[] = data.genres.map((genre: Genre): GenreOption => ({
                    value: genre.name,
                    label: `${genre.name}`,
                    count: genre.count
                }));

                // Sort by count (descending) with explicit type handling
                transformed.sort((a: GenreOption, b: GenreOption) => (b.count ?? 0) - (a.count ?? 0));

                // Filter for distinct genre options
                const distinctTransformed = transformed.reduce((acc: GenreOption[], curr: GenreOption) => {
                    if (!acc.find(item => item.value === curr.value)) {
                        acc.push(curr);
                    }
                    return acc;
                }, []);

                setGenres(distinctTransformed);
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

    const handleGenreChange = useCallback((value: string[]) => {
        // Ensure that there are no misspelled genres being passed to the database

        const validGenres = value.map((genre) => {
            if (genre.toLowerCase() === "familv") {
                return "Family";
            } else if (genre.toLowerCase() === "fantasv") {
                return "Fantasy";
            }
            return genre;
        });
        setSelectedGenres(validGenres);
    }, [setSelectedGenres]);

    return (
        <Box>
            <Text size="md" mb={8}>Genres</Text>
            {isLoading ? (
                <Box style={{ minHeight: '38px', display: 'flex', alignItems: 'center' }}>
                    <Loader size="sm" />
                </Box>
            ) : (
                <div>
                    <MultiSelect
                        data={genres}
                        value={selectedGenres}
                        onChange={handleGenreChange}
                        placeholder="Any"
                        searchable
                        clearable
                        rightSection={<IconChevronDown size={16} />}
                        maxDropdownHeight={280}
                        valueComponent={({ value, ...others }) => {
                            const genre = genres.find((g) => g.value === value);
                            if (!genre) return null;
                            return (
                                <Badge
                                    color="blue"
                                    radius="sm"
                                    variant="light"
                                    style={{ margin: '2px', display: 'inline-flex', alignItems: 'center', pointerEvents: 'auto' }}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleGenreChange(selectedGenres.filter(g => g !== value));
                                    }}
                                >
                                    {genre.label} ×
                                </Badge>
                            );
                        }}
                        styles={(theme) => ({
                            input: {
                                minHeight: '38px',
                                padding: '4px 8px',
                                cursor: 'pointer'
                            },
                            values: {
                                display: 'flex',
                                flexWrap: 'wrap',
                                minWidth: '100px',
                                position: 'relative',
                            },
                            rightSection: { pointerEvents: 'none' },
                        })}
                    />
                </div>
            )}
        </Box>
    );
}
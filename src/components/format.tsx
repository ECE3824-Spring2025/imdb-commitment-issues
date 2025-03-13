'use client';
import { useState, createContext, useContext } from 'react';
import { Box, Select, Text } from '@mantine/core';
import { IconChevronDown } from '@tabler/icons-react';

export type FormatType = 'Movie' | 'Any';

// Create a context to share the format state across components
export const MovieFormatContext = createContext<{
  formatType: FormatType;
  setFormatType: (format: FormatType) => void;
}>({
  formatType: 'Movie',  // Changed default from 'Any' to 'Movie'
  setFormatType: () => {}
});

// Custom hook to use the context
export const useMovieFormat = () => useContext(MovieFormatContext);

// Provider component that will wrap the app
export function MovieFormatProvider({ children }: { children: React.ReactNode }) {
  const [formatType, setFormatType] = useState<FormatType>('Movie');  // Changed default from 'Any' to 'Movie'
  
  return (
    <MovieFormatContext.Provider value={{ formatType, setFormatType }}>
      {children}
    </MovieFormatContext.Provider>
  );
}

export default function Format() {
  const { formatType, setFormatType } = useMovieFormat();
  
  // Removed 'Any' from the data array
  const formatOptions: {value: FormatType, label: string}[] = [
    { value: 'Movie', label: 'Movie' },
  ];
  
  return (
    <Box>
      <Text size="md" mb={8}>Format</Text>
      <Select
        data={formatOptions}
        value={formatType}
        onChange={(value) => setFormatType(value as FormatType || 'Movie')}  // Default to 'Movie' if null
        rightSection={<IconChevronDown size={16} />}
        styles={{
          input: {
            fontWeight: 500,
            minWidth: '200px'
          },
          rightSection: { 
            pointerEvents: 'none' // Make the dropdown icon not block clicks
          }
        }}
      />
    </Box>
  );
}
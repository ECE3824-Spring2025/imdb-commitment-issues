'use client';

import { Grid, Card, Image, Text, Rating, Flex, ActionIcon, Loader, Badge, Box, Container } from '@mantine/core';
import { IconHeart, IconHeartFilled, IconStar } from '@tabler/icons-react';
import { memo, useState, useEffect } from 'react';

// Format vote count according to IMDB style (e.g., 1.2M, 934K, 123)
const formatVotes = (votes: number): string => {
  if (votes >= 1000000) {
    return `${(votes / 1000000).toFixed(1)}M`;
  } else if (votes >= 1000) {
    return `${Math.round(votes / 1000)}K`;
  } else {
    return votes.toString();
  }
};

export interface Movie {
  id: string;
  title: string;
  imageUrl: string;
  rating: number;
  votes?: number;
  type?: string;
  genres?: string[];
  rank?: number;
}

export interface MovieListComponentProps {
  movies: Movie[];
  isLoading?: boolean;
  width?: number;
  favoriteMovies: string[];
  showRanks: boolean;
  onToggleFavorite: (id: string, event?: React.MouseEvent) => void;
}

// Movie card component that fetches TMDB poster images
const MovieCard = memo(({ 
  movie, 
  isFavorite, 
  showRank, 
  onToggleFavorite 
}: { 
  movie: Movie; 
  isFavorite: boolean; 
  showRank: boolean; 
  onToggleFavorite: (id: string, event?: React.MouseEvent) => void;
}) => {
  const [posterUrl, setPosterUrl] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // TMDB API key - Replace with your actual key
  const TMDB_API_KEY = process.env.NEXT_PUBLIC_TMDB_API_KEY || "68ef6f5d041dc3079fd6f2cfc0a35d2b";

  useEffect(() => {
    const fetchMoviePoster = async () => {
      // If the imageUrl is already a TMDB path
      if (movie.imageUrl.startsWith('/')) {
        setPosterUrl(`https://image.tmdb.org/t/p/w500${movie.imageUrl}`);
        setIsLoading(false);
        return;
      }

      try {
        // Search for the movie in TMDB
        const response = await fetch(
          `https://api.themoviedb.org/3/search/movie?api_key=${TMDB_API_KEY}&query=${encodeURIComponent(movie.title)}&include_adult=false`
        );
        
        if (!response.ok) {
          throw new Error('TMDB API request failed');
        }
        
        const data = await response.json();
        
        // If we found results and the first result has a poster
        if (data.results && data.results.length > 0 && data.results[0].poster_path) {
          setPosterUrl(`https://image.tmdb.org/t/p/w500${data.results[0].poster_path}`);
        } else {
          // No poster found, use placeholder
          setPosterUrl(`https://placehold.co/230x288/png?text=${encodeURIComponent(movie.title.slice(0, 20))}`);
        }
      } catch (error) {
        console.error('Error fetching movie poster:', error);
        setPosterUrl(`https://placehold.co/230x288/png?text=${encodeURIComponent(movie.title.slice(0, 20))}`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMoviePoster();
  }, [movie.title, movie.imageUrl, TMDB_API_KEY]);

  return (
    <Card shadow="sm" padding="xs" pos="relative" w={230} style={{ height: '100%' }}>
      <Card.Section pos="relative">
        <Image
          src={posterUrl || `https://placehold.co/230x288/png?text=${encodeURIComponent(movie.title.slice(0, 20))}`}
          height={288}
          w={230}
          alt={movie.title}
          loading="lazy" // Lazy load images
          placeholder={isLoading ? "blur" : undefined}
          fallbackSrc={`https://placehold.co/230x288/png?text=${encodeURIComponent(movie.title.slice(0, 20))}`}
        />
        
        {/* Rank badge */}
        {showRank && movie.rank && (
          <Badge 
            color="rgba(0, 0, 0, 255)"
            radius={2}
            style={{ 
              position: 'absolute', 
              top: 0, 
              left: 0,
              fontSize: '18px',
              padding: '20px 10px'
            }}
          >
            #{movie.rank}
          </Badge>
        )}
        
        {/* Favorite button */}
        <ActionIcon 
          variant="filled" 
          color={isFavorite ? "red" : "gray"} 
          onClick={(e) => onToggleFavorite(movie.id, e)}
          style={{ 
            position: 'absolute', 
            bottom: 0, 
            right: 0,
            opacity: 0.9
          }}
        >
          {isFavorite ? 
            <IconHeartFilled size={18} /> : 
            <IconHeart size={18} />
          }
        </ActionIcon>
      </Card.Section>
      
      <Flex justify="space-between" align="center" mt="xs">
        <Text fw={500} size="14px" lineClamp={2} title={movie.title} style={{ lineHeight: '1.2' }}>
          {movie.title}
        </Text>
      </Flex>
      
      <Flex align="center" mt={4} style={{ flexWrap: 'nowrap', alignItems: 'center' }}>
        <Rating
          value={movie.rating / 2} // Normalize to 5-star scale
          fractions={2}
          count={5}
          size={14}
          readOnly
        />
        {movie.rating > 0 && (
          <Text size="xs" ml={4} style={{ whiteSpace: 'nowrap', lineHeight: 1, display: 'flex', alignItems: 'center' }}>
            {movie.rating.toFixed(1)}
            {movie.votes !== undefined && movie.votes > 0 && (
              <Text component="span" size="xs" c="dimmed" ml={3} style={{ display: 'inline', lineHeight: 1 }}>
                {" "}({formatVotes(movie.votes)})
              </Text>
            )}
          </Text>
        )}
      </Flex>
    </Card>
  );
});

// Add display name for debugging and better component tree
MovieCard.displayName = 'MovieCard';

// Pure presentational component - only handles rendering
const MovieListComponent = ({ 
  movies, 
  isLoading = false, 
  width = 1250,
  favoriteMovies,
  showRanks,
  onToggleFavorite
}: MovieListComponentProps) => {

  // Render movie grid or loading state
  const renderMovieGrid = () => {
    if (isLoading && movies.length === 0) {
      return (
        <Box style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
          <Loader size="xl" />
        </Box>
      );
    }

    if (!movies || movies.length === 0) {
      return (
        <Box style={{ textAlign: 'center', padding: '50px' }}>
          <Text fw={500} fz="lg">No movies found</Text>
          <Text size="sm" mt="xs">Try changing your filter selection</Text>
        </Box>
      );
    }

    return (
      <Grid>
        {movies.map((movie) => (
          <Grid.Col key={movie.id} span={{ base: 12, sm: 6, md: 4, lg: 2.4 }} style={{ display: 'flex', justifyContent: 'center' }}>
            <MovieCard 
              movie={movie}
              isFavorite={favoriteMovies.includes(movie.id)}
              showRank={showRanks}
              onToggleFavorite={onToggleFavorite}
            />
          </Grid.Col>
        ))}
      </Grid>
    );
  };

  return (
    <Container size={width} px={0}>
      {renderMovieGrid()}
    </Container>
  );
};

// Export as memoized component to prevent unnecessary re-renders
export default memo(MovieListComponent);
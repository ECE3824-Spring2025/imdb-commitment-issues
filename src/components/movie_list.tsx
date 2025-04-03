'use client';

import { Grid, Card, Image, Text, Rating, Flex, ActionIcon, Loader, Badge, Box, Container } from '@mantine/core';
import { IconHeart, IconHeartFilled, IconEye, IconEyeOff } from '@tabler/icons-react';
import { memo, useState, useEffect } from 'react';

export interface Movie {
  id: string;
  title: string;
  imageUrl: string;
  rating: number;
  votes?: number;
  type?: string;
  genres?: string[];
  rank?: number;
  description?: string;
  releaseDate?: string;
  runtime?: number;
  actors?: string[];
}

export interface MovieListComponentProps {
  movies: Movie[];
  isLoading?: boolean;
  width?: number;
  favoriteMovies: string[];
  watchlistMovies: string[];
  showRanks: boolean;
  onToggleFavorite: (id: string, event?: React.MouseEvent) => void;
  onToggleWatchlist: (id: string, event?: React.MouseEvent) => void;
  onMovieClick: (movie: Movie) => void;
}

const MovieCard = memo(({ 
  movie, 
  isFavorite, 
  isWatchlisted,
  showRank,
  onToggleFavorite,
  onToggleWatchlist,
  onMovieClick
}: { 
  movie: Movie; 
  isFavorite: boolean;
  isWatchlisted: boolean;
  showRank: boolean;
  onToggleFavorite: (id: string, event?: React.MouseEvent) => void;
  onToggleWatchlist: (id: string, event?: React.MouseEvent) => void;
  onMovieClick: (movie: Movie) => void;
}) => {
  const [posterUrl, setPosterUrl] = useState<string>("");

  useEffect(() => {
    if (movie.imageUrl) {
      setPosterUrl(movie.imageUrl);
    } else {
      setPosterUrl(`https://placehold.co/230x288/png?text=${encodeURIComponent(movie.title.slice(0, 20))}`);
    }
  }, [movie.imageUrl, movie.title]);
  
  

  return (
    <Card shadow="sm" padding={0} pos="relative" w={230} style={{ height: '100%', cursor: 'pointer' }} onClick={() => onMovieClick(movie)}>
      <Card.Section pos="relative">
        <Image
          src={posterUrl || `https://placehold.co/230x288/png?text=${encodeURIComponent(movie.title.slice(0, 20))}`}
          height={288}
          w={230}
          alt={movie.title}
        />
        {showRank && movie.rank && (
          <Badge color="dark" radius={2} style={{ position: 'absolute', top: 0, left: 0, fontSize: '18px', padding: '20px 10px' }}>
            #{movie.rank}
          </Badge>
        )}
        <ActionIcon 
          variant="filled" 
          color={isFavorite ? "red" : "gray"} 
          onClick={(e) => onToggleFavorite(movie.id, e)}
          style={{ position: 'absolute', bottom: 0, right: 0, opacity: 0.9 }}
        >
          {isFavorite ? <IconHeartFilled size={18} /> : <IconHeart size={18} />}
        </ActionIcon>
        <ActionIcon 
          variant="filled" 
          color={isWatchlisted ? "blue" : "gray"} 
          onClick={(e) => onToggleWatchlist(movie.id, e)}
          style={{ position: 'absolute', bottom: 0, left: 0, opacity: 0.9 }}
        >
          {isWatchlisted ? <IconEyeOff size={18} /> : <IconEye size={18} />}
        </ActionIcon>
      </Card.Section>
      <Box p="xs">
        <Text fw={500} size="14px" lineClamp={2} title={movie.title} style={{ lineHeight: '1.2' }}>
          {movie.title}
        </Text>
        <Flex align="center" mt={5} style={{ flexWrap: 'nowrap', alignItems: 'center' }}>
          <Rating value={movie.rating / 2} fractions={2} count={5} size="xs" readOnly />
          {movie.rating > 0 && (
            <Text size="xs" ml={4} c="dimmed">
              {movie.rating.toFixed(1)} {movie.votes && `(${movie.votes})`}
            </Text>
          )}
        </Flex>
      </Box>
    </Card>
  );
});

MovieCard.displayName = 'MovieCard';

const MovieListComponent = ({
  movies,
  isLoading = false,
  width = 1250,
  favoriteMovies,
  watchlistMovies,
  showRanks,
  onToggleFavorite,
  onToggleWatchlist,
  onMovieClick
}: MovieListComponentProps) => {
  if (isLoading && movies.length === 0) {
    return <Box style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}><Loader size="xl" /></Box>;
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
    <Container size={width} px={0}>
      <Grid>
        {movies.map((movie) => (
          <Grid.Col key={movie.id} span={12} xs={12} sm={6} md={4} lg={2.4} style={{ display: 'flex', justifyContent: 'center' }}>
            <MovieCard
              movie={movie}
              isFavorite={favoriteMovies.includes(movie.id)}
              isWatchlisted={watchlistMovies.includes(movie.id)}
              showRank={showRanks}
              onToggleFavorite={onToggleFavorite}
              onToggleWatchlist={onToggleWatchlist}
              onMovieClick={onMovieClick}
            />
          </Grid.Col>
        ))}
      </Grid>
    </Container>
  );
};

export default memo(MovieListComponent);

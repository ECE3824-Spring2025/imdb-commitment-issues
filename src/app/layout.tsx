'use client';

import {
  MantineProvider,
  ColorSchemeProvider,
  ColorScheme,
  createEmotionCache,
} from '@mantine/core';
import { useState } from 'react';
import { CacheProvider } from '@emotion/react';
import { useLocalStorage } from '@mantine/hooks';

const myCache = createEmotionCache({ key: 'mantine', prepend: false });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [colorScheme, setColorScheme] = useLocalStorage<ColorScheme>({
    key: 'color-scheme',
    defaultValue: 'light',
  });

  const toggleColorScheme = (value?: ColorScheme) =>
    setColorScheme(value || (colorScheme === 'dark' ? 'light' : 'dark'));

  return (
    <html lang="en">
      <head>
        <title>IMDB Project</title>
        <meta name="viewport" content="minimum-scale=1, initial-scale=1, width=device-width" />
      </head>
      <body>
        <CacheProvider value={myCache}>
          <ColorSchemeProvider colorScheme={colorScheme} toggleColorScheme={toggleColorScheme}>
            <MantineProvider
              theme={{ colorScheme }}
              withGlobalStyles
              withNormalizeCSS
              emotionCache={myCache}
            >
              {children}
            </MantineProvider>
          </ColorSchemeProvider>
        </CacheProvider>
      </body>
    </html>
  );
}

'use client';

import { MantineProvider, MantineThemeOverride, createEmotionCache } from '@mantine/core';
import { CacheProvider } from '@emotion/react';

// Create cache with namespace to avoid conflicts in app router
const myCache = createEmotionCache({ key: 'mantine', prepend: false });

// Define theme for Mantine v6
const theme: MantineThemeOverride = {
  colorScheme: 'light',
  primaryColor: 'blue',
  defaultRadius: 'md',
  // Add any other theme customizations here
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <title>IMDB Project</title>
        <meta name="viewport" content="minimum-scale=1, initial-scale=1, width=device-width" />
      </head>
      <body style={{ backgroundColor: '#f5f5f5', margin: 0 }}>
        <CacheProvider value={myCache}>
          <MantineProvider theme={theme} withGlobalStyles withNormalizeCSS emotionCache={myCache}>
            {children}
          </MantineProvider>
        </CacheProvider>
      </body>
    </html>
  );
}
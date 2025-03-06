import { MantineProvider, MantineThemeOverride } from '@mantine/core';
import '@mantine/core/styles.css';

// Define theme for Mantine v6
const theme: MantineThemeOverride = {
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
      <body style={{ backgroundColor: '#f5f5f5' }}>
        <MantineProvider theme={theme}>
          {children}
        </MantineProvider>
      </body>
    </html>
  );
}
import React from 'react';
import { CssBaseline, Container, ThemeProvider, createTheme } from '@mui/material';
import VideoConverter from './components/VideoConverter';

const theme = createTheme({
  palette: {
    mode: 'light',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container>
        <VideoConverter />
      </Container>
    </ThemeProvider>
  );
}

export default App; 
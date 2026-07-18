import { BrowserRouter as Router } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext.tsx'; // Wait, it's context/AuthContext.tsx actually, let's keep context/AuthContext.tsx
import { ThemeProvider } from './context/ThemeContext.tsx';
import ErrorBoundary from './components/common/ErrorBoundary.tsx';
import AppRoutes from './routes/AppRoutes.tsx';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <ErrorBoundary>
          <AuthProvider>
            <Router>
              <AppRoutes />
              <Toaster
                position="top-right"
                toastOptions={{
                  className: 'dark:bg-gray-800 dark:text-white',
                  duration: 4000,
                }}
              />
            </Router>
          </AuthProvider>
        </ErrorBoundary>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;

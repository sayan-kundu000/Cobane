import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext.tsx';
import { ThemeProvider } from './context/ThemeContext.tsx';
import DashboardLayout from './layouts/DashboardLayout.tsx';
import Dashboard from './pages/Dashboard.tsx';
import Auth from './pages/Auth.tsx';
import Projects from './pages/Projects.tsx';
import Reviews from './pages/Reviews.tsx';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public route */}
            <Route path="/auth" element={<Auth />} />

            {/* Console / Dashboard routes */}
            <Route
              path="/"
              element={
                <DashboardLayout>
                  <Dashboard />
                </DashboardLayout>
              }
            />
            <Route
              path="/projects"
              element={
                <DashboardLayout>
                  <Projects />
                </DashboardLayout>
              }
            />
            <Route
              path="/reviews"
              element={
                <DashboardLayout>
                  <Reviews />
                </DashboardLayout>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;

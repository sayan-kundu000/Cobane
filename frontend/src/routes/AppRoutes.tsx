import React, { useContext } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext.tsx';
import DashboardLayout from '../layouts/DashboardLayout.tsx';
import MainLayout from '../layouts/MainLayout.tsx';

// Pages
import Landing from '../pages/Landing.tsx';
import Auth from '../pages/Auth.tsx';
import Dashboard from '../pages/Dashboard.tsx';
import Projects from '../pages/Projects.tsx';
import ProjectDetail from '../pages/ProjectDetail.tsx';
import Reviews from '../pages/Reviews.tsx';
import ReviewDetail from '../pages/ReviewDetail.tsx';
import Reports from '../pages/Reports.tsx';
import ReportDetail from '../pages/ReportDetail.tsx';
import Documentation from '../pages/Documentation.tsx';
import Settings from '../pages/Settings.tsx';
import Profile from '../pages/Profile.tsx';
import Admin from '../pages/Admin.tsx';
import BackendStatus from '../pages/BackendStatus.tsx';
import NotFound from '../pages/NotFound.tsx';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const authContext = useContext(AuthContext);
  if (!authContext) {
    return <>{children}</>;
  }

  const { isAuthenticated } = authContext;
  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  return <>{children}</>;
};

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route
        path="/landing"
        element={
          <MainLayout>
            <Landing />
          </MainLayout>
        }
      />
      <Route
        path="/auth"
        element={
          <MainLayout>
            <Auth />
          </MainLayout>
        }
      />

      {/* Protected Console / Dashboard routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <Dashboard />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/projects"
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <Projects />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/projects/:id"
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <ProjectDetail />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/reviews"
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <Reviews />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/reviews/:id"
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <ReviewDetail />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/reports"
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <Reports />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/reports/:id"
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <ReportDetail />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/documentation"
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <Documentation />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <Settings />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <Profile />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <Admin />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/backend-status"
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <BackendStatus />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />

      {/* Redirects & Wildcard */}
      <Route path="/404" element={<NotFound />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.ts';
import { useTheme } from '../hooks/useTheme.ts';

export const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/auth?mode=login');
  };

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r dark:bg-gray-800 dark:border-gray-700">
        <div className="p-6">
          <h2 className="text-xl font-bold text-primary-600 dark:text-primary-400">Cobane Console</h2>
        </div>
        <nav className="mt-6 px-4 space-y-2">
          <Link to="/" className="block px-4 py-2 text-gray-700 rounded hover:bg-gray-200 dark:text-gray-200 dark:hover:bg-gray-700">
            Dashboard
          </Link>
          <Link to="/projects" className="block px-4 py-2 text-gray-700 rounded hover:bg-gray-200 dark:text-gray-200 dark:hover:bg-gray-700">
            Projects
          </Link>
          <Link to="/reviews" className="block px-4 py-2 text-gray-700 rounded hover:bg-gray-200 dark:text-gray-200 dark:hover:bg-gray-700">
            Reviews
          </Link>
          <Link to="/backend-status" className="block px-4 py-2 text-gray-700 rounded hover:bg-gray-200 dark:text-gray-200 dark:hover:bg-gray-700 font-semibold text-indigo-600 dark:text-indigo-400">
            Backend Status
          </Link>
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white border-b flex items-center justify-between px-6 dark:bg-gray-800 dark:border-gray-700">
          <span className="text-sm font-medium text-gray-500">Status: Ready</span>
          <div className="flex items-center space-x-3">
            <button
              onClick={toggleTheme}
              className="text-xs bg-gray-200 hover:bg-gray-300 px-3 py-1.5 rounded-none dark:bg-gray-700 dark:text-white dark:hover:bg-gray-650 transition font-bold uppercase tracking-wider"
            >
              {theme === 'light' ? '☀️ Light' : theme === 'dark' ? '🌙 Dark' : '⚡ Neon'}
            </button>
            <button
              onClick={handleLogout}
              className="text-xs bg-rose-600 hover:bg-rose-700 text-white px-3 py-1.5 rounded-none font-bold uppercase tracking-wider transition"
            >
              Logout
            </button>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};
export default DashboardLayout;

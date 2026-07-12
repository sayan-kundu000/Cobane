import React from 'react';
import { Link } from 'react-router-dom';

export const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
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
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white border-b flex items-center justify-between px-6 dark:bg-gray-800 dark:border-gray-700">
          <span className="text-sm font-medium text-gray-500">Status: Ready</span>
          <button className="text-sm bg-gray-200 px-3 py-1 rounded dark:bg-gray-700">Logout</button>
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};
export default DashboardLayout;

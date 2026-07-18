import React from 'react';
import { Link } from 'react-router-dom';

export const NotFound: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-center space-y-6 max-w-md mx-auto px-4 bg-gray-50 dark:bg-gray-900">
      <div className="text-primary-600 dark:text-primary-400 font-black text-9xl tracking-wider select-none">
        404
      </div>
      <div className="space-y-2">
        <h2 className="text-2xl font-black text-gray-900 dark:text-white tracking-tight">
          Page Not Found
        </h2>
        <p className="text-sm text-gray-500 max-w-sm mx-auto leading-relaxed">
          The requested console workspace URL was not resolved or has expired. Verify spelling or return to the main dashboard.
        </p>
      </div>
      <Link
        to="/"
        className="px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-xl text-xs font-bold transition shadow-md shadow-primary-500/20"
      >
        Return to Dashboard
      </Link>
    </div>
  );
};

export default NotFound;

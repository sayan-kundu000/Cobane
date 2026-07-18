import React from 'react';
import Card from '../components/ui/Card.tsx';

export const Admin: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-6 bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 rounded-2xl shadow-sm">
        <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          Superuser Operations
        </h1>
        <p className="text-sm text-gray-550 mt-1">
          Access core administrative database backups and global token metrics.
        </p>
      </div>

      <Card className="text-center p-16 space-y-4 max-w-2xl mx-auto">
        <div className="p-4 bg-primary-50 dark:bg-primary-950/20 text-primary-600 dark:text-primary-400 rounded-full inline-block">
          <svg className="h-10 w-10 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <div className="space-y-2">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white">Admin Module Locked</h2>
          <p className="text-xs text-gray-500 max-w-md mx-auto">
            This module is reserved for deployment architecture. It is fully routed and ready for future integrations.
          </p>
        </div>
      </Card>
    </div>
  );
};

export default Admin;

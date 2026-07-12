import React from 'react';

export const Admin: React.FC = () => {
  return (
    <div className="p-6 bg-white rounded-lg shadow dark:bg-gray-800">
      <h1 className="text-2xl font-bold mb-4">Administration Console</h1>
      <p className="text-gray-600 dark:text-gray-300">Manage users, system configurations, and view telemetry logs here.</p>
    </div>
  );
};
export default Admin;

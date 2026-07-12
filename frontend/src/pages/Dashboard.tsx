import React from 'react';

export const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="p-6 bg-white rounded-lg shadow dark:bg-gray-800">
        <h1 className="text-2xl font-bold mb-2">Welcome to Cobane Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-300">View code review metrics, trends, and recent submissions here.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 bg-white rounded-lg shadow dark:bg-gray-800">
          <h3 className="text-lg font-medium text-gray-500 mb-2">Total Reviews</h3>
          <span className="text-3xl font-bold">12</span>
        </div>
        <div className="p-6 bg-white rounded-lg shadow dark:bg-gray-800">
          <h3 className="text-lg font-medium text-gray-500 mb-2">Average Complexity</h3>
          <span className="text-3xl font-bold text-green-500">A</span>
        </div>
        <div className="p-6 bg-white rounded-lg shadow dark:bg-gray-800">
          <h3 className="text-lg font-medium text-gray-500 mb-2">Critical Risks Found</h3>
          <span className="text-3xl font-bold text-red-500">0</span>
        </div>
      </div>
    </div>
  );
};
export default Dashboard;

import React from 'react';
import { Button } from '../components/common/Button.tsx';

export const Projects: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-white p-6 rounded-lg shadow dark:bg-gray-800">
        <div>
          <h1 className="text-2xl font-bold">Projects Management</h1>
          <p className="text-gray-600 dark:text-gray-300">Create, upload, or import repositories for AI review.</p>
        </div>
        <Button variant="primary">New Project</Button>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden dark:bg-gray-800">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Project Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Activity</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            <tr>
              <td className="px-6 py-4 text-sm font-medium">demo-python-app</td>
              <td className="px-6 py-4 text-sm text-gray-500">2026-07-11</td>
              <td className="px-6 py-4 text-sm"><span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">Reviewed</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};
export default Projects;

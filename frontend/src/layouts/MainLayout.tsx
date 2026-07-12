import React from 'react';

export const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col dark:bg-gray-900 dark:text-gray-100">
      <div className="flex-1 max-w-7xl w-full mx-auto p-6">
        {children}
      </div>
    </div>
  );
};
export default MainLayout;

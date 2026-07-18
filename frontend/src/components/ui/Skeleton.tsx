import React from 'react';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'rect' | 'circle';
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = '', variant = 'rect' }) => {
  const variantClasses = {
    text: 'h-4 w-full rounded',
    rect: 'h-24 w-full rounded-lg',
    circle: 'h-12 w-12 rounded-full',
  };

  return (
    <div
      className={`animate-pulse bg-gray-200 dark:bg-gray-700 ${variantClasses[variant]} ${className}`}
    ></div>
  );
};

export const SkeletonLoader: React.FC = () => {
  return (
    <div className="space-y-4">
      <Skeleton variant="text" className="w-1/3 h-6" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Skeleton variant="rect" />
        <Skeleton variant="rect" />
        <Skeleton variant="rect" />
      </div>
      <Skeleton variant="rect" className="h-64" />
    </div>
  );
};

export default Skeleton;

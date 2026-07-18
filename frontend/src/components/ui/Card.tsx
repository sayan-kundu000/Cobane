import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hoverable?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, hoverable = false, className = '', ...props }) => {
  return (
    <div
      className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700/80 rounded-xl shadow-sm p-6 overflow-hidden transition-all duration-250 ${
        hoverable ? 'hover:shadow-md hover:border-gray-300 dark:hover:border-gray-600 hover:-translate-y-[2px]' : ''
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;

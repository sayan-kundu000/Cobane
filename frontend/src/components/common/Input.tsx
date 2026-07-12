import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const Input: React.FC<InputProps> = ({ label, ...props }) => {
  return (
    <div className="flex flex-col space-y-1 w-full">
      {label && <label className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</label>}
      <input
        className="px-3 py-2 border rounded focus:ring-2 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-700"
        {...props}
      />
    </div>
  );
};

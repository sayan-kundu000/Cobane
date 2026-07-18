import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'primary', className = '' }) => {
  const baseClasses = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold font-mono tracking-wider uppercase';
  
  const variantClasses = {
    primary: 'bg-primary-50 text-primary-700 border border-primary-200 dark:bg-primary-950/20 dark:text-primary-300 dark:border-primary-900',
    secondary: 'bg-gray-150 text-gray-700 border border-gray-250 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-750',
    success: 'bg-emerald-50 text-emerald-700 border border-emerald-250 dark:bg-emerald-950/20 dark:text-emerald-300 dark:border-emerald-900',
    warning: 'bg-amber-50 text-amber-700 border border-amber-250 dark:bg-amber-950/20 dark:text-amber-300 dark:border-amber-900',
    danger: 'bg-rose-50 text-rose-700 border border-rose-250 dark:bg-rose-950/20 dark:text-rose-300 dark:border-rose-900',
    info: 'bg-sky-50 text-sky-700 border border-sky-250 dark:bg-sky-950/20 dark:text-sky-300 dark:border-sky-900',
  };

  return (
    <span className={`${baseClasses} ${variantClasses[variant]} ${className}`}>
      {children}
    </span>
  );
};

export default Badge;

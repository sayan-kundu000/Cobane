import React from 'react';

interface AlertProps {
  title?: string;
  children: React.ReactNode;
  variant?: 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({ title, children, variant = 'info', className = '' }) => {
  const borderColors = {
    success: 'border-emerald-500 bg-emerald-50 text-emerald-800 dark:bg-emerald-950/20 dark:text-emerald-350 dark:border-emerald-900',
    warning: 'border-amber-500 bg-amber-50 text-amber-800 dark:bg-amber-950/20 dark:text-amber-350 dark:border-amber-900',
    danger: 'border-rose-500 bg-rose-50 text-rose-800 dark:bg-rose-950/20 dark:text-rose-350 dark:border-rose-900',
    info: 'border-sky-500 bg-sky-50 text-sky-800 dark:bg-sky-950/20 dark:text-sky-350 dark:border-sky-900',
  };

  return (
    <div className={`p-4 border-l-4 rounded-r-md ${borderColors[variant]} ${className}`} role="alert">
      {title && <h4 className="text-sm font-bold uppercase tracking-wider mb-1">{title}</h4>}
      <div className="text-sm font-medium">{children}</div>
    </div>
  );
};

export default Alert;

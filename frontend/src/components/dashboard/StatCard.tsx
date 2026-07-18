import React from 'react';
import Card from '../ui/Card.tsx';

interface StatCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  trend?: {
    value: number | string;
    isPositive: boolean;
  };
  icon?: React.ReactNode;
  loading?: boolean;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtext,
  trend,
  icon,
  loading = false,
}) => {
  return (
    <Card hoverable className="relative overflow-hidden">
      {loading ? (
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-250 dark:bg-gray-700 rounded w-1/2"></div>
          <div className="h-8 bg-gray-250 dark:bg-gray-700 rounded w-1/3"></div>
          <div className="h-3 bg-gray-250 dark:bg-gray-700 rounded w-2/3"></div>
        </div>
      ) : (
        <div className="flex justify-between items-start">
          <div className="space-y-2">
            <span className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider block">
              {title}
            </span>
            <div className="flex items-baseline space-x-2">
              <span className="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">
                {value}
              </span>
              {trend && (
                <span
                  className={`text-xs font-bold inline-flex items-center px-1.5 py-0.5 rounded-full ${
                    trend.isPositive
                      ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/20 dark:text-emerald-400'
                      : 'bg-rose-50 text-rose-700 dark:bg-rose-950/20 dark:text-rose-400'
                  }`}
                >
                  {trend.isPositive ? '+' : ''}
                  {trend.value}
                </span>
              )}
            </div>
            {subtext && <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">{subtext}</p>}
          </div>
          {icon && (
            <div className="p-3 bg-primary-50 dark:bg-primary-950/30 rounded-xl text-primary-600 dark:text-primary-400">
              {icon}
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

export default StatCard;

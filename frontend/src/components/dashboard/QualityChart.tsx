import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import Card from '../ui/Card.tsx';

interface ChartDataPoint {
  name: string;
  pylint: number;
  complexity: number;
}

interface QualityChartProps {
  data: ChartDataPoint[];
  title?: string;
  loading?: boolean;
}

export const QualityChart: React.FC<QualityChartProps> = ({
  data,
  title = 'Code Quality Overview',
  loading = false,
}) => {
  return (
    <Card className="h-[350px] flex flex-col justify-between">
      <div className="mb-2">
        <h3 className="text-md font-bold text-gray-900 dark:text-white">{title}</h3>
        <p className="text-xs text-gray-500">Pylint score vs. Maintainability index comparison</p>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <svg className="animate-spin h-8 w-8 text-primary-500" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      ) : data.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-sm text-gray-450 italic">
          No quality metrics available yet.
        </div>
      ) : (
        <div className="flex-1 w-full min-h-0">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data}
              margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:stroke-gray-700" />
              <XAxis
                dataKey="name"
                stroke="#9ca3af"
                fontSize={10}
                tickLine={false}
              />
              <YAxis
                stroke="#9ca3af"
                fontSize={10}
                domain={[0, 100]}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff',
                  fontSize: '12px',
                }}
              />
              <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
              <Line
                name="Pylint Score (x10)"
                type="monotone"
                dataKey="pylint"
                stroke="#5275ff"
                strokeWidth={2.5}
                activeDot={{ r: 6 }}
                dot={{ r: 3 }}
              />
              <Line
                name="Maintainability Index"
                type="monotone"
                dataKey="complexity"
                stroke="#10b981"
                strokeWidth={2.5}
                activeDot={{ r: 6 }}
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
};

export default QualityChart;

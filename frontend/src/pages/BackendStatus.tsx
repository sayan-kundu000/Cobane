import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api.ts';

interface BackendStatusData {
  status: 'green' | 'yellow' | 'red';
  message: string;
  logs: string[];
}

export const BackendStatus: React.FC = () => {
  const [data, setData] = useState<BackendStatusData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const consoleEndRef = useRef<HTMLDivElement>(null);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/health/status');
      if (response.data && response.data.success) {
        setData(response.data.data);
      } else {
        throw new Error("Failed to load valid health envelope");
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to fetch backend status');
    } finally {
      setLoading(false);
    }
  };


  const handleRefresh = async () => {
    try {
      setActionLoading(true);
      setError(null);
      const response = await api.post('/health/refresh');
      if (response.data && response.data.success) {
        setData(response.data.data);
      } else {
        throw new Error("Failed to perform healing refresh");
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Healing request failed');
    } finally {
      setActionLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  useEffect(() => {
    if (consoleEndRef.current) {
      consoleEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [data?.logs]);

  // Color helper for logs
  const getLogLineStyle = (line: string) => {
    if (line.includes('[ERROR]') || line.includes('[CRITICAL]') || line.includes('[FATAL]')) {
      return 'text-red-400 font-semibold';
    }
    if (line.includes('[WARN]')) {
      return 'text-yellow-400 font-semibold';
    }
    if (line.includes('[INFO] [cobane.resolution]')) {
      return 'text-cyan-400 font-medium';
    }
    if (line.includes('[INFO]')) {
      return 'text-green-400';
    }
    return 'text-gray-300';
  };

  // UI state-based styles
  const getStatusStyles = () => {
    if (!data) return { cardBg: 'bg-gray-100', border: 'border-gray-300', text: 'text-gray-800', badge: 'bg-gray-500 text-white', desc: 'Connecting to backend...' };
    switch (data.status) {
      case 'green':
        return {
          cardBg: 'bg-green-50 dark:bg-green-950/20',
          border: 'border-green-500 dark:border-green-600',
          text: 'text-green-800 dark:text-green-300',
          badge: 'bg-green-500 text-white',
          desc: 'Rogers, Wilco! The site or server works very very fine.'
        };
      case 'yellow':
        return {
          cardBg: 'bg-yellow-50 dark:bg-yellow-950/20',
          border: 'border-yellow-500 dark:border-yellow-600',
          text: 'text-yellow-800 dark:text-yellow-300',
          badge: 'bg-yellow-500 text-black',
          desc: 'Pan Pan! There are minor issues but the site or server works very very fine.'
        };
      case 'red':
        return {
          cardBg: 'bg-red-50 dark:bg-red-950/20',
          border: 'border-red-500 dark:border-red-600',
          text: 'text-red-800 dark:text-red-300',
          badge: 'bg-red-500 text-white',
          desc: "Mayday, Mayday, Mayday! There are major issues & the site or server doesn't work very very fine."
        };
      default:
        return {
          cardBg: 'bg-gray-50 dark:bg-gray-950/20',
          border: 'border-gray-500 dark:border-gray-600',
          text: 'text-gray-800 dark:text-gray-300',
          badge: 'bg-gray-500 text-white',
          desc: 'Unknown backend state.'
        };
    }
  };

  const statusStyle = getStatusStyles();

  return (
    <div className="space-y-6">
      {/* Header section */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 dark:bg-gray-800 dark:border-gray-700">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Backend Status</h1>
        <p className="text-gray-600 dark:text-gray-300 mt-1">
          Monitor the current state and execution of the backend server.
        </p>
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Status Card and Simulations */}
        <div className="lg:col-span-1 space-y-6">
          {/* Status Display Card */}
          <div className={`p-6 rounded-lg border-2 shadow-sm ${statusStyle.cardBg} ${statusStyle.border}`}>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
              Backend Status
            </h3>
            
            {loading ? (
              <div className="animate-pulse space-y-3 mt-4">
                <div className="h-8 bg-gray-200 rounded w-3/4 dark:bg-gray-700"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6 dark:bg-gray-700"></div>
              </div>
            ) : data ? (
              <div className="mt-4 space-y-3">
                <div className="flex items-center space-x-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${statusStyle.badge}`}>
                    {data.status.toUpperCase()}
                  </span>
                </div>
                <h2 className={`text-2xl font-extrabold tracking-tight ${statusStyle.text}`}>
                  {data.message}
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  {statusStyle.desc}
                </p>
              </div>
            ) : (
              <p className="text-red-500 mt-4">Could not establish connection to backend server.</p>
            )}
          </div>

          {/* Action Dashboard Controls */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 dark:bg-gray-800 dark:border-gray-700 space-y-4">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Heal & Recovery Panel</h3>
            
            <div className="space-y-3">
              <button
                onClick={handleRefresh}
                disabled={actionLoading || loading}
                className="w-full flex items-center justify-center px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md font-semibold focus:outline-none transition disabled:opacity-50"
              >
                {actionLoading ? (
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                ) : (
                  <svg className="mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 8H17" />
                  </svg>
                )}
                Auto-Heal & Refresh
              </button>
            </div>

            {error && (
              <div className="p-3 bg-red-50 text-red-800 text-xs rounded border border-red-200 dark:bg-red-950/20 dark:text-red-300 dark:border-red-900 mt-2">
                <strong>Error:</strong> {error}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Console Logs */}
        <div className="lg:col-span-2 flex flex-col">
          <div className="bg-gray-900 rounded-lg shadow-sm border border-gray-800 overflow-hidden flex flex-col h-full min-h-[450px]">
            {/* Terminal Header */}
            <div className="bg-gray-950 px-4 py-3 flex items-center justify-between border-b border-gray-800">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                <span className="text-xs font-mono text-gray-400 pl-2">backend - log_streamer.sh</span>
              </div>
              <button
                onClick={fetchStatus}
                className="text-xs text-gray-400 hover:text-white flex items-center font-mono"
              >
                <svg className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 8H17" />
                </svg>
                fetch logs
              </button>
            </div>

            {/* Terminal Output */}
            <div className="p-4 flex-1 font-mono text-xs overflow-y-auto space-y-1 bg-black">
              {loading && !data ? (
                <div className="text-gray-500 animate-pulse">Initializing log streams...</div>
              ) : data && data.logs.length > 0 ? (
                data.logs.map((log, idx) => (
                  <div key={idx} className={`${getLogLineStyle(log)} break-all whitespace-pre-wrap`}>
                    {log}
                  </div>
                ))
              ) : (
                <div className="text-gray-500 italic">No log lines streamed. Check backend port 8000.</div>
              )}
              <div ref={consoleEndRef} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BackendStatus;

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { useTheme } from '../hooks/useTheme.ts';
import { getUserSettings, updateUserSettings } from '../services/settings.ts';
import Card from '../components/ui/Card.tsx';
import { Button } from '../components/common/Button.tsx';

export const Settings: React.FC = () => {
  const queryClient = useQueryClient();
  const { setTheme } = useTheme();

  const [notification, setNotification] = useState(true);
  const [activeTheme, setActiveTheme] = useState<'light' | 'dark' | 'neon'>('light');

  // Query settings from server
  const { data: settingsRes, isLoading } = useQuery({
    queryKey: ['user-settings'],
    queryFn: getUserSettings,
  });

  useEffect(() => {
    if (settingsRes?.data) {
      setNotification(settingsRes.data.receiving_notifications);
      setActiveTheme(settingsRes.data.theme);
      // Sync local context theme
      setTheme(settingsRes.data.theme);
    }
  }, [settingsRes, setTheme]);

  // Mutation to update settings
  const settingsMutation = useMutation({
    mutationFn: updateUserSettings,
    onSuccess: (res) => {
      if (res.success && res.data) {
        toast.success('Preferences saved successfully!');
        queryClient.invalidateQueries({ queryKey: ['user-settings'] });
      }
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.message || err.message || 'Failed to update preferences.');
    },
  });

  const handleSave = () => {
    settingsMutation.mutate({
      theme: activeTheme,
      receiving_notifications: notification,
    });
  };

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'neon') => {
    setActiveTheme(newTheme);
    setTheme(newTheme); // Apply theme immediately in UI
  };

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div className="p-6 bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 rounded-2xl shadow-sm">
        <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          System Preferences
        </h1>
        <p className="text-sm text-gray-550 mt-1">
          Customize code reviews triggers, dashboard color modes, and audit report notifications.
        </p>
      </div>

      {isLoading ? (
        <div className="animate-pulse space-y-4">
          <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded-xl"></div>
          <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded-xl"></div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Theme toggling widget */}
          <Card className="space-y-4">
            <div>
              <h3 className="text-sm font-bold text-gray-950 dark:text-white uppercase tracking-wider">
                Interface Color Palette
              </h3>
              <p className="text-xs text-gray-500">Select application visual presentation mode</p>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <button
                type="button"
                onClick={() => handleThemeChange('light')}
                className={`p-4 border-2 rounded-none text-center font-bold text-xs uppercase tracking-wider transition ${
                  activeTheme === 'light'
                    ? 'border-primary-500 bg-primary-50/20 text-primary-600 dark:bg-primary-950/20'
                    : 'border-gray-200 dark:border-gray-700 text-gray-550 hover:border-gray-300'
                }`}
              >
                ☀️ Light
              </button>
              <button
                type="button"
                onClick={() => handleThemeChange('dark')}
                className={`p-4 border-2 rounded-none text-center font-bold text-xs uppercase tracking-wider transition ${
                  activeTheme === 'dark'
                    ? 'border-primary-500 bg-primary-50/20 text-primary-600 dark:bg-primary-950/20'
                    : 'border-gray-200 dark:border-gray-700 text-gray-550 hover:border-gray-300'
                }`}
              >
                🌙 Dark
              </button>
              <button
                type="button"
                onClick={() => handleThemeChange('neon')}
                className={`p-4 border-2 rounded-none text-center font-bold text-xs uppercase tracking-wider transition ${
                  activeTheme === 'neon'
                    ? 'border-primary-500 bg-primary-50/20 text-primary-600 dark:bg-primary-950/20'
                    : 'border-gray-200 dark:border-gray-700 text-gray-550 hover:border-gray-300'
                }`}
              >
                ⚡ Neon
              </button>
            </div>
          </Card>

          {/* Notifications config */}
          <Card className="space-y-4">
            <div>
              <h3 className="text-sm font-bold text-gray-950 dark:text-white uppercase tracking-wider">
                Notification Stream
              </h3>
              <p className="text-xs text-gray-550">Configure how you receive review reports alerts</p>
            </div>

            <div className="flex items-center space-x-3">
              <input
                id="notifications-toggle"
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                checked={notification}
                onChange={(e) => setNotification(e.target.checked)}
              />
              <label htmlFor="notifications-toggle" className="text-xs font-bold text-gray-700 dark:text-gray-350 cursor-pointer">
                Enable desktop reports notifications on review completions
              </label>
            </div>
          </Card>

          {/* Submit Actions */}
          <div className="flex justify-end pt-2">
            <Button
              onClick={handleSave}
              disabled={settingsMutation.isPending}
              className="font-bold px-6 py-2.5 h-11 rounded-none"
            >
              {settingsMutation.isPending ? 'Saving...' : 'Save Settings'}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;

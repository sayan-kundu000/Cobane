import api from './api.ts';
import { ApiResponse, UserPreference } from '../types';

export const getUserSettings = async (): Promise<ApiResponse<UserPreference>> => {
  const response = await api.get('/settings/user');
  return response.data;
};

export const updateUserSettings = async (settingsData: {
  theme?: 'light' | 'dark' | 'neon';
  receiving_notifications?: boolean;
}): Promise<ApiResponse<UserPreference>> => {
  const response = await api.put('/settings/user', settingsData);
  return response.data;
};

export const getSystemSettings = async (): Promise<ApiResponse<{
  app_name: string;
  system_version: string;
  features: {
    pylint: boolean;
    bandit: boolean;
    radon: boolean;
    ai_review: boolean;
  };
}>> => {
  const response = await api.get('/settings/system');
  return response.data;
};

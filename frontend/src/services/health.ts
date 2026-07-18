import api from './api.ts';
import { ApiResponse } from '../types';

export interface BackendStatusData {
  status: 'green' | 'yellow' | 'red';
  message: string;
  logs: string[];
}

export const getBackendStatus = async (): Promise<ApiResponse<BackendStatusData>> => {
  const response = await api.get('/health/status');
  return response.data;
};

export const triggerRefresh = async (): Promise<ApiResponse<BackendStatusData>> => {
  const response = await api.post('/health/refresh');
  return response.data;
};

import api from './api.ts';
import { ApiResponse, Report } from '../types';

export const listReports = async (): Promise<ApiResponse<Report[]>> => {
  const response = await api.get('/reports');
  return response.data;
};

export const getReportDetails = async (reportId: number): Promise<ApiResponse<Report>> => {
  const response = await api.get(`/reports/${reportId}`);
  return response.data;
};

export const downloadReportFile = async (
  reportId: number
): Promise<ApiResponse<{ message: string; download_url: string; format: string }>> => {
  const response = await api.get(`/reports/${reportId}/download`);
  return response.data;
};

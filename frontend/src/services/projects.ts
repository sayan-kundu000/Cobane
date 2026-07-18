import api from './api.ts';
import { ApiResponse, Project, ProjectStats, PaginatedResponse, UploadedSource } from '../types';

export const listProjects = async (params?: {
  page?: number;
  page_size?: number;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  language?: string;
}): Promise<ApiResponse<PaginatedResponse<Project>>> => {
  const response = await api.get('/projects', { params });
  return response.data;
};

export const getProject = async (projectId: number): Promise<ApiResponse<Project>> => {
  const response = await api.get(`/projects/${projectId}`);
  return response.data;
};

export const createProject = async (projectData: { name: string; description?: string }): Promise<ApiResponse<Project>> => {
  const response = await api.post('/projects', projectData);
  return response.data;
};

export const updateProject = async (projectId: number, projectData: { name?: string; description?: string }): Promise<ApiResponse<Project>> => {
  const response = await api.put(`/projects/${projectId}`, projectData);
  return response.data;
};

export const deleteProject = async (projectId: number): Promise<ApiResponse<{ message: string }>> => {
  const response = await api.delete(`/projects/${projectId}`);
  return response.data;
};

export const getProjectStats = async (projectId: number): Promise<ApiResponse<ProjectStats>> => {
  const response = await api.get(`/projects/${projectId}/stats`);
  return response.data;
};

export const uploadProjectFile = async (
  projectId: number,
  file: File
): Promise<ApiResponse<UploadedSource>> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post(`/projects/${projectId}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

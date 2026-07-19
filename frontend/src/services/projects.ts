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

export const listProjectSources = async (projectId: number): Promise<ApiResponse<UploadedSource[]>> => {
  const response = await api.get(`/projects/${projectId}/sources`);
  return response.data;
};

export interface ProjectSourceContent {
  id: number;
  project_id: number;
  filename: string;
  language: string;
  content: string;
}

export const getProjectSourceContent = async (
  projectId: number,
  sourceId: number
): Promise<ApiResponse<ProjectSourceContent>> => {
  const response = await api.get(`/projects/${projectId}/sources/${sourceId}`);
  return response.data;
};

export const updateProjectSourceContent = async (
  projectId: number,
  sourceId: number,
  content: string
): Promise<ApiResponse<ProjectSourceContent>> => {
  const response = await api.put(`/projects/${projectId}/sources/${sourceId}`, { content });
  return response.data;
};

export interface ProjectSourceRunResponse {
  stdout: string;
  stderr: string;
  exit_code: number;
}

export const runProjectSource = async (
  projectId: number,
  sourceId: number
): Promise<ApiResponse<ProjectSourceRunResponse>> => {
  const response = await api.post(`/projects/${projectId}/sources/${sourceId}/run`);
  return response.data;
};

export const deleteProjectSource = async (
  projectId: number,
  sourceId: number
): Promise<ApiResponse<{ message: string }>> => {
  const response = await api.delete(`/projects/${projectId}/sources/${sourceId}`);
  return response.data;
};



import api from './api.ts';
import { ApiResponse, User, UserProfile } from '../types';

export const loginUser = async (credentials: any): Promise<ApiResponse<any>> => {
  const response = await api.post('/auth/login', credentials);
  return response.data;
};

export const registerUser = async (userData: any): Promise<ApiResponse<User>> => {
  const response = await api.post('/auth/register', userData);
  return response.data;
};

export const logoutUser = async (): Promise<ApiResponse<{ message: string }>> => {
  const response = await api.post('/auth/logout');
  return response.data;
};

export const forgotPassword = async (data: { email: string }): Promise<ApiResponse<{ message: string }>> => {
  const response = await api.post('/auth/forgot-password', data);
  return response.data;
};

export const resetPassword = async (data: any): Promise<ApiResponse<{ message: string }>> => {
  const response = await api.post('/auth/reset-password', data);
  return response.data;
};

export const getMe = async (): Promise<ApiResponse<User>> => {
  const response = await api.get('/users/me');
  return response.data;
};

export const updateProfile = async (profileData: { full_name?: string; bio?: string }): Promise<ApiResponse<UserProfile>> => {
  const response = await api.put('/users/me/profile', profileData);
  return response.data;
};

export const changePassword = async (pwdData: any): Promise<ApiResponse<{ message: string }>> => {
  const response = await api.put('/users/me/password', pwdData);
  return response.data;
};

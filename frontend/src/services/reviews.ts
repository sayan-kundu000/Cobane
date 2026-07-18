import api from './api.ts';
import { ApiResponse, Review, ReviewFinding, ReviewMetrics, Report, PaginatedResponse } from '../types';

export const listReviews = async (params?: {
  project_id?: number;
  page?: number;
  page_size?: number;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  language?: string;
}): Promise<ApiResponse<PaginatedResponse<Review>>> => {
  const response = await api.get('/reviews', { params });
  return response.data;
};

export const getReview = async (reviewId: number): Promise<ApiResponse<Review>> => {
  const response = await api.get(`/reviews/${reviewId}`);
  return response.data;
};

export const createReview = async (reviewData: {
  project_id: number;
  uploaded_source_id?: number;
}): Promise<ApiResponse<Review>> => {
  const response = await api.post('/reviews', reviewData);
  return response.data;
};

export const deleteReview = async (reviewId: number): Promise<ApiResponse<{ message: string }>> => {
  const response = await api.delete(`/reviews/${reviewId}`);
  return response.data;
};

export const getReviewFindings = async (reviewId: number): Promise<ApiResponse<ReviewFinding[]>> => {
  const response = await api.get(`/reviews/${reviewId}/findings`);
  return response.data;
};

export const getReviewMetrics = async (reviewId: number): Promise<ApiResponse<ReviewMetrics>> => {
  const response = await api.get(`/reviews/${reviewId}/metrics`);
  return response.data;
};

export const getReviewReports = async (reviewId: number): Promise<ApiResponse<Report[]>> => {
  const response = await api.get(`/reviews/${reviewId}/reports`);
  return response.data;
};

export interface ReviewCodeContent {
  id: number;
  filename: string;
  language: string;
  content: string;
}

export const getReviewCodeContent = async (reviewId: number): Promise<ApiResponse<ReviewCodeContent>> => {
  const response = await api.get(`/reviews/${reviewId}/code`);
  return response.data;
};

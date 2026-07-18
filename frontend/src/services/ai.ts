import api from './api.ts';
import { ApiResponse } from '../types';

export interface AIConfig {
  provider: string;
  base_url: string;
  model_engine: string;
  temperature: number;
  max_tokens: number;
}

export interface AIPromptTemplate {
  name: string;
  description: string;
}

export const getAIConfig = async (): Promise<ApiResponse<AIConfig>> => {
  const response = await api.get('/ai/config');
  return response.data;
};

export const getAIPrompts = async (): Promise<ApiResponse<{ templates: AIPromptTemplate[] }>> => {
  const response = await api.get('/ai/prompts');
  return response.data;
};

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  project_id?: number;
  review_id?: number;
  message: string;
  history?: ChatMessage[];
}

export interface ChatResponse {
  response: string;
}

export const sendChatMessage = async (payload: ChatRequest): Promise<ApiResponse<ChatResponse>> => {
  const response = await api.post('/ai/chat', payload);
  return response.data;
};

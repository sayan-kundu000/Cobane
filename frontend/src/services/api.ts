import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL
    ? (import.meta.env.VITE_API_URL.endsWith('/api/v1')
        ? import.meta.env.VITE_API_URL
        : `${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api/v1`)
    : '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;

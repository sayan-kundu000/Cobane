import axios from 'axios';

let resolvedBaseUrl = '/api/v1';
if (import.meta.env.VITE_API_URL) {
  let url = import.meta.env.VITE_API_URL.trim();
  // Prepend protocol if it is a domain name without one
  if (!url.startsWith('/') && !/^https?:\/\//i.test(url)) {
    url = `https://${url}`;
  }
  // Append /api/v1 if not already present
  if (!url.endsWith('/api/v1')) {
    url = `${url.replace(/\/$/, '')}/api/v1`;
  }
  resolvedBaseUrl = url;
}

const api = axios.create({
  baseURL: resolvedBaseUrl,
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

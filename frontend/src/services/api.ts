import axios from 'axios';

let resolvedBaseUrl = '/api/v1';
if (import.meta.env.VITE_API_URL && import.meta.env.VITE_API_URL !== 'undefined' && import.meta.env.VITE_API_URL !== 'null') {
  let url = import.meta.env.VITE_API_URL.trim();

  // If the host is Render's internal host name (no dots and not localhost),
  // map it to the public Render subdomain.
  if (!url.startsWith('/') && !url.startsWith('//') && !/^https?:\/\//i.test(url)) {
    if (!url.includes('.') && !url.includes('localhost')) {
      url = `${url}.onrender.com`;
    }
    // Prepend double slash to make it protocol-relative
    url = `//${url}`;
  } else if (/^https?:\/\//i.test(url)) {
    // Make absolute URL protocol-relative
    url = url.replace(/^https?:\/\//i, '//');
  }

  // Convert protocol-relative // to a full protocol in non-browser environments
  if (url.startsWith('//') && typeof window === 'undefined') {
    url = `https:${url}`;
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

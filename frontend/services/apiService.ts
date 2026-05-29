import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { getAccessToken, refreshAccessToken } from './UserService';

export const resolveApiUrl = (): string => {
  const rawUrl = process.env.NEXT_PUBLIC_API_URL?.trim();
  const resolved = rawUrl || 'http://localhost:8000';
  return resolved.replace(/\/+$/, '');
};

const API_URL = resolveApiUrl();


export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

type RetryableRequestConfig = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

const isRefreshRequest = (url?: string): boolean => {
  if (!url) {
    return false;
  }
  return url.includes('/auth/tokens/refresh') || url.includes('/refresh');
};

// Add request interceptor to automatically add access token
api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Update the interceptor to use our UserService refresh function
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableRequestConfig | undefined;

    if (!originalRequest) {
      return Promise.reject(error);
    }

    // Network error (no response) means the server is down or sleeping
    if (!error.response && typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('server:down'));
    }

    console.debug("Intercepting 401 response")

    // Never retry refresh endpoints to avoid recursive refresh loops.
    if (isRefreshRequest(originalRequest.url)) {
      return Promise.reject(error);
    }

    // Prevent infinite retry loops
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
          // Update the token in the failed request and retry
          const token = getAccessToken();
          if (token) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }

          console.debug("Successfully refreshed")
          return api(originalRequest);
        }
      } catch (refreshError) {
        // If refresh fails, let the error propagate
      }
    }
    return Promise.reject(error);
  }
);
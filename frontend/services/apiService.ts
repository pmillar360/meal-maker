import axios from 'axios';
import { getAccessToken, refreshAccessToken } from './UserService';

// Connect to localhost:8000 if NEXT_PUBLIC_API_URL is not provided
const API_URL = process.env.NEXT_PUBLIC_API_URL 
  ? `${process.env.NEXT_PUBLIC_API_URL}:8000`
  : 'http://localhost:8000';


export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

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
  async (error) => {
    const originalRequest = error.config;
    console.log("Intercepting 401 response")
    // Prevent infinite retry loops
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
          // Update the token in the failed request and retry
          originalRequest.headers.Authorization = `Bearer ${getAccessToken()}`;

          console.log("Successfully refreshed")
          return api(originalRequest);
        }
      } catch (refreshError) {
        // If refresh fails, let the error propagate
      }
    }
    return Promise.reject(error);
  }
);
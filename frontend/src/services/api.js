import axios from 'axios';
import authService from './auth.service';
import apiConfig from '../config/api.config';

const api = axios.create({
  baseURL: apiConfig.apiBaseUrl,
  timeout: apiConfig.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Add token to request headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // For FormData, remove Content-Type to let browser set it with boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Handle token expiration
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;
    const url = originalRequest?.url || '';

    // If 401 from auth endpoints (login/register) just pass through
    if (status === 401 && (url.includes('/auth/login') || url.includes('/auth/register'))) {
      return Promise.reject(error); // let caller handle error message
    }

    // Refresh logic only if:
    // - 401
    // - Not already retried
    // - Not refresh endpoint itself
    // - We have a refresh token stored
    if (
      status === 401 &&
      !originalRequest._retry &&
      !url.includes('/auth/refresh') &&
      localStorage.getItem('refresh_token')
    ) {
      originalRequest._retry = true;
      try {
        const refreshResult = await authService.refreshToken();
        if (!refreshResult.success) throw new Error('Token refresh failed');
        const newToken = localStorage.getItem('access_token');
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Clear tokens and only redirect if not already on login page
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Helper function to create audio URL for playback
export const createAudioUrl = (jobId, isVoiceClone = false) => {
  const token = localStorage.getItem('access_token');
  const endpoint = isVoiceClone ? `/file/voice-clone/${jobId}` : `/file/synthesis/${jobId}`;
  return `${api.defaults.baseURL}${endpoint}?token=${token}`;
};

export default api;
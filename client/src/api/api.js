import axios from 'axios';
import { getAccessToken, refreshAccessToken, clearAccessToken } from '../services/AuthService';

const API = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL, // Use REACT_APP_ prefix
  withCredentials: true, // Allow Axios to send HttpOnly cookies
});

// Request Interceptor to attach the access token to headers
API.interceptors.request.use(
  (config) => {
    const accessToken = getAccessToken(); // Function to get the access token
    if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor to handle token refresh
API.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes('/auth/refresh')
    ) {
      originalRequest._retry = true;
      try {
        const newAccessToken = await refreshAccessToken();
        if (newAccessToken) {
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
          return API(originalRequest);
        }
      } catch (refreshError) {
        console.error('Error refreshing token:', refreshError);
        clearAccessToken();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default API;

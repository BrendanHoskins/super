import API from '../api/api';

let inMemoryToken = null;

export const setAccessToken = (token) => {
  inMemoryToken = token;
  localStorage.setItem('accessToken', token);
};

export const getAccessToken = () => {
  if (!inMemoryToken) {
    inMemoryToken = localStorage.getItem('accessToken');
  }
  return inMemoryToken;
};

export const clearAccessToken = () => {
  inMemoryToken = null;
  localStorage.removeItem('accessToken');
};

export const login = async (username, password) => {
  try {
    const response = await API.post('/auth/login', { username, password });
    const accessToken = response.data.access_token;
    setAccessToken(accessToken);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get a new access token using the refresh cookie.
 * @param {Object} options
 * @param {boolean} options.redirectOnFailure - If true (default), redirect to /login on failure. If false, caller handles (e.g. PrivateRoute).
 */
export const refreshAccessToken = async (options = {}) => {
  const { redirectOnFailure = true } = options;
  try {
    const response = await API.post('/auth/refresh', {}, {
      withCredentials: true
    });
    const accessToken = response.data.access_token;
    setAccessToken(accessToken);
    return accessToken;
  } catch (error) {
    console.error('Error refreshing token:', error);
    clearAccessToken();
    if (redirectOnFailure) {
      window.location.href = '/login';
    }
    throw error;
  }
};

export const logout = async () => {
  try {
    await API.post('/auth/logout', {}, {
      withCredentials: true // Ensure cookies are sent with the request
    });
  } catch (error) {
    console.error('Error during logout:', error);
  } finally {
    clearAccessToken();
  }
};

/** Restore session from refresh cookie when there's no access token (e.g. after closing tab). Does not redirect on failure. */
export const initializeAuth = async () => {
  const token = getAccessToken();
  if (!token) {
    try {
      return await refreshAccessToken({ redirectOnFailure: false });
    } catch (error) {
      return null;
    }
  }
  return token;
};

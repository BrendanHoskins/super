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

// Update the refreshAccessToken function
export const refreshAccessToken = async () => {
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
    // Redirect to login page or handle authentication failure
    window.location.href = '/login';
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

export const initializeAuth = async () => {
  const token = getAccessToken();
  if (!token) {
    try {
      const newToken = await refreshAccessToken();
      return newToken;
    } catch (error) {
      console.error('Failed to initialize auth:', error);
      await logout();
      return null;
    }
  }
  return token;
};

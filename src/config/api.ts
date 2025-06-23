
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  ENDPOINTS: {
    AUTH: {
      REQUEST_MAGIC_LINK: '/api/v1/auth/request-magic-link',
      VERIFY_TOKEN: '/api/v1/auth/verify-token',
    },
    UPLOADS: '/api/v1/uploads/',
    ANALYSIS: {
      STATUS: '/api/v1/analysis/{job_id}/status',
      START: '/api/v1/analysis/start',
    },
    INSIGHTS: '/api/v1/insights/{user_id}',
    USER: '/api/v1/user/profile',
  },
};

export const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

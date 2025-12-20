
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  ENDPOINTS: {
    AUTH: {
      LOGIN: '/api/v1/auth/login',
      REGISTER: '/api/v1/auth/register',
      REFRESH: '/api/v1/auth/refresh',
      LOGOUT: '/api/v1/auth/logout',
      ME: '/api/v1/auth/me',
      PROFILE: '/api/v1/auth/profile',
      CHANGE_PASSWORD: '/api/v1/auth/change-password',
    },
    GLUCOSE: {
      READINGS: '/api/v1/glucose/readings',
      BULK: '/api/v1/glucose/bulk',
    },
    SLEEP: '/api/v1/sleep',
    MEALS: '/api/v1/meals',
    ACTIVITIES: '/api/v1/activities',
    UPLOADS: '/api/v1/uploads/',
    ANALYSIS: {
      STATUS: '/api/v1/analysis/{job_id}/status',
      START: '/api/v1/analysis/start',
    },
    INSIGHTS: {
      CORRELATIONS: '/api/v1/insights/correlations',
      PATTERNS: '/api/v1/insights/patterns',
      DASHBOARD: '/api/v1/insights/dashboard',
      TRIGGER_ANALYSIS: '/api/v1/insights/trigger-analysis',
    },
    ADVANCED_INSIGHTS: {
      PCMCI: '/api/v1/advanced_insights/pcmci',
      RUN_PCMCI: '/api/v1/advanced_insights/run_pcmci',
      STUMPY_PATTERNS: '/api/v1/advanced_insights/stumpy_patterns',
      RUN_STUMPY: '/api/v1/advanced_insights/run_stumpy',
    },
    USER: '/api/v1/user/profile',
  },
};

export const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

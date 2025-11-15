/**
 * API Configuration for Frontend
 *
 * This file provides environment-aware API configuration.
 * Copy to your frontend's config/api.js or similar.
 */

// Detect environment and framework
const getEnvVar = (name) => {
  // Vite
  if (typeof import.meta !== 'undefined' && import.meta.env) {
    return import.meta.env[name];
  }
  // Next.js / CRA
  if (typeof process !== 'undefined' && process.env) {
    return process.env[name];
  }
  return undefined;
};

// API Configuration
export const API_CONFIG = {
  // Base URL for API requests
  baseURL:
    getEnvVar('VITE_API_URL') ||
    getEnvVar('NEXT_PUBLIC_API_URL') ||
    getEnvVar('REACT_APP_API_URL') ||
    getEnvVar('NG_APP_API_URL') ||
    'http://localhost:8000/api/v1',

  // API base (without /api/v1)
  apiBase:
    getEnvVar('VITE_API_BASE') ||
    getEnvVar('NEXT_PUBLIC_API_BASE') ||
    getEnvVar('REACT_APP_API_BASE') ||
    'http://localhost:8000',

  // Request timeout (ms)
  timeout: 30000,

  // Retry configuration
  retry: {
    attempts: 3,
    delay: 1000,
  },

  // Enable logging in development
  debug: process.env.NODE_ENV === 'development',
};

// API Endpoints
export const API_ENDPOINTS = {
  // Glucose
  glucose: {
    list: '/glucose/readings',
    create: '/glucose/readings',
    bulk: '/glucose/bulk',
  },

  // Sleep
  sleep: {
    create: '/sleep',
  },

  // Activities
  activities: {
    create: '/activities',
  },

  // Meals
  meals: {
    create: '/meals',
  },

  // Insights
  insights: {
    correlations: '/insights/correlations',
    patterns: '/insights/patterns',
    dashboard: '/insights/dashboard',
    triggerAnalysis: '/insights/trigger-analysis',
  },

  // Health check
  health: '/health',
};

// Helper to build full URL
export const buildURL = (endpoint, params = {}) => {
  const url = new URL(endpoint, API_CONFIG.baseURL);
  Object.keys(params).forEach(key => {
    if (params[key] !== undefined && params[key] !== null) {
      url.searchParams.append(key, params[key]);
    }
  });
  return url.toString();
};

export default API_CONFIG;

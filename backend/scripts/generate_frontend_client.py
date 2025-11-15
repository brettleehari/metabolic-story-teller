"""
GlucoLens API Client for Frontend Integration

TypeScript/JavaScript client for connecting to the GlucoLens backend API.
Compatible with React, Next.js, Vue, and vanilla JavaScript.

Usage:
    import { GlucoLensAPI } from './api-client';

    const api = new GlucoLensAPI('http://localhost:8000');
    const readings = await api.glucose.getReadings();
"""

from typing import TypedDict, List, Optional
from datetime import datetime


# TypeScript Types (copy to your frontend)
TYPESCRIPT_TYPES = """
// ============ API Types ============

export interface GlucoseReading {
  id: number;
  user_id: string;
  timestamp: string;
  value: number;
  source?: string;
  device_id?: string;
  created_at: string;
}

export interface GlucoseReadingCreate {
  timestamp: string;
  value: number;
  source?: string;
  device_id?: string;
}

export interface SleepData {
  id: number;
  user_id: string;
  date: string;
  sleep_start: string;
  sleep_end: string;
  duration_minutes?: number;
  deep_sleep_minutes?: number;
  rem_sleep_minutes?: number;
  light_sleep_minutes?: number;
  awake_minutes?: number;
  quality_score?: number;
  source?: string;
  created_at: string;
}

export interface Activity {
  id: number;
  user_id: string;
  timestamp: string;
  activity_type?: string;
  duration_minutes?: number;
  intensity?: 'light' | 'moderate' | 'vigorous';
  calories_burned?: number;
  heart_rate_avg?: number;
  source?: string;
  created_at: string;
}

export interface Meal {
  id: number;
  user_id: string;
  timestamp: string;
  meal_type?: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  carbs_grams?: number;
  protein_grams?: number;
  fat_grams?: number;
  calories?: number;
  glycemic_load?: number;
  description?: string;
  photo_url?: string;
  source?: string;
  created_at: string;
}

export interface Correlation {
  id: number;
  factor_x: string;
  factor_y: string;
  correlation_coefficient: number;
  p_value: number;
  lag_days: number;
  sample_size: number;
  confidence_level: 'high' | 'medium' | 'low';
  computed_at: string;
}

export interface Pattern {
  id: number;
  pattern_type: string;
  description: string;
  confidence?: number;
  support?: number;
  occurrences: number;
  example_dates: string[];
  metadata?: Record<string, any>;
  discovered_at: string;
}

export interface DashboardSummary {
  period_days: number;
  avg_glucose: number;
  time_in_range_percent: number;
  avg_sleep_hours?: number;
  total_exercise_minutes?: number;
  top_correlations: Correlation[];
  recent_patterns: Pattern[];
}
"""


# JavaScript API Client (copy to your frontend)
JAVASCRIPT_CLIENT = """
// ============ API Client ============

class GlucoLensAPI {
  constructor(baseURL = 'http://localhost:8000/api/v1') {
    this.baseURL = baseURL;
  }

  // Helper method for fetch requests
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'API request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // ======== Glucose Endpoints ========

  async getGlucoseReadings(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/glucose/readings?${queryString}`);
  }

  async createGlucoseReading(reading) {
    return this.request('/glucose/readings', {
      method: 'POST',
      body: JSON.stringify(reading),
    });
  }

  async bulkUploadGlucose(readings) {
    return this.request('/glucose/bulk', {
      method: 'POST',
      body: JSON.stringify({ readings }),
    });
  }

  // ======== Sleep Endpoints ========

  async createSleepData(sleepData) {
    return this.request('/sleep', {
      method: 'POST',
      body: JSON.stringify(sleepData),
    });
  }

  // ======== Activity Endpoints ========

  async createActivity(activity) {
    return this.request('/activities', {
      method: 'POST',
      body: JSON.stringify(activity),
    });
  }

  // ======== Meal Endpoints ========

  async createMeal(meal) {
    return this.request('/meals', {
      method: 'POST',
      body: JSON.stringify(meal),
    });
  }

  // ======== Insights Endpoints ========

  async getCorrelations(limit = 10) {
    return this.request(`/insights/correlations?limit=${limit}`);
  }

  async getPatterns(limit = 10) {
    return this.request(`/insights/patterns?limit=${limit}`);
  }

  async getDashboard(periodDays = 7) {
    return this.request(`/insights/dashboard?period_days=${periodDays}`);
  }

  async triggerAnalysis() {
    return this.request('/insights/trigger-analysis', {
      method: 'POST',
    });
  }
}

// Export for use in modules
export default GlucoLensAPI;

// For CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GlucoLensAPI;
}
"""


# React Hook Example
REACT_HOOK = """
// ============ React Hook Example ============

import { useState, useEffect } from 'react';
import GlucoLensAPI from './api-client';

const api = new GlucoLensAPI();

export function useGlucoseReadings(params = {}) {
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchReadings() {
      try {
        setLoading(true);
        const data = await api.getGlucoseReadings(params);
        setReadings(data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchReadings();
  }, [JSON.stringify(params)]);

  return { readings, loading, error };
}

export function useDashboard(periodDays = 7) {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchDashboard() {
      try {
        setLoading(true);
        const data = await api.getDashboard(periodDays);
        setDashboard(data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchDashboard();
  }, [periodDays]);

  return { dashboard, loading, error };
}

// Usage in component:
// const { readings, loading, error } = useGlucoseReadings({ limit: 100 });
// const { dashboard } = useDashboard(7);
"""


if __name__ == "__main__":
    # Write files
    print("Generating frontend integration files...")

    with open("typescript-types.ts", "w") as f:
        f.write(TYPESCRIPT_TYPES)

    with open("api-client.js", "w") as f:
        f.write(JAVASCRIPT_CLIENT)

    with open("react-hooks.js", "w") as f:
        f.write(REACT_HOOK)

    print("✅ Generated:")
    print("  - typescript-types.ts")
    print("  - api-client.js")
    print("  - react-hooks.js")

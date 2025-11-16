// Demo Service - API client for AWS Lambda read-only demo
import { getDemoApiUrl, DEMO_USERS, DemoUser } from '@/config/demo';

// Base fetch wrapper for demo API
async function demoFetch<T>(endpoint: string): Promise<T> {
  const baseUrl = getDemoApiUrl();
  const url = `${baseUrl}${endpoint}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Demo API error: ${response.statusText}`);
  }

  return await response.json();
}

// Demo user profile response
export interface DemoUserProfile {
  id: string;
  email: string;
  full_name: string;
  age: number;
  created_at: string;
}

// Glucose reading
export interface GlucoseReading {
  id: number;
  user_id: string;
  timestamp: string;
  value: number;
  source: string;
}

// Correlation data
export interface Correlation {
  factor_type: string;
  factor_name: string;
  correlation: number;
  abs_correlation: number;
  p_value: number;
  sample_size: number;
  interpretation: string;
}

// Pattern data
export interface Pattern {
  id: number;
  antecedents: string[];
  consequents: string[];
  support: number;
  confidence: number;
  lift: number;
  conviction: number;
  interpretation: string;
}

// Dashboard data
export interface DashboardData {
  period: string;
  glucose_stats: {
    avg: number;
    min: number;
    max: number;
    std_dev: number;
    time_in_range_70_180: number;
    time_below_70: number;
    time_above_180: number;
  };
  correlations: Correlation[];
  patterns: Pattern[];
  recent_insights: any[];
}

// Combined insights
export interface CombinedInsights {
  user: DemoUserProfile;
  correlations: Correlation[];
  patterns: Pattern[];
  glucose_summary: {
    total_readings: number;
    avg_glucose: number;
    time_in_range: number;
  };
}

class DemoService {
  // Get all demo user profiles
  async getDemoUsers(): Promise<DemoUser[]> {
    try {
      const profiles = await demoFetch<DemoUserProfile[]>('/users');
      // Merge with local demo user data for full profile
      return DEMO_USERS.filter(user =>
        profiles.some(p => p.id === user.id)
      );
    } catch (error) {
      console.error('Error fetching demo users:', error);
      // Fallback to local data
      return DEMO_USERS;
    }
  }

  // Get combined insights for a user
  async getInsights(userId: string): Promise<CombinedInsights> {
    return demoFetch<CombinedInsights>(`/insights/${userId}`);
  }

  // Get correlations for a user
  async getCorrelations(userId: string, limit: number = 10): Promise<Correlation[]> {
    return demoFetch<Correlation[]>(`/correlations/${userId}?limit=${limit}`);
  }

  // Get patterns for a user
  async getPatterns(userId: string, minConfidence: number = 0.5): Promise<Pattern[]> {
    return demoFetch<Pattern[]>(`/patterns/${userId}?min_confidence=${minConfidence}`);
  }

  // Get dashboard data
  async getDashboard(userId: string, period: '7' | '30' | '90' = '30'): Promise<DashboardData> {
    return demoFetch<DashboardData>(`/dashboard/${userId}?period=${period}`);
  }

  // Get glucose readings
  async getGlucoseReadings(
    userId: string,
    startDate?: string,
    endDate?: string,
    limit: number = 1000
  ): Promise<GlucoseReading[]> {
    let url = `/glucose/readings/${userId}?limit=${limit}`;
    if (startDate) url += `&start_date=${startDate}`;
    if (endDate) url += `&end_date=${endDate}`;
    return demoFetch<GlucoseReading[]>(url);
  }

  // Health check
  async healthCheck(): Promise<{ status: string; message: string }> {
    try {
      return await demoFetch<{ status: string; message: string }>('/');
    } catch (error) {
      return { status: 'error', message: 'Demo API unavailable' };
    }
  }
}

// Export singleton instance
export const demoService = new DemoService();

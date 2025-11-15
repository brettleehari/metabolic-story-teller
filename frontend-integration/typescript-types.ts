
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

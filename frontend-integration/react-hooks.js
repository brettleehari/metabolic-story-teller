
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

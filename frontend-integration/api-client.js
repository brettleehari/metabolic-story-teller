
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

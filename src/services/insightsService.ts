
import { API_CONFIG, getAuthHeaders } from '@/config/api';

export interface Insight {
  id: string;
  title: string;
  pattern: string;
  confidence: number;
  description: string;
  actionable: string;
  data_points: number;
  correlation: number;
  chart_data?: any;
  created_at: string;
}

export interface InsightsResponse {
  insights: Insight[];
  summary: {
    total_insights: number;
    high_confidence_count: number;
    analysis_period: {
      start_date: string;
      end_date: string;
    };
  };
}

class InsightsService {
  private baseUrl = API_CONFIG.BASE_URL;

  async getUserInsights(userId: string): Promise<InsightsResponse> {
    try {
      const url = `${this.baseUrl}${API_CONFIG.ENDPOINTS.INSIGHTS.replace('{user_id}', userId)}`;
      const response = await fetch(url, {
        headers: {
          ...getAuthHeaders(),
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch insights:', error);
      throw error;
    }
  }

  async getInsightById(insightId: string) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/insights/detail/${insightId}`, {
        headers: {
          ...getAuthHeaders(),
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch insight details:', error);
      throw error;
    }
  }
}

export const insightsService = new InsightsService();

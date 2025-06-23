
import { API_CONFIG, getAuthHeaders } from '@/config/api';

export interface AnalysisStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  message?: string;
  results?: any;
}

export interface StartAnalysisRequest {
  file_ids: string[];
  analysis_type?: string;
}

class AnalysisService {
  private baseUrl = API_CONFIG.BASE_URL;

  async startAnalysis(request: StartAnalysisRequest): Promise<{ job_id: string }> {
    try {
      const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.ANALYSIS.START}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to start analysis:', error);
      throw new Error('Failed to start analysis. Please try again.');
    }
  }

  async getAnalysisStatus(jobId: string): Promise<AnalysisStatus> {
    try {
      const url = `${this.baseUrl}${API_CONFIG.ENDPOINTS.ANALYSIS.STATUS.replace('{job_id}', jobId)}`;
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
      console.error('Failed to get analysis status:', error);
      throw error;
    }
  }
}

export const analysisService = new AnalysisService();

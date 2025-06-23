
import { API_CONFIG, getAuthHeaders } from '@/config/api';

export interface UploadResponse {
  success: boolean;
  message: string;
  file_id?: string;
  job_id?: string;
}

export interface FileUploadData {
  file: File;
  data_type: 'glucose' | 'sleep' | 'food' | 'exercise';
  metadata?: Record<string, any>;
}

class UploadService {
  private baseUrl = API_CONFIG.BASE_URL;

  async uploadFile(uploadData: FileUploadData): Promise<UploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', uploadData.file);
      formData.append('data_type', uploadData.data_type);
      
      if (uploadData.metadata) {
        formData.append('metadata', JSON.stringify(uploadData.metadata));
      }

      const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.UPLOADS}`, {
        method: 'POST',
        headers: {
          ...getAuthHeaders(),
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('File upload failed:', error);
      throw new Error('Failed to upload file. Please try again.');
    }
  }

  async getUploadHistory() {
    try {
      const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.UPLOADS}`, {
        headers: {
          ...getAuthHeaders(),
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch upload history:', error);
      throw error;
    }
  }
}

export const uploadService = new UploadService();

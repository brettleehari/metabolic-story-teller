
import { API_CONFIG, getAuthHeaders } from '@/config/api';

export interface MagicLinkRequest {
  email: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  token?: string;
  user?: {
    id: string;
    email: string;
    name?: string;
  };
}

class AuthService {
  private baseUrl = API_CONFIG.BASE_URL;

  async requestMagicLink(email: string): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.REQUEST_MAGIC_LINK}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Magic link request failed:', error);
      throw new Error('Failed to send magic link. Please try again.');
    }
  }

  async verifyToken(token: string): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.VERIFY_TOKEN}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.token) {
        localStorage.setItem('auth_token', data.token);
        localStorage.setItem('user_data', JSON.stringify(data.user));
      }

      return data;
    } catch (error) {
      console.error('Token verification failed:', error);
      throw new Error('Failed to verify authentication. Please try again.');
    }
  }

  async getUserProfile() {
    try {
      const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.USER}`, {
        headers: {
          ...getAuthHeaders(),
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      throw error;
    }
  }

  logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
  }

  getCurrentUser() {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  }

  isAuthenticated() {
    return !!localStorage.getItem('auth_token');
  }
}

export const authService = new AuthService();

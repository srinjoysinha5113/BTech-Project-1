const API_BASE_URL = 'http://localhost:8000/api/v1';

/**
 * Basic API service to handle communication with the backend.
 */
class ApiService {
  private static token: string | null = null;

  static setToken(token: string) {
    this.token = token;
    sessionStorage.setItem('token', token);
  }

  static getToken() {
    if (!this.token) {
      this.token = sessionStorage.getItem('token');
    }
    return this.token;
  }

  private static async request(endpoint: string, options: RequestInit = {}) {
    const headers = new Headers(options.headers || {});
    
    const token = this.getToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || 'Network response was not ok');
    }

    return response.json();
  }

  // Auth Endpoints
  static async login(userData: any) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    
    if (!response.ok) {
        throw new Error('Login failed');
    }
    
    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  static async register(userData: any) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  // Health
  static async getHealth() {
    return this.request('/health');
  }

  // Kyber / Session
  static async createSession(publicKey: string, variant: string = 'Kyber512') {
    return this.request('/kyber/create-session', {
      method: 'POST',
      body: JSON.stringify({ public_key: publicKey, variant }),
    });
  }

  // Messages
  static async sendMessageWithSession(messageData: any) {
    return this.request('/messages/send-with-session', {
      method: 'POST',
      body: JSON.stringify(messageData),
    });
  }

  static async getInbox() {
    return this.request('/messages/inbox');
  }

  static async decryptMessageWithSession(messageId: number, sessionId: string) {
    return this.request(`/messages/${messageId}/decrypt-with-session`, {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId }),
    });
  }

  // Benchmarks
  static async runBenchmarks() {
    return this.request('/benchmarks/run');
  }

  static async getBenchmarkHistory() {
    return this.request('/benchmarks/history');
  }
}

export default ApiService;

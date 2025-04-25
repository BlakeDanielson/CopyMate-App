import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";
import { API_BASE_URL, STORAGE_KEYS } from "../../config/constants";

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor for adding auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for handling errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        // Handle specific error codes
        if (error.response) {
          switch (error.response.status) {
            case 401: // Unauthorized
              // Clear token and redirect to login
              localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
              // Redirect logic would be here
              break;
            case 429: // Too Many Requests
              // Implement rate limit handling
              break;
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Generic request methods
  public async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.api.get(url, config);
    return response.data;
  }

  public async post<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.api.post(url, data, config);
    return response.data;
  }

  public async put<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.api.put(url, data, config);
    return response.data;
  }

  public async patch<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.api.patch(url, data, config);
    return response.data;
  }

  public async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.api.delete(url, config);
    return response.data;
  }

  // SSE streaming for LLM responses
  public createEventSource(url: string): EventSource {
    const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    const fullUrl = `${API_BASE_URL}${url}${token ? `?token=${token}` : ""}`;
    return new EventSource(fullUrl);
  }

  // Methods for tracking API performance
  public async getWithMetrics<T>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<{ data: T; metrics: any }> {
    const startTime = performance.now();
    const response: AxiosResponse<T> = await this.api.get(url, config);
    const endTime = performance.now();
    const metrics = {
      totalTime: endTime - startTime,
      status: response.status,
      size: JSON.stringify(response.data).length,
    };
    return { data: response.data, metrics };
  }
}

// Singleton instance
export const apiService = new ApiService();

import { apiService } from "./api.service";
import { AxiosRequestConfig } from "axios";
import {
  TimeWindow,
  AnalyticsDashboardResponse,
  ApiPerformanceResponse,
  LlmPerformanceResponse,
  EndpointsResponse,
  ProviderModelsResponse,
} from "../../interfaces/analytics";

/**
 * Service for interacting with the analytics API endpoints
 */
class AnalyticsApiService {
  private readonly BASE_URL = "/analytics";

  /**
   * Get dashboard analytics data
   *
   * @param timeWindow Time window for the data (hourly, daily, weekly, monthly)
   * @param startDate Optional start date for custom range
   * @param endDate Optional end date for custom range
   * @param filters Optional filters for providers, models, endpoints
   * @returns Dashboard analytics data
   */
  async getDashboardData(
    timeWindow: TimeWindow = TimeWindow.DAY,
    startDate?: Date,
    endDate?: Date,
    filters?: {
      providers?: string[];
      models?: string[];
      endpoints?: string[];
    }
  ): Promise<AnalyticsDashboardResponse> {
    const config: AxiosRequestConfig = {
      params: {
        timeWindow,
        ...(startDate && { startDate: startDate.toISOString() }),
        ...(endDate && { endDate: endDate.toISOString() }),
        ...(filters?.providers && { providers: filters.providers.join(",") }),
        ...(filters?.models && { models: filters.models.join(",") }),
        ...(filters?.endpoints && { endpoints: filters.endpoints.join(",") }),
      },
    };

    return apiService.get(`${this.BASE_URL}/dashboard`, config);
  }

  /**
   * Get API performance metrics
   *
   * @param timeWindow Time window for the data
   * @param startDate Optional start date for custom range
   * @param endDate Optional end date for custom range
   * @param endpoints Optional endpoint filters
   * @returns API performance metrics
   */
  async getApiPerformanceMetrics(
    timeWindow: TimeWindow = TimeWindow.DAY,
    startDate?: Date,
    endDate?: Date,
    endpoints?: string[]
  ): Promise<ApiPerformanceResponse> {
    const config: AxiosRequestConfig = {
      params: {
        timeWindow,
        ...(startDate && { startDate: startDate.toISOString() }),
        ...(endDate && { endDate: endDate.toISOString() }),
        ...(endpoints && { endpoints: endpoints.join(",") }),
      },
    };

    return apiService.get(`${this.BASE_URL}/api-performance`, config);
  }

  /**
   * Get LLM performance metrics
   *
   * @param timeWindow Time window for the data
   * @param startDate Optional start date for custom range
   * @param endDate Optional end date for custom range
   * @param filters Optional filters for providers, models, successOnly
   * @returns LLM performance metrics
   */
  async getLlmPerformanceMetrics(
    timeWindow: TimeWindow = TimeWindow.DAY,
    startDate?: Date,
    endDate?: Date,
    filters?: {
      providers?: string[];
      models?: string[];
      successOnly?: boolean;
    }
  ): Promise<LlmPerformanceResponse> {
    const config: AxiosRequestConfig = {
      params: {
        timeWindow,
        ...(startDate && { startDate: startDate.toISOString() }),
        ...(endDate && { endDate: endDate.toISOString() }),
        ...(filters?.providers && { providers: filters.providers.join(",") }),
        ...(filters?.models && { models: filters.models.join(",") }),
        ...(filters?.successOnly !== undefined && {
          successOnly: filters.successOnly,
        }),
      },
    };

    return apiService.get(`${this.BASE_URL}/llm-performance`, config);
  }

  /**
   * Get unique endpoints for filtering
   *
   * @returns Array of unique endpoint strings
   */
  async getUniqueEndpoints(): Promise<EndpointsResponse> {
    return apiService.get(`${this.BASE_URL}/endpoints`);
  }

  /**
   * Get unique provider/model combinations for filtering
   *
   * @returns Provider/model combinations
   */
  async getUniqueProviderModels(): Promise<ProviderModelsResponse> {
    return apiService.get(`${this.BASE_URL}/provider-models`);
  }
}

export const analyticsService = new AnalyticsApiService();

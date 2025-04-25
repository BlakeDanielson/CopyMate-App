/**
 * Types for the analytics system - frontend interfaces
 */

// Time windows for metrics aggregation
export enum TimeWindow {
  HOUR = "hourly",
  DAY = "daily",
  WEEK = "weekly",
  MONTH = "monthly",
}

// API Performance Log types
export interface ApiPerformanceMetrics {
  endpoint: string;
  method: string;
  averageResponseTime: number;
  p50ResponseTime?: number;
  p95ResponseTime?: number;
  p99ResponseTime?: number;
  successRate: number;
  requestCount: number;
  failureCount: number;
  timeWindow: string;
  startTime: string;
  endTime: string;
}

// LLM Performance Metrics types
export interface LlmPerformanceMetrics {
  provider: string;
  model: string;
  operation: string;
  averageTotalDuration: number;
  averageTimeToFirstToken?: number;
  p50TotalDuration?: number;
  p95TotalDuration?: number;
  p99TotalDuration?: number;
  successRate: number;
  requestCount: number;
  failureCount: number;
  timeWindow: string;
  startTime: string;
  endTime: string;
}

// Analytics filter
export interface AnalyticsFilter {
  startDate?: string;
  endDate?: string;
  providers?: string[];
  models?: string[];
  endpoints?: string[];
  timeWindow?: TimeWindow;
  userId?: string;
  successOnly?: boolean;
}

// Combined dashboard metrics
export interface AnalyticsDashboardData {
  apiPerformance: ApiPerformanceMetrics[];
  llmPerformance: LlmPerformanceMetrics[];
  topEndpoints: {
    endpoint: string;
    requestCount: number;
    averageResponseTime: number;
  }[];
  topModels: {
    provider: string;
    model: string;
    requestCount: number;
    averageDuration: number;
  }[];
  overallApiSuccessRate: number;
  overallLlmSuccessRate: number;
  timeWindow: TimeWindow;
  startTime: string;
  endTime: string;
}

// Provider/Model mapping
export interface ProviderModelMap {
  raw: {
    provider: string;
    model: string;
  }[];
  byProvider: Record<string, string[]>;
}

// API response wrappers
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
  message?: string;
}

export interface AnalyticsDashboardResponse
  extends ApiResponse<AnalyticsDashboardData> {}
export interface ApiPerformanceResponse
  extends ApiResponse<ApiPerformanceMetrics[]> {}
export interface LlmPerformanceResponse
  extends ApiResponse<LlmPerformanceMetrics[]> {}
export interface EndpointsResponse extends ApiResponse<string[]> {}
export interface ProviderModelsResponse extends ApiResponse<ProviderModelMap> {}

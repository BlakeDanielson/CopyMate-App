/**
 * Type definitions for the analytics system
 */

// API Performance Log types
export interface ApiPerformanceLogEntry {
  id?: string;
  endpoint: string;
  method: string;
  statusCode: number;
  responseTime: number;
  userId?: string;
  timestamp?: Date;
  metadata?: Record<string, any>;
}

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
  startTime: Date;
  endTime: Date;
}

// LLM Performance Log types
export interface LlmPerformanceLogEntry {
  id?: string;
  provider: string;
  model: string;
  operation: string;
  timeToFirstToken?: number;
  totalDuration: number;
  tokenCount?: number;
  success: boolean;
  errorCode?: string;
  errorMessage?: string;
  userId?: string;
  timestamp?: Date;
  metadata?: Record<string, any>;
}

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
  startTime: Date;
  endTime: Date;
}

// Performance Aggregate types
export interface PerformanceAggregateEntry {
  id?: string;
  metricType: string;
  metricTarget: string;
  timeWindow: string;
  timestamp: Date;
  value: number;
  sampleCount: number;
  p50?: number;
  p95?: number;
  p99?: number;
  metadata?: Record<string, any>;
}

// Time windows for metrics aggregation
export enum TimeWindow {
  HOUR = 'hourly',
  DAY = 'daily',
  WEEK = 'weekly',
  MONTH = 'monthly',
}

// Analytics data filters
export interface AnalyticsFilter {
  startDate?: Date;
  endDate?: Date;
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
  startTime: Date;
  endTime: Date;
}

// Admin permissions for analytics
export enum AnalyticsPermission {
  VIEW_API_METRICS = 'view_api_metrics',
  VIEW_LLM_METRICS = 'view_llm_metrics',
  VIEW_USER_METRICS = 'view_user_metrics',
  EXPORT_METRICS = 'export_metrics',
}

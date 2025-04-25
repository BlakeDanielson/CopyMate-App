import { prisma } from '../lib/prisma';
import { 
  ApiPerformanceMetrics, 
  LlmPerformanceMetrics, 
  AnalyticsFilter,
  AnalyticsDashboardData,
  TimeWindow
} from '../types/analytics';

/**
 * Service for analytics data processing, aggregation, and retrieval
 */
export class AnalyticsService {
  /**
   * Get API performance metrics within the specified time range and filters
   * 
   * @param filter Analytics filter options
   * @returns API performance metrics for the selected endpoints
   */
  async getApiPerformanceMetrics(filter: AnalyticsFilter = {}): Promise<ApiPerformanceMetrics[]> {
    // Apply filter dates or use default (last 24 hours)
    const startDate = filter.startDate || new Date(Date.now() - 24 * 60 * 60 * 1000);
    const endDate = filter.endDate || new Date();
    
    // Prepare where clause for prisma query
    const whereClause: any = {
      timestamp: {
        gte: startDate,
        lte: endDate
      }
    };
    
    // Add endpoint filter if specified
    if (filter.endpoints && filter.endpoints.length > 0) {
      whereClause.endpoint = {
        in: filter.endpoints
      };
    }
    
    // Add user filter if specified
    if (filter.userId) {
      whereClause.userId = filter.userId;
    }
    
    // Query API performance logs
    const logs = await prisma.apiPerformanceLog.findMany({
      where: whereClause,
      orderBy: {
        timestamp: 'asc'
      }
    });
    
    // Group logs by endpoint and method
    const groupedLogs: Record<string, {
      endpoint: string;
      method: string;
      responseTimes: number[];
      statusCodes: number[];
    }> = {};
    
    logs.forEach((log: any) => {
      const key = `${log.endpoint}|${log.method}`;
      
      if (!groupedLogs[key]) {
        groupedLogs[key] = {
          endpoint: log.endpoint,
          method: log.method,
          responseTimes: [],
          statusCodes: []
        };
      }
      
      groupedLogs[key].responseTimes.push(log.responseTime);
      groupedLogs[key].statusCodes.push(log.statusCode);
    });
    
    // Calculate metrics for each endpoint/method
    const metrics: ApiPerformanceMetrics[] = Object.values(groupedLogs).map(group => {
      // Sort response times for percentiles
      const sortedTimes = [...group.responseTimes].sort((a, b) => a - b);
      const requestCount = sortedTimes.length;
      
      // Calculate success (2xx or 3xx status) and failure counts
      const successCount = group.statusCodes.filter(code => code < 400).length;
      const failureCount = requestCount - successCount;
      
      // Calculate average response time
      const totalTime = sortedTimes.reduce((sum, time) => sum + time, 0);
      const averageResponseTime = requestCount > 0 ? totalTime / requestCount : 0;
      
      // Calculate percentiles
      const p50Index = Math.floor(requestCount * 0.5);
      const p95Index = Math.floor(requestCount * 0.95);
      const p99Index = Math.floor(requestCount * 0.99);
      
      return {
        endpoint: group.endpoint,
        method: group.method,
        averageResponseTime,
        p50ResponseTime: requestCount > 0 ? sortedTimes[p50Index] : undefined,
        p95ResponseTime: requestCount > 0 ? sortedTimes[p95Index] : undefined,
        p99ResponseTime: requestCount > 0 ? sortedTimes[p99Index] : undefined,
        successRate: requestCount > 0 ? successCount / requestCount : 0,
        requestCount,
        failureCount,
        timeWindow: filter.timeWindow || TimeWindow.DAY,
        startTime: startDate,
        endTime: endDate
      };
    });
    
    return metrics;
  }
  
  /**
   * Get LLM performance metrics within the specified time range and filters
   * 
   * @param filter Analytics filter options
   * @returns LLM performance metrics for the selected providers and models
   */
  async getLlmPerformanceMetrics(filter: AnalyticsFilter = {}): Promise<LlmPerformanceMetrics[]> {
    // Apply filter dates or use default (last 24 hours)
    const startDate = filter.startDate || new Date(Date.now() - 24 * 60 * 60 * 1000);
    const endDate = filter.endDate || new Date();
    
    // Prepare where clause for prisma query
    const whereClause: any = {
      timestamp: {
        gte: startDate,
        lte: endDate
      }
    };
    
    // Add provider filter if specified
    if (filter.providers && filter.providers.length > 0) {
      whereClause.provider = {
        in: filter.providers
      };
    }
    
    // Add model filter if specified
    if (filter.models && filter.models.length > 0) {
      whereClause.model = {
        in: filter.models
      };
    }
    
    // Add user filter if specified
    if (filter.userId) {
      whereClause.userId = filter.userId;
    }
    
    // Add success filter if specified
    if (filter.successOnly) {
      whereClause.success = true;
    }
    
    // Query LLM performance logs
    const logs = await prisma.llmPerformanceLog.findMany({
      where: whereClause,
      orderBy: {
        timestamp: 'asc'
      }
    });
    
    // Group logs by provider, model, and operation
    const groupedLogs: Record<string, {
      provider: string;
      model: string;
      operation: string;
      totalDurations: number[];
      timeToFirstTokens: number[];
      successCounts: number;
      failureCounts: number;
    }> = {};
    
    logs.forEach((log: any) => {
      const key = `${log.provider}|${log.model}|${log.operation}`;
      
      if (!groupedLogs[key]) {
        groupedLogs[key] = {
          provider: log.provider,
          model: log.model,
          operation: log.operation,
          totalDurations: [],
          timeToFirstTokens: [],
          successCounts: 0,
          failureCounts: 0
        };
      }
      
      groupedLogs[key].totalDurations.push(log.totalDuration);
      
      // Only add non-null timeToFirstToken values
      if (log.timeToFirstToken !== null) {
        groupedLogs[key].timeToFirstTokens.push(log.timeToFirstToken);
      }
      
      // Increment success or failure count
      if (log.success) {
        groupedLogs[key].successCounts++;
      } else {
        groupedLogs[key].failureCounts++;
      }
    });
    
    // Calculate metrics for each provider/model/operation
    const metrics: LlmPerformanceMetrics[] = Object.values(groupedLogs).map(group => {
      // Sort durations for percentiles
      const sortedDurations = [...group.totalDurations].sort((a, b) => a - b);
      const requestCount = sortedDurations.length;
      
      // Calculate average total duration
      const totalDurationSum = sortedDurations.reduce((sum, time) => sum + time, 0);
      const averageTotalDuration = requestCount > 0 ? totalDurationSum / requestCount : 0;
      
      // Calculate average time to first token (if available)
      let averageTimeToFirstToken: number | undefined;
      if (group.timeToFirstTokens.length > 0) {
        const ttftSum = group.timeToFirstTokens.reduce((sum, time) => sum + time, 0);
        averageTimeToFirstToken = ttftSum / group.timeToFirstTokens.length;
      }
      
      // Calculate percentiles
      const p50Index = Math.floor(requestCount * 0.5);
      const p95Index = Math.floor(requestCount * 0.95);
      const p99Index = Math.floor(requestCount * 0.99);
      
      return {
        provider: group.provider,
        model: group.model,
        operation: group.operation,
        averageTotalDuration,
        averageTimeToFirstToken,
        p50TotalDuration: requestCount > 0 ? sortedDurations[p50Index] : undefined,
        p95TotalDuration: requestCount > 0 ? sortedDurations[p95Index] : undefined,
        p99TotalDuration: requestCount > 0 ? sortedDurations[p99Index] : undefined,
        successRate: requestCount > 0 ? group.successCounts / requestCount : 0,
        requestCount,
        failureCount: group.failureCounts,
        timeWindow: filter.timeWindow || TimeWindow.DAY,
        startTime: startDate,
        endTime: endDate
      };
    });
    
    return metrics;
  }
  
  /**
   * Get dashboard analytics data including combined metrics for APIs and LLMs
   * 
   * @param filter Analytics filter options
   * @returns Combined dashboard metrics
   */
  async getDashboardData(filter: AnalyticsFilter = {}): Promise<AnalyticsDashboardData> {
    // Get API and LLM metrics
    const apiMetrics = await this.getApiPerformanceMetrics(filter);
    const llmMetrics = await this.getLlmPerformanceMetrics(filter);
    
    // Calculate top endpoints by request count
    const topEndpoints = [...apiMetrics]
      .sort((a, b) => b.requestCount - a.requestCount)
      .slice(0, 5)
      .map(metric => ({
        endpoint: metric.endpoint,
        requestCount: metric.requestCount,
        averageResponseTime: metric.averageResponseTime
      }));
    
    // Calculate top models by request count
    const topModels = [...llmMetrics]
      .sort((a, b) => b.requestCount - a.requestCount)
      .slice(0, 5)
      .map(metric => ({
        provider: metric.provider,
        model: metric.model,
        requestCount: metric.requestCount,
        averageDuration: metric.averageTotalDuration
      }));
    
    // Calculate overall success rates
    const totalApiRequests = apiMetrics.reduce((sum, metric) => sum + metric.requestCount, 0);
    const totalApiSuccesses = apiMetrics.reduce((sum, metric) => 
      sum + (metric.requestCount * metric.successRate), 0);
    
    const totalLlmRequests = llmMetrics.reduce((sum, metric) => sum + metric.requestCount, 0);
    const totalLlmSuccesses = llmMetrics.reduce((sum, metric) => 
      sum + (metric.requestCount * metric.successRate), 0);
    
    const overallApiSuccessRate = totalApiRequests > 0 ? totalApiSuccesses / totalApiRequests : 0;
    const overallLlmSuccessRate = totalLlmRequests > 0 ? totalLlmSuccesses / totalLlmRequests : 0;
    
    // Return combined dashboard data
    return {
      apiPerformance: apiMetrics,
      llmPerformance: llmMetrics,
      topEndpoints,
      topModels,
      overallApiSuccessRate,
      overallLlmSuccessRate,
      timeWindow: filter.timeWindow || TimeWindow.DAY,
      startTime: filter.startDate || new Date(Date.now() - 24 * 60 * 60 * 1000),
      endTime: filter.endDate || new Date()
    };
  }
  
  /**
   * Store a calculated performance metric aggregate
   * 
   * @param metricType Type of metric (e.g., api_avg_response, llm_avg_ttft)
   * @param metricTarget Target of the metric (e.g., endpoint name, provider+model)
   * @param timeWindow Time window (hourly, daily, etc.)
   * @param timestamp Timestamp for the start of the window
   * @param value Calculated metric value
   * @param sampleCount Number of samples used to calculate the metric
   * @param p50 50th percentile (median) value (optional)
   * @param p95 95th percentile value (optional)
   * @param p99 99th percentile value (optional)
   * @param metadata Additional metadata (optional)
   * @returns True if the aggregate was stored successfully
   */
  async storeAggregate(
    metricType: string,
    metricTarget: string,
    timeWindow: string,
    timestamp: Date,
    value: number,
    sampleCount: number,
    p50?: number,
    p95?: number,
    p99?: number,
    metadata?: Record<string, any>
  ): Promise<boolean> {
    try {
      await prisma.performanceAggregate.create({
        data: {
          metricType,
          metricTarget,
          timeWindow,
          timestamp,
          value,
          sampleCount,
          p50,
          p95,
          p99,
          metadata: metadata as any
        }
      });
      return true;
    } catch (error) {
      console.error('Error storing performance aggregate:', error);
      return false;
    }
  }
  
  /**
   * Get calculated aggregates for a specific metric type and target
   * 
   * @param metricType Type of metric
   * @param metricTarget Target of the metric
   * @param timeWindow Time window
   * @param startDate Start date for the query
   * @param endDate End date for the query
   * @returns Array of aggregate data points
   */
  async getAggregates(
    metricType: string,
    metricTarget: string,
    timeWindow: string,
    startDate: Date,
    endDate: Date
  ): Promise<{
    timestamp: Date;
    value: number;
    sampleCount: number;
    p50?: number;
    p95?: number;
    p99?: number;
  }[]> {
    const aggregates = await prisma.performanceAggregate.findMany({
      where: {
        metricType,
        metricTarget,
        timeWindow,
        timestamp: {
          gte: startDate,
          lte: endDate
        }
      },
      orderBy: {
        timestamp: 'asc'
      },
      select: {
        timestamp: true,
        value: true,
        sampleCount: true,
        p50: true,
        p95: true,
        p99: true
      }
    });
    
    // Map results to convert null percentiles to undefined to match return type
    return aggregates.map(agg => ({
      timestamp: agg.timestamp,
      value: agg.value,
      sampleCount: agg.sampleCount,
      p50: agg.p50 === null ? undefined : agg.p50,
      p95: agg.p95 === null ? undefined : agg.p95,
      p99: agg.p99 === null ? undefined : agg.p99,
    }));
  }
  
  /**
   * Get all unique API endpoints in the database
   * 
   * @returns Array of unique endpoint strings
   */
  async getUniqueEndpoints(): Promise<string[]> {
    const result = await prisma.apiPerformanceLog.groupBy({
      by: ['endpoint'],
      orderBy: {
        endpoint: 'asc'
      }
    });
    
    return result.map((r: { endpoint: string }) => r.endpoint);
  }
  
  /**
   * Get all unique provider/model combinations in the database
   * 
   * @returns Array of objects with provider and model
   */
  async getUniqueProviderModels(): Promise<{provider: string; model: string}[]> {
    const result = await prisma.llmPerformanceLog.groupBy({
      by: ['provider', 'model'],
      orderBy: [
        { provider: 'asc' },
        { model: 'asc' }
      ]
    });
    
    return result.map((r: { provider: string; model: string }) => ({ provider: r.provider, model: r.model }));
  }
}

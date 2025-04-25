import { Request, Response } from 'express';
import { AnalyticsService } from '../services/analytics.service';
import { TimeWindow } from '../types/analytics';

/**
 * Controller for analytics endpoints
 */
export class AnalyticsController {
  private analyticsService: AnalyticsService;
  
  /**
   * Constructor
   */
  constructor() {
    this.analyticsService = new AnalyticsService();
  }
  
  /**
   * Get dashboard analytics data
   * 
   * @param req Express request
   * @param res Express response
   */
  getDashboardData = async (req: Request, res: Response): Promise<void> => {
    try {
      // Parse query parameters
      const timeWindow = req.query.timeWindow as string || TimeWindow.DAY;
      
      // Parse start and end dates if provided
      let startDate: Date | undefined;
      let endDate: Date | undefined;
      
      if (req.query.startDate) {
        startDate = new Date(req.query.startDate as string);
      }
      
      if (req.query.endDate) {
        endDate = new Date(req.query.endDate as string);
      }
      
      // Parse additional filters
      const providers = req.query.providers 
        ? (req.query.providers as string).split(',') 
        : undefined;
        
      const models = req.query.models 
        ? (req.query.models as string).split(',') 
        : undefined;
        
      const endpoints = req.query.endpoints 
        ? (req.query.endpoints as string).split(',') 
        : undefined;
      
      // Get dashboard data with filters
      const dashboardData = await this.analyticsService.getDashboardData({
        timeWindow: timeWindow as TimeWindow,
        startDate,
        endDate,
        providers,
        models,
        endpoints,
        // If this is an admin API and we want to filter by user
        userId: req.query.userId as string || undefined
      });
      
      // Return dashboard data
      res.status(200).json({
        success: true,
        data: dashboardData
      });
    } catch (error) {
      console.error('Error getting dashboard data:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to retrieve analytics data',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  };

  /**
   * Get API performance metrics
   * 
   * @param req Express request
   * @param res Express response
   */
  getApiPerformanceMetrics = async (req: Request, res: Response): Promise<void> => {
    try {
      // Parse query parameters
      const timeWindow = req.query.timeWindow as string || TimeWindow.DAY;
      
      // Parse start and end dates if provided
      let startDate: Date | undefined;
      let endDate: Date | undefined;
      
      if (req.query.startDate) {
        startDate = new Date(req.query.startDate as string);
      }
      
      if (req.query.endDate) {
        endDate = new Date(req.query.endDate as string);
      }
      
      // Parse endpoint filter
      const endpoints = req.query.endpoints 
        ? (req.query.endpoints as string).split(',') 
        : undefined;
      
      // Get API performance metrics
      const metrics = await this.analyticsService.getApiPerformanceMetrics({
        timeWindow: timeWindow as TimeWindow,
        startDate,
        endDate,
        endpoints,
        userId: req.query.userId as string || undefined
      });
      
      // Return metrics
      res.status(200).json({
        success: true,
        data: metrics
      });
    } catch (error) {
      console.error('Error getting API performance metrics:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to retrieve API performance metrics',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  };

  /**
   * Get LLM performance metrics
   * 
   * @param req Express request
   * @param res Express response
   */
  getLlmPerformanceMetrics = async (req: Request, res: Response): Promise<void> => {
    try {
      // Parse query parameters
      const timeWindow = req.query.timeWindow as string || TimeWindow.DAY;
      
      // Parse start and end dates if provided
      let startDate: Date | undefined;
      let endDate: Date | undefined;
      
      if (req.query.startDate) {
        startDate = new Date(req.query.startDate as string);
      }
      
      if (req.query.endDate) {
        endDate = new Date(req.query.endDate as string);
      }
      
      // Parse additional filters
      const providers = req.query.providers 
        ? (req.query.providers as string).split(',') 
        : undefined;
        
      const models = req.query.models 
        ? (req.query.models as string).split(',') 
        : undefined;
      
      // Handle successOnly boolean
      const successOnlyStr = req.query.successOnly as string;
      const successOnly = successOnlyStr === 'true' ? true : 
                         successOnlyStr === 'false' ? false : undefined;
      
      // Get LLM performance metrics
      const metrics = await this.analyticsService.getLlmPerformanceMetrics({
        timeWindow: timeWindow as TimeWindow,
        startDate,
        endDate,
        providers,
        models,
        successOnly,
        userId: req.query.userId as string || undefined
      });
      
      // Return metrics
      res.status(200).json({
        success: true,
        data: metrics
      });
    } catch (error) {
      console.error('Error getting LLM performance metrics:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to retrieve LLM performance metrics',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  };

  /**
   * Get unique endpoints for filtering
   * 
   * @param req Express request
   * @param res Express response
   */
  getUniqueEndpoints = async (req: Request, res: Response): Promise<void> => {
    try {
      const endpoints = await this.analyticsService.getUniqueEndpoints();
      
      res.status(200).json({
        success: true,
        data: endpoints
      });
    } catch (error) {
      console.error('Error getting unique endpoints:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to retrieve unique endpoints',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  };

  /**
   * Get unique provider/model combinations for filtering
   * 
   * @param req Express request
   * @param res Express response
   */
  getUniqueProviderModels = async (req: Request, res: Response): Promise<void> => {
    try {
      const providerModels = await this.analyticsService.getUniqueProviderModels();
      
      // Group by provider for easier frontend consumption
      const groupedByProvider: Record<string, string[]> = {};
      
      providerModels.forEach(({ provider, model }) => {
        if (!groupedByProvider[provider]) {
          groupedByProvider[provider] = [];
        }
        
        groupedByProvider[provider].push(model);
      });
      
      res.status(200).json({
        success: true,
        data: {
          raw: providerModels,
          byProvider: groupedByProvider
        }
      });
    } catch (error) {
      console.error('Error getting unique provider/models:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to retrieve unique provider/models',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  };
}

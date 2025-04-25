import { Request, Response, NextFunction } from 'express';
import { prisma } from '../lib/prisma';
import { ApiPerformanceLogEntry } from '../types/analytics';

/**
 * Middleware to track API request performance metrics
 * This middleware:
 * 1. Records the start time of the request
 * 2. Processes the request normally
 * 3. Records metrics about the completed request (duration, status, etc.)
 * 4. Stores the metrics in the database
 */
export const trackApiPerformance = (excludePaths: string[] = []) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    // Skip tracking for excluded paths (like health checks, static assets, etc.)
    if (excludePaths.some(path => req.path.startsWith(path))) {
      return next();
    }

    // Record start time
    const startTime = process.hrtime();
    
    // Store original end method to wrap it
    const originalEnd = res.end;
    
    // Override end method to capture response metrics
    // @ts-ignore - We're intentionally modifying the function signature
    res.end = function(chunk?: any, encoding?: string): void {
      // Execute original end method
      // @ts-ignore
      originalEnd.apply(res, arguments);
      
      // Calculate response time in milliseconds
      const hrDuration = process.hrtime(startTime);
      const responseTimeMs = Math.round(hrDuration[0] * 1000 + hrDuration[1] / 1000000);
      
      // Extract user ID from request if available (assumes auth middleware sets req.user)
      const userId = (req as any).user?.id;
      
      // Create performance log entry
      const performanceEntry: ApiPerformanceLogEntry = {
        endpoint: req.path,
        method: req.method,
        statusCode: res.statusCode,
        responseTime: responseTimeMs,
        userId: userId,
        metadata: {
          userAgent: req.headers['user-agent'],
          contentType: req.headers['content-type'],
          contentLength: res.getHeader('content-length'),
          queryParams: req.query,
        }
      };
      
      // Store metrics asynchronously - we don't want to block the response
      storeApiPerformanceMetrics(performanceEntry).catch(err => {
        console.error('Failed to store API performance metrics:', err);
      });
    };
    
    next();
  };
};

/**
 * Save API performance metrics to the database
 */
async function storeApiPerformanceMetrics(entry: ApiPerformanceLogEntry): Promise<void> {
  try {
    await prisma.apiPerformanceLog.create({
      data: {
        endpoint: entry.endpoint,
        method: entry.method,
        statusCode: entry.statusCode,
        responseTime: entry.responseTime,
        userId: entry.userId,
        metadata: entry.metadata as any,
      }
    });
  } catch (error) {
    console.error('Error storing API performance metrics:', error);
    // We intentionally don't rethrow - metrics storage failure shouldn't affect the app
  }
}

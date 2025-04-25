/**
 * Authentication middleware
 * Verifies JWT token from request headers and adds user info to the request
 */

import { Request, Response, NextFunction } from 'express';
import { authService } from '../services/auth.service';

/**
 * Middleware to verify JWT tokens and extract user info
 */
export const authMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  try {
    // Get the token from the Authorization header
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      res.status(401).json({
        success: false,
        error: 'Unauthorized',
        message: 'Authentication required. Please include a valid Bearer token.'
      });
      return;
    }

    // Extract the token
    const token = authHeader.split(' ')[1];
    
    if (!token) {
      res.status(401).json({
        success: false,
        error: 'Unauthorized',
        message: 'Authentication token is missing'
      });
      return;
    }

    // Verify the token
    const decoded = authService.verifyToken(token);

    // Add the user info to the request
    req.user = {
      id: decoded.userId,
      email: decoded.email,
      role: decoded.role
    };

    // Continue to the next middleware or route handler
    next();
  } catch (error) {
    res.status(401).json({
      success: false,
      error: 'Unauthorized',
      message: 'Invalid or expired authentication token'
    });
  }
};

/**
 * Middleware to verify if user has admin role
 * Must be used after authMiddleware
 */
export const adminMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  try {
    if (!req.user) {
      res.status(401).json({
        success: false,
        error: 'Unauthorized',
        message: 'Authentication required'
      });
      return;
    }

    if (req.user.role !== 'ADMIN') {
      res.status(403).json({
        success: false,
        error: 'Forbidden',
        message: 'Admin role required for this resource'
      });
      return;
    }

    next();
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Internal Server Error',
      message: 'An error occurred while processing your request'
    });
  }
};

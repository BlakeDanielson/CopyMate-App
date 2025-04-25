/**
 * Authentication controller
 * Handles HTTP requests for user authentication operations
 */

import { Request, Response } from 'express';
import { startOfMonth, endOfMonth, format } from 'date-fns';
import { authService } from '../services/auth.service';
import { RegisterUserInput, LoginUserInput, SignUpUserInput } from '../types/auth';

export class AuthController {
  /**
   * Register a new user
   */
  async register(req: Request, res: Response): Promise<void> {
    try {
      const userData: RegisterUserInput = req.body;

      // Validate required fields
      if (!userData.email || !userData.password) {
        res.status(400).json({
          success: false,
          error: 'Bad Request',
          message: 'Email and password are required'
        });
        return;
      }

      // Register the user
      const user = await authService.register(userData);

      res.status(201).json({
        success: true,
        data: user,
        message: 'User registered successfully'
      });
    } catch (error: any) {
      console.error('Registration error:', error);

      // Check if it's a duplicate email error
      if (error.message && error.message.includes('already exists')) {
        res.status(409).json({
          success: false,
          error: 'Conflict',
          message: error.message
        });
        return;
      }

      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred during registration'
      });
    }
  }

  /**
   * Login a user
   */
  async login(req: Request, res: Response): Promise<void> {
    try {
      const credentials: LoginUserInput = req.body;

      // Validate required fields
      if (!credentials.email || !credentials.password) {
        res.status(400).json({
          success: false,
          error: 'Bad Request',
          message: 'Email and password are required'
        });
        return;
      }

      // Login the user
      const tokens = await authService.login(credentials);

      res.status(200).json({
        success: true,
        data: tokens,
        message: 'Login successful'
      });
    } catch (error: any) {
      console.error('Login error:', error);

      // Check if it's an invalid credentials error
      if (error.message && error.message.includes('Invalid email or password')) {
        res.status(401).json({
          success: false,
          error: 'Unauthorized',
          message: 'Invalid email or password'
        });
        return;
      }

      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred during login'
      });
    }
  }

  /**
   * Login a test user (bypasses password check) - ONLY FOR DEVELOPMENT/TESTING
   */
  async testLogin(req: Request, res: Response): Promise<void> {
    // Explicitly check the environment variable here as well for safety
    if (process.env.ENABLE_TEST_AUTH !== 'true') {
      res.status(403).json({
        success: false,
        error: 'Forbidden',
        message: 'Test login feature is disabled.'
      });
      return;
    }

    try {
      console.log('Attempting test login...');
      const tokens = await authService.testLogin();
      console.log('Test login successful, returning tokens.');

      res.status(200).json({
        success: true,
        data: tokens,
        message: 'Test login successful'
      });
    } catch (error: any) {
      console.error('Test login error in controller:', error);
      // Handle specific errors if needed, e.g., if the service throws 'Test login feature is disabled.'
      if (error.message && error.message.includes('Test login feature is disabled')) {
         res.status(403).json({
           success: false,
           error: 'Forbidden',
           message: error.message
         });
         return;
      }
      // Generic error handling
      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred during test login'
      });
    }
  }
/**
   * Sign up a new user
   */
  async signup(req: Request, res: Response): Promise<void> {
    try {
      const { email, password, confirmPassword }: SignUpUserInput = req.body;

      // Basic validation (more comprehensive validation in service)
      if (!email || !password || !confirmPassword) {
        res.status(400).json({
          success: false,
          error: 'Bad Request',
          message: 'Email, password, and confirm password are required',
        });
        return;
      }

      if (password !== confirmPassword) {
        res.status(400).json({
          success: false,
          error: 'Bad Request',
          message: 'Passwords do not match',
        });
        return;
      }

      // Call the service to handle signup logic
      const user = await authService.signup({ email, password, confirmPassword });

      res.status(201).json({
        success: true,
        data: user, // Return the created user (without password hash)
        message: 'User signed up successfully',
      });
    } catch (error: any) {
      console.error('Signup error:', error);

      // Handle specific errors from the service
      if (error.message && error.message.includes('Email already exists')) {
        res.status(409).json({
          success: false,
          error: 'Conflict',
          message: 'An account with this email address already exists.',
        });
        return;
      }
      if (error.message && (error.message.includes('Password validation failed') || error.message.includes('Invalid email format'))) {
         res.status(400).json({
           success: false,
           error: 'Bad Request',
           message: error.message, // Pass specific validation error message
         });
         return;
      }

      // Generic error handling
      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred during sign-up',
      });
    }
  }

  /**
   * Get the current user profile
   */
  async getProfile(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.user?.id;

      if (!userId) {
        res.status(401).json({
          success: false,
          error: 'Unauthorized',
          message: 'Authentication required'
        });
        return;
      }

      const user = await authService.getUserById(userId);

      if (!user) {
        res.status(404).json({
          success: false,
          error: 'Not Found',
          message: 'User not found'
        });
        return;
      }

      res.status(200).json({
        success: true,
        data: user,
        message: 'User profile retrieved successfully'
      });
    } catch (error: any) {
      console.error('Get profile error:', error);
      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred while fetching user profile'
      });
    }
  }

  /**
   * Get the current user's usage metrics
   */
  async getUserMetrics(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.user?.id;

      if (!userId) {
        res.status(401).json({
          success: false,
          error: 'Unauthorized',
          message: 'Authentication required'
        });
        return;
      }

      const metrics = await authService.getUserMetrics(userId);
      
      // Format dates for display
      const formattedMetrics = {
        ...metrics,
        billingPeriodStart: format(metrics.billingPeriodStart, 'yyyy-MM-dd'),
        billingPeriodEnd: format(metrics.billingPeriodEnd, 'yyyy-MM-dd'),
      };

      res.status(200).json({
        success: true,
        data: formattedMetrics,
        message: 'User metrics retrieved successfully'
      });
    } catch (error: any) {
      console.error('Get metrics error:', error);
      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred while fetching user metrics'
      });
    }
  }
}

// Create a singleton instance
export const authController = new AuthController();

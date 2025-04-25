/**
 * Authentication routes
 */

import { Router } from 'express';
import rateLimit from 'express-rate-limit';
import { authController } from '../controllers/auth.controller';
import { authMiddleware } from '../middleware/auth.middleware';

// Define rate limiter for authentication routes
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // Limit each IP to 5 requests per windowMs
  message: {
    success: false,
    error: 'Too Many Requests',
    message: 'Too many authentication attempts from this IP, please try again after 15 minutes'
  },
  standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers
});


export const createAuthRoutes = (): Router => {
  const router = Router();

  /**
   * @route   POST /api/v1/auth/register
   * @desc    Register a new user
   * @access  Public
   */
  router.post('/register', authLimiter, (req, res) => authController.register(req, res));

  /**
   * @route   POST /api/v1/auth/login
   * @desc    Login a user and get JWT token
   * @access  Public
   */
  router.post('/login', authLimiter, (req, res) => authController.login(req, res));

  /**
   * @route   POST /api/v1/auth/test-login
   * @desc    Login a test user (bypasses password check) - ONLY FOR DEVELOPMENT/TESTING
   * @access  Public (Strictly disabled in production)
   */
  // Only add the test-login route if NOT in production environment
  if (process.env.NODE_ENV !== 'production') {
    router.post('/test-login', authLimiter, (req, res) => authController.testLogin(req, res));
    console.log('INFO: Test login route (/api/v1/auth/test-login) is ENABLED.');
  } else {
    console.log('INFO: Test login route (/api/v1/auth/test-login) is DISABLED in production.');
  }

/**
   * @route   POST /api/v1/auth/signup
   * @desc    Sign up a new user
   * @access  Public
   */
  router.post('/signup', authLimiter, (req, res) => authController.signup(req, res));
  /**
   * @route   GET /api/v1/auth/profile
   * @desc    Get the current user's profile
   * @access  Private (requires authentication)
   */
  router.get('/profile', authMiddleware, (req, res) => authController.getProfile(req, res));

  /**
   * @route   GET /api/v1/auth/metrics
   * @desc    Get the current user's usage metrics
   * @access  Private (requires authentication)
   */
  router.get('/metrics', authMiddleware, (req, res) => authController.getUserMetrics(req, res));

  return router;
};

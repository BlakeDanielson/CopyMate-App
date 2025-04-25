import { Router } from 'express';
import { AnalyticsController } from '../controllers/analytics.controller';
import { authMiddleware, adminMiddleware } from '../middleware/auth.middleware';

// Create router
const router = Router();

// Create controller instance
const analyticsController = new AnalyticsController();


// Routes
// All analytics routes require authentication and admin role

// Dashboard data
router.get(
  '/dashboard',
  authMiddleware,
  adminMiddleware,
  analyticsController.getDashboardData
);

// API performance metrics
router.get(
  '/api-performance',
  authMiddleware,
  adminMiddleware,
  analyticsController.getApiPerformanceMetrics
);

// LLM performance metrics
router.get(
  '/llm-performance',
  authMiddleware,
  adminMiddleware,
  analyticsController.getLlmPerformanceMetrics
);

// Unique endpoints for filtering
router.get(
  '/endpoints',
  authMiddleware,
  adminMiddleware,
  analyticsController.getUniqueEndpoints
);

// Unique provider/model combinations for filtering
router.get(
  '/provider-models',
  authMiddleware,
  adminMiddleware,
  analyticsController.getUniqueProviderModels
);

export default router;

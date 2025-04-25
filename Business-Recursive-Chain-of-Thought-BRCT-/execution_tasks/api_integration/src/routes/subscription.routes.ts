import { Router } from 'express';
import { body } from 'express-validator';
import subscriptionController from '../controllers/subscription.controller';
import { authMiddleware } from '../middleware/auth.middleware';

const router = Router();

/**
 * @route   GET /api/subscriptions/plans
 * @desc    Get all active subscription plans
 * @access  Public
 */
router.get('/plans', subscriptionController.getSubscriptionPlans);

/**
 * @route   GET /api/subscriptions/plans/:id
 * @desc    Get subscription plan by ID
 * @access  Public
 */
router.get('/plans/:id', subscriptionController.getSubscriptionPlanById);

/**
 * @route   GET /api/subscriptions/status
 * @desc    Get the current user's subscription status
 * @access  Private
 */
router.get('/status', authMiddleware, subscriptionController.getUserSubscription);

/**
 * @route   GET /api/subscriptions/quota
 * @desc    Get the current user's subscription quota details
 * @access  Private
 */
router.get('/quota', authMiddleware, subscriptionController.getUserSubscriptionQuota);

/**
 * @route   POST /api/subscriptions/checkout
 * @desc    Create a checkout session for subscribing to a plan
 * @access  Private
 */
router.post('/checkout', 
  authMiddleware,
  [
    body('planId').notEmpty().withMessage('Plan ID is required'),
  ],
  subscriptionController.createCheckoutSession
);

/**
 * @route   POST /api/subscriptions/portal
 * @desc    Create a customer portal session for managing subscription
 * @access  Private
 */
router.post('/portal', authMiddleware, subscriptionController.createCustomerPortalSession);

/**
 * @route   POST /api/subscriptions/webhooks
 * @desc    Handle Stripe webhook events
 * @access  Public (secured with Stripe signature verification)
 */
router.post(
  '/webhooks',
  // The webhook handler needs raw body data for signature verification
  // so we disable any parsing middleware for this route only
  (req, res, next) => {
    // Raw body is set by our custom middleware in app.ts
    next();
  },
  subscriptionController.handleWebhookEvent
);

export default router;

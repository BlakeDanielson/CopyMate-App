import { Request, Response } from 'express';
import { UserPayload } from '../types/auth';
import { validationResult } from 'express-validator';
import subscriptionService from '../services/subscription.service';
import { CreateCheckoutSessionDto } from '../types/subscription';

class SubscriptionController {
  /**
   * Get all active subscription plans
   */
  async getSubscriptionPlans(req: Request, res: Response): Promise<void> {
    try {
      const plans = await subscriptionService.getSubscriptionPlans();
      res.json(plans);
    } catch (error) {
      console.error('Error getting subscription plans:', error);
      res.status(500).json({ message: 'Error getting subscription plans' });
    }
  }

  /**
   * Get subscription plan by ID
   */
  async getSubscriptionPlanById(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const plan = await subscriptionService.getSubscriptionPlanById(id);
      
      if (!plan) {
        res.status(404).json({ message: 'Subscription plan not found' });
        return;
      }
      
      res.json(plan);
    } catch (error) {
      console.error('Error getting subscription plan:', error);
      res.status(500).json({ message: 'Error getting subscription plan' });
    }
  }

  /**
   * Get the current user's subscription details
   */
  async getUserSubscription(req: Request, res: Response): Promise<void> {
    try {
      if (!req.user) {
        res.status(401).json({ message: 'Unauthorized - User not authenticated' });
        return;
      }
      
      const userId = req.user.id;
      const subscription = await subscriptionService.getUserSubscription(userId);
      
      if (!subscription) {
        res.status(404).json({ message: 'No active subscription found for this user' });
        return;
      }
      
      res.json(subscription);
    } catch (error) {
      console.error('Error getting user subscription:', error);
      res.status(500).json({ message: 'Error getting user subscription' });
    }
  }

  /**
   * Get the current user's subscription quota details
   */
  async getUserSubscriptionQuota(req: Request, res: Response): Promise<void> {
    try {
      if (!req.user) {
        res.status(401).json({ message: 'Unauthorized - User not authenticated' });
        return;
      }
      
      const userId = req.user.id;
      const quota = await subscriptionService.getUserSubscriptionQuota(userId);
      res.json(quota);
    } catch (error) {
      if ((error as Error).message.includes('does not have an active subscription')) {
        res.status(404).json({ message: 'No active subscription found for this user' });
        return;
      }
      
      console.error('Error getting user subscription quota:', error);
      res.status(500).json({ message: 'Error getting user subscription quota' });
    }
  }

  /**
   * Create a checkout session for subscribing to a plan
   */
  async createCheckoutSession(req: Request, res: Response): Promise<void> {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        res.status(400).json({ errors: errors.array() });
        return;
      }

      if (!req.user) {
        res.status(401).json({ message: 'Unauthorized - User not authenticated' });
        return;
      }
      
      const userId = req.user.id;
      const { planId, successUrl, cancelUrl } = req.body as CreateCheckoutSessionDto;
      
      const session = await subscriptionService.createCheckoutSession(userId, {
        planId,
        successUrl,
        cancelUrl,
      });
      
      res.json(session);
    } catch (error) {
      console.error('Error creating checkout session:', error);
      res.status(500).json({ message: 'Error creating checkout session', error: (error as Error).message });
    }
  }

  /**
   * Create a Stripe customer portal session for managing subscription
   */
  async createCustomerPortalSession(req: Request, res: Response): Promise<void> {
    try {
      if (!req.user) {
        res.status(401).json({ message: 'Unauthorized - User not authenticated' });
        return;
      }
      
      const userId = req.user.id;
      const session = await subscriptionService.createCustomerPortalSession(userId);
      res.json(session);
    } catch (error) {
      if ((error as Error).message.includes('does not have a Stripe customer ID')) {
        res.status(404).json({ message: 'User does not have an active subscription' });
        return;
      }
      
      console.error('Error creating customer portal session:', error);
      res.status(500).json({ message: 'Error creating customer portal session' });
    }
  }

  /**
   * Handle Stripe webhook events
   */
  async handleWebhookEvent(req: Request, res: Response): Promise<void> {
    const sig = req.headers['stripe-signature'];
    
    if (!sig) {
      res.status(400).json({ message: 'Missing stripe-signature header' });
      return;
    }

    const secret = process.env.STRIPE_WEBHOOK_SECRET;
    if (!secret) {
      console.error('STRIPE_WEBHOOK_SECRET is not defined');
      res.status(500).json({ message: 'Server configuration error' });
      return;
    }

    try {
      // @ts-ignore - We're importing Stripe dynamically here
      const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
      const event = stripe.webhooks.constructEvent(req.body, sig, secret);
      
      // Process the event
      await subscriptionService.handleWebhookEvent(event);
      
      // Return a response to acknowledge receipt of the event
      res.json({ received: true });
    } catch (error) {
      console.error('Error handling webhook event:', error);
      res.status(400).json({ message: 'Webhook error', error: (error as Error).message });
    }
  }
}

export default new SubscriptionController();

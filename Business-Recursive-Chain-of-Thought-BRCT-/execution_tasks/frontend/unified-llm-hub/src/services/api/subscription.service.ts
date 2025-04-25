import { AxiosResponse } from "axios";
import { apiService } from "./api.service";

// Interface for subscription plan
export interface SubscriptionPlan {
  id: string;
  name: string;
  description?: string;
  price: number;
  currency: string;
  interval: "MONTH" | "YEAR";
  messageQuota: number;
  isActive: boolean;
}

// Interface for subscription status
export interface UserSubscription {
  id: string;
  userId: string;
  planId: string;
  status: "ACTIVE" | "INACTIVE" | "PAST_DUE" | "CANCELED" | "TRIAL";
  currentPeriodStart?: Date;
  currentPeriodEnd?: Date;
  stripeSubscriptionId?: string;
  cancelAtPeriodEnd: boolean;
  remainingQuota?: number;
  createdAt: Date;
  updatedAt: Date;
  plan: SubscriptionPlan;
}

// Interface for subscription quota details
export interface SubscriptionQuota {
  totalQuota: number;
  usedQuota: number;
  remainingQuota: number;
  usagePercentage: number;
  currentPeriodStart?: Date;
  currentPeriodEnd?: Date;
  status: "ACTIVE" | "INACTIVE" | "PAST_DUE" | "CANCELED" | "TRIAL";
  plan: {
    id: string;
    name: string;
    description?: string;
    price: number;
    currency: string;
    interval: "MONTH" | "YEAR";
    messageQuota: number;
  };
}

// Interface for checkout session response
export interface CheckoutSessionResponse {
  sessionId: string;
  url: string;
}

// Interface for customer portal session response
export interface CustomerPortalSessionResponse {
  url: string;
}

class SubscriptionService {
  private endpoint = "/subscriptions";

  /**
   * Get all active subscription plans
   */
  async getSubscriptionPlans(): Promise<SubscriptionPlan[]> {
    try {
      const response: AxiosResponse<SubscriptionPlan[]> = await apiService.get(
        `${this.endpoint}/plans`
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching subscription plans:", error);
      throw error;
    }
  }

  /**
   * Get subscription plan by ID
   */
  async getSubscriptionPlanById(id: string): Promise<SubscriptionPlan> {
    try {
      const response: AxiosResponse<SubscriptionPlan> = await apiService.get(
        `${this.endpoint}/plans/${id}`
      );
      return response.data;
    } catch (error) {
      console.error(`Error fetching subscription plan ${id}:`, error);
      throw error;
    }
  }

  /**
   * Get current user's subscription status
   */
  async getCurrentSubscription(): Promise<UserSubscription | null> {
    try {
      const response: AxiosResponse<UserSubscription> = await apiService.get(
        `${this.endpoint}/status`
      );
      return response.data;
    } catch (error) {
      if ((error as any)?.response?.status === 404) {
        // User doesn't have a subscription
        return null;
      }
      console.error("Error fetching current subscription:", error);
      throw error;
    }
  }

  /**
   * Get current user's subscription quota
   */
  async getSubscriptionQuota(): Promise<SubscriptionQuota | null> {
    try {
      const response: AxiosResponse<SubscriptionQuota> = await apiService.get(
        `${this.endpoint}/quota`
      );
      return response.data;
    } catch (error) {
      if ((error as any)?.response?.status === 404) {
        // User doesn't have a subscription
        return null;
      }
      console.error("Error fetching subscription quota:", error);
      throw error;
    }
  }

  /**
   * Create a Stripe checkout session for subscribing
   */
  async createCheckoutSession(
    planId: string
  ): Promise<CheckoutSessionResponse> {
    try {
      const response: AxiosResponse<CheckoutSessionResponse> =
        await apiService.post(`${this.endpoint}/checkout`, { planId });
      return response.data;
    } catch (error) {
      console.error("Error creating checkout session:", error);
      throw error;
    }
  }

  /**
   * Create a Stripe customer portal session for managing subscription
   */
  async createCustomerPortalSession(): Promise<CustomerPortalSessionResponse> {
    try {
      const response: AxiosResponse<CustomerPortalSessionResponse> =
        await apiService.post(`${this.endpoint}/portal`);
      return response.data;
    } catch (error) {
      console.error("Error creating customer portal session:", error);
      throw error;
    }
  }

  /**
   * Helper method to redirect to Stripe Checkout
   */
  async subscribeToplan(planId: string): Promise<void> {
    try {
      const { url } = await this.createCheckoutSession(planId);
      // Redirect to Stripe Checkout
      window.location.href = url;
    } catch (error) {
      console.error("Error redirecting to checkout:", error);
      throw error;
    }
  }

  /**
   * Helper method to redirect to Stripe Customer Portal
   */
  async manageSubscription(): Promise<void> {
    try {
      const { url } = await this.createCustomerPortalSession();
      // Redirect to Stripe Customer Portal
      window.location.href = url;
    } catch (error) {
      console.error("Error redirecting to customer portal:", error);
      throw error;
    }
  }
}

export default new SubscriptionService();

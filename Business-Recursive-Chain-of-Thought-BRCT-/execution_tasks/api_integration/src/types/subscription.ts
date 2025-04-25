// Subscription Plan
// Note: Enums like PlanInterval and SubscriptionStatus are now imported
// directly from the generated Prisma client where needed.
export interface SubscriptionPlan {
  id: string;
  name: string;
  description?: string | null;
  price: number;
  currency: string;
  // interval: PlanInterval; // Use Prisma generated type directly in consuming code
  interval: string; // Temporarily use string, will be replaced by Prisma type import
  messageQuota: number;
  stripePriceId?: string | null;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateSubscriptionPlanDto {
  name: string;
  description?: string;
  price: number;
  currency?: string;
  // interval?: PlanInterval; // Use Prisma generated type directly in consuming code
  interval?: string; // Temporarily use string, will be replaced by Prisma type import
  messageQuota: number;
  stripePriceId?: string;
  isActive?: boolean;
}

export interface UpdateSubscriptionPlanDto {
  name?: string;
  description?: string;
  price?: number;
  currency?: string;
  // interval?: PlanInterval; // Use Prisma generated type directly in consuming code
  interval?: string; // Temporarily use string, will be replaced by Prisma type import
  messageQuota?: number;
  stripePriceId?: string;
  isActive?: boolean;
}

// User Subscription
export interface UserSubscription {
  id: string;
  userId: string;
  planId: string;
  // status: SubscriptionStatus; // Use Prisma generated type directly in consuming code
  status: string; // Temporarily use string, will be replaced by Prisma type import
  currentPeriodStart?: Date | null;
  currentPeriodEnd?: Date | null;
  stripeSubscriptionId?: string | null;
  cancelAtPeriodEnd: boolean;
  remainingQuota?: number | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface UserSubscriptionDetails extends UserSubscription {
  plan: SubscriptionPlan;
}

export interface CreateUserSubscriptionDto {
  userId: string;
  planId: string;
  // status?: SubscriptionStatus; // Use Prisma generated type directly in consuming code
  status?: string; // Temporarily use string, will be replaced by Prisma type import
  currentPeriodStart?: Date;
  currentPeriodEnd?: Date;
  stripeSubscriptionId?: string;
  cancelAtPeriodEnd?: boolean;
  remainingQuota?: number;
}

export interface UpdateUserSubscriptionDto {
  planId?: string;
  // status?: SubscriptionStatus; // Use Prisma generated type directly in consuming code
  status?: string; // Temporarily use string, will be replaced by Prisma type import
  currentPeriodStart?: Date;
  currentPeriodEnd?: Date;
  stripeSubscriptionId?: string;
  cancelAtPeriodEnd?: boolean;
  remainingQuota?: number;
}

// Stripe-specific types
export interface CreateCheckoutSessionDto {
  planId: string;
  successUrl?: string;
  cancelUrl?: string;
}

export interface CheckoutSessionResponse {
  sessionId: string;
  url: string;
}

export interface CustomerPortalSessionResponse {
  url: string;
}

export interface UserSubscriptionQuotaResponse {
  totalQuota: number;
  usedQuota: number;
  remainingQuota: number;
  usagePercentage: number;
  currentPeriodStart?: Date;
  currentPeriodEnd?: Date;
  // status: SubscriptionStatus; // Use Prisma generated type directly in consuming code
  status: string; // Temporarily use string, will be replaced by Prisma type import
  plan: {
    id: string;
    name: string;
    description?: string;
    price: number;
    currency: string;
    // interval: PlanInterval; // Use Prisma generated type directly in consuming code
    interval: string; // Temporarily use string, will be replaced by Prisma type import
    messageQuota: number;
  };
}

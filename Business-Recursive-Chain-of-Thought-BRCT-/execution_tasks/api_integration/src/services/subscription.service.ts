import { PrismaClient, PlanInterval, SubscriptionStatus, Prisma } from '../generated/prisma'; // Import enums and Prisma namespace
// Use Prisma.TransactionClient for the interactive transaction type
import type { Prisma as PrismaTypes } from '../generated/prisma';
import Stripe from 'stripe';
import {
  CreateSubscriptionPlanDto,
  UpdateSubscriptionPlanDto,
  SubscriptionPlan,
  CreateUserSubscriptionDto,
  UpdateUserSubscriptionDto,
  UserSubscription,
  UserSubscriptionDetails,
  // SubscriptionStatus, // Removed from here
  UserSubscriptionQuotaResponse,
  CreateCheckoutSessionDto,
  CheckoutSessionResponse,
  CustomerPortalSessionResponse
} from '../types/subscription';
import { prisma } from '../lib/prisma';

class SubscriptionService {
  private stripe: Stripe;
  
  constructor() {
    if (!process.env.STRIPE_SECRET_KEY) {
      throw new Error('STRIPE_SECRET_KEY is not defined in environment variables');
    }
    this.stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
      apiVersion: '2023-10-16' as any, // Cast to any to avoid type errors with API version
    });
  }

  // Subscription Plan Methods
  async createSubscriptionPlan(data: CreateSubscriptionPlanDto): Promise<SubscriptionPlan> {
    // Create a price in Stripe if stripePriceId is not provided
    if (!data.stripePriceId) {
      const product = await this.stripe.products.create({
        name: data.name,
        description: data.description || `${data.name} - ${data.messageQuota} messages`,
        metadata: {
          messageQuota: data.messageQuota.toString(),
        },
      });

      const price = await this.stripe.prices.create({
        product: product.id,
        unit_amount: data.price,
        currency: data.currency || 'usd',
        recurring: {
          interval: (data.interval?.toLowerCase() || 'month') as 'month' | 'year',
        },
        metadata: {
          messageQuota: data.messageQuota.toString(),
        },
      });

      data.stripePriceId = price.id;
    }

    return prisma.subscriptionPlan.create({
      data: {
        name: data.name,
        description: data.description,
        price: data.price,
        currency: data.currency || 'usd',
        interval: data.interval ? PlanInterval[data.interval as keyof typeof PlanInterval] : PlanInterval.MONTH, // Use Prisma enum
        messageQuota: data.messageQuota,
        stripePriceId: data.stripePriceId,
        isActive: data.isActive !== undefined ? data.isActive : true,
      },
    });
  }

  async getSubscriptionPlans(): Promise<SubscriptionPlan[]> {
    return prisma.subscriptionPlan.findMany({
      where: { isActive: true },
      orderBy: { price: 'asc' },
    });
  }

  async getSubscriptionPlanById(id: string): Promise<SubscriptionPlan | null> {
    return prisma.subscriptionPlan.findUnique({
      where: { id },
    });
  }

  async updateSubscriptionPlan(id: string, data: UpdateSubscriptionPlanDto): Promise<SubscriptionPlan> {
    // Update Stripe product/price if necessary
    const plan = await prisma.subscriptionPlan.findUnique({ where: { id } });
    if (!plan) {
      throw new Error(`Subscription plan with ID ${id} not found`);
    }

    // If price or recurring interval changed, create a new price in Stripe
    if ((data.price && data.price !== plan.price) || 
        (data.interval && data.interval !== plan.interval)) {
      
      // Get the Stripe product ID from the existing price
      let productId: string | undefined;
      if (plan.stripePriceId) {
        const existingPrice = await this.stripe.prices.retrieve(plan.stripePriceId);
        productId = existingPrice.product as string;
      }

      // If no existing product, create one
      if (!productId) {
        const product = await this.stripe.products.create({
          name: data.name || plan.name,
          description: data.description || plan.description || undefined,
        });
        productId = product.id;
      }

      // Create new price
      const price = await this.stripe.prices.create({
        product: productId,
        unit_amount: data.price || plan.price,
        currency: data.currency || plan.currency,
        recurring: {
          // Use Prisma enum value directly if possible, or map string
          interval: ((data.interval || plan.interval) === PlanInterval.MONTH ? 'month' : 'year') as 'month' | 'year',
        },
        metadata: {
          messageQuota: (data.messageQuota || plan.messageQuota).toString(),
        },
      });

      data.stripePriceId = price.id;
    }

    // Update plan in database
    // Explicitly map fields to ensure type compatibility
    const updateData: any = { ...data };
    if (data.interval) {
      updateData.interval = PlanInterval[data.interval as keyof typeof PlanInterval];
    }

    return prisma.subscriptionPlan.update({
      where: { id },
      data: updateData,
    });
  }

  // User Subscription Methods
  async createUserSubscription(data: CreateUserSubscriptionDto): Promise<UserSubscription> {
    const user = await prisma.user.findUnique({ where: { id: data.userId } });
    if (!user) {
      throw new Error(`User with ID ${data.userId} not found`);
    }

    const plan = await prisma.subscriptionPlan.findUnique({ where: { id: data.planId } });
    if (!plan) {
      throw new Error(`Subscription plan with ID ${data.planId} not found`);
    }

    return prisma.userSubscription.create({
      data: {
        userId: data.userId,
        planId: data.planId,
        status: data.status ? SubscriptionStatus[data.status as keyof typeof SubscriptionStatus] : SubscriptionStatus.INACTIVE, // Use Prisma enum
        currentPeriodStart: data.currentPeriodStart,
        currentPeriodEnd: data.currentPeriodEnd,
        stripeSubscriptionId: data.stripeSubscriptionId,
        cancelAtPeriodEnd: data.cancelAtPeriodEnd || false,
        remainingQuota: data.remainingQuota !== undefined ? data.remainingQuota : plan.messageQuota,
      },
    });
  }

  async getUserSubscription(userId: string): Promise<UserSubscriptionDetails | null> {
    return prisma.userSubscription.findUnique({
      where: { userId },
      include: { plan: true },
    });
  }

  async updateUserSubscription(userId: string, data: UpdateUserSubscriptionDto): Promise<UserSubscription> {
    // Explicitly map fields to ensure type compatibility
    const updateData: any = { ...data };
     if (data.status) {
      updateData.status = SubscriptionStatus[data.status as keyof typeof SubscriptionStatus];
    }
    // Remove planId if present, as it's not directly updatable here (part of relation)
    delete updateData.planId;


    return prisma.userSubscription.update({
      where: { userId },
      data: updateData,
    });
  }

  async getUserSubscriptionQuota(userId: string): Promise<UserSubscriptionQuotaResponse> {
    const subscription = await prisma.userSubscription.findUnique({
      where: { userId },
      include: { plan: true, user: true },
    });

    if (!subscription) {
      throw new Error(`User with ID ${userId} does not have an active subscription`);
    }

    const { plan, remainingQuota, status, currentPeriodStart, currentPeriodEnd, user } = subscription;
    const usedQuota = user.messageCount;
    const totalQuota = plan.messageQuota;
    const actualRemainingQuota = remainingQuota !== null ? remainingQuota : Math.max(0, totalQuota - usedQuota);
    const usagePercentage = Math.min(100, Math.round((usedQuota / totalQuota) * 100));

    return {
      totalQuota,
      usedQuota,
      remainingQuota: actualRemainingQuota,
      usagePercentage,
      currentPeriodStart: currentPeriodStart || undefined,
      currentPeriodEnd: currentPeriodEnd || undefined,
      // status, // Removed duplicate assignment
      // Cast Prisma types back to expected response types if necessary
      // (Assuming UserSubscriptionQuotaResponse uses string enums for now)
      status: status as string, // Cast Prisma enum back to string for response
      plan: {
        id: plan.id,
        name: plan.name,
        description: plan.description || undefined,
        price: plan.price,
        currency: plan.currency,
        interval: plan.interval as string, // Cast Prisma enum back to string for response
        messageQuota: plan.messageQuota,
      },
    };
  }

  async decrementUserQuota(userId: string, count: number = 1): Promise<number | null> {
    // Start a transaction with the correct type for tx
    return prisma.$transaction(async (tx: PrismaTypes.TransactionClient) => {
      // Increment user message count
      await tx.user.update({
        where: { id: userId },
        data: { messageCount: { increment: count } },
      });

      // Get the user's subscription
      const subscription = await tx.userSubscription.findUnique({
        where: { userId },
        include: { plan: true },
      });

      // If no subscription or inactive, return null (no quota left)
      if (!subscription || subscription.status !== SubscriptionStatus.ACTIVE) { // Use Prisma enum
        return null;
      }

      // If remainingQuota is null, calculate based on plan's messageQuota and user's messageCount
      if (subscription.remainingQuota === null) {
        const user = await tx.user.findUnique({ where: { id: userId } });
        if (!user) return null;

        const newRemainingQuota = Math.max(0, subscription.plan.messageQuota - user.messageCount);
        
        // Update the subscription with calculated remaining quota
        await tx.userSubscription.update({
          where: { userId },
          data: { remainingQuota: newRemainingQuota },
        });
        
        return newRemainingQuota;
      }
      
      // Otherwise, decrement the remaining quota directly
      const newRemainingQuota = Math.max(0, subscription.remainingQuota - count);
      
      // Update the subscription
      await tx.userSubscription.update({
        where: { userId },
        data: { remainingQuota: newRemainingQuota },
      });
      
      return newRemainingQuota;
    });
  }

  // Stripe Integration Methods
  async createCheckoutSession(userId: string, dto: CreateCheckoutSessionDto): Promise<CheckoutSessionResponse> {
    const user = await prisma.user.findUnique({ where: { id: userId } });
    if (!user) {
      throw new Error(`User with ID ${userId} not found`);
    }

    const plan = await prisma.subscriptionPlan.findUnique({ where: { id: dto.planId } });
    if (!plan) {
      throw new Error(`Subscription plan with ID ${dto.planId} not found`);
    }

    if (!plan.stripePriceId) {
      throw new Error(`Subscription plan with ID ${dto.planId} does not have a Stripe price ID`);
    }

    // Ensure customer exists in Stripe
    let customerId = user.stripeCustomerId;
    if (!customerId) {
      const customer = await this.stripe.customers.create({
        email: user.email,
        name: user.fullName || undefined,
        metadata: {
          userId: user.id,
        },
      });
      
      customerId = customer.id;
      
      // Update user with Stripe customer ID
      await prisma.user.update({
        where: { id: userId },
        data: { stripeCustomerId: customerId },
      });
    }

    // Create checkout session
    const session = await this.stripe.checkout.sessions.create({
      customer: customerId,
      payment_method_types: ['card'],
      line_items: [
        {
          price: plan.stripePriceId,
          quantity: 1,
        },
      ],
      mode: 'subscription',
      success_url: dto.successUrl || process.env.STRIPE_SUCCESS_URL || `${process.env.FRONTEND_URL}/settings/subscription?success=true`,
      cancel_url: dto.cancelUrl || process.env.STRIPE_CANCEL_URL || `${process.env.FRONTEND_URL}/settings/subscription?canceled=true`,
      metadata: {
        userId,
        planId: plan.id,
      },
    });

    return {
      sessionId: session.id,
      url: session.url || '',
    };
  }

  async createCustomerPortalSession(userId: string): Promise<CustomerPortalSessionResponse> {
    const user = await prisma.user.findUnique({ where: { id: userId } });
    if (!user || !user.stripeCustomerId) {
      throw new Error(`User with ID ${userId} does not have a Stripe customer ID`);
    }

    const session = await this.stripe.billingPortal.sessions.create({
      customer: user.stripeCustomerId,
      return_url: `${process.env.FRONTEND_URL}/settings/subscription`,
    });

    return {
      url: session.url,
    };
  }

  // Webhook Event Handling
  async handleWebhookEvent(event: Stripe.Event): Promise<any> {
    const { type, data } = event;

    switch (type) {
      case 'checkout.session.completed':
        return this.handleCheckoutSessionCompleted(data.object as Stripe.Checkout.Session);
      
      case 'invoice.paid':
        return this.handleInvoicePaid(data.object as Stripe.Invoice);
      
      case 'invoice.payment_failed':
        return this.handleInvoicePaymentFailed(data.object as Stripe.Invoice);
      
      case 'customer.subscription.updated':
        return this.handleSubscriptionUpdated(data.object as Stripe.Subscription);
      
      case 'customer.subscription.deleted':
        return this.handleSubscriptionDeleted(data.object as Stripe.Subscription);
      
      default:
        console.log(`Unhandled event type ${type}`);
        return { received: true };
    }
  }

  private async handleCheckoutSessionCompleted(session: Stripe.Checkout.Session): Promise<any> {
    // Extract metadata from session
    const { userId, planId } = session.metadata || {};
    if (!userId || !planId) {
      throw new Error('Missing metadata in checkout session');
    }

    // Get subscription from Stripe
    if (!session.subscription) {
      throw new Error('Missing subscription in checkout session');
    }
    
    const subscription = await this.stripe.subscriptions.retrieve(
      session.subscription as string
    );

    // Get plan details
    const plan = await prisma.subscriptionPlan.findUnique({ where: { id: planId } });
    if (!plan) {
      throw new Error(`Subscription plan with ID ${planId} not found`);
    }

    // Check if user already has a subscription
    const existingSubscription = await prisma.userSubscription.findUnique({
      where: { userId },
    });

    // Calculate current period - cast to any to access stripe properties
    const currentPeriodStart = new Date(((subscription as any).current_period_start || 0) * 1000);
    const currentPeriodEnd = new Date(((subscription as any).current_period_end || 0) * 1000);

    if (existingSubscription) {
      // Update existing subscription
      return prisma.userSubscription.update({
        where: { userId },
        data: {
          planId,
          status: SubscriptionStatus.ACTIVE, // Use Prisma enum
          stripeSubscriptionId: subscription.id,
          currentPeriodStart,
          currentPeriodEnd,
          remainingQuota: plan.messageQuota,
          cancelAtPeriodEnd: subscription.cancel_at_period_end,
        },
      });
    } else {
      // Create new subscription
      return prisma.userSubscription.create({
        data: {
          userId,
          planId,
          status: SubscriptionStatus.ACTIVE, // Use Prisma enum
          stripeSubscriptionId: subscription.id,
          currentPeriodStart,
          currentPeriodEnd,
          remainingQuota: plan.messageQuota,
          cancelAtPeriodEnd: subscription.cancel_at_period_end,
        },
      });
    }
  }

  private async handleInvoicePaid(invoice: Stripe.Invoice): Promise<any> {
    // Cast to any to access non-standard properties
    const subscriptionId = (invoice as any).subscription;
    if (!subscriptionId) return { received: true };

    const subscription = await this.stripe.subscriptions.retrieve(
      subscriptionId as string
    );

    // Find the user by Stripe customer ID
    const user = await prisma.user.findFirst({
      where: { stripeCustomerId: invoice.customer as string },
    });

    if (!user) {
      throw new Error(`User with Stripe customer ID ${invoice.customer} not found`);
    }

    // Get user's subscription
    const userSubscription = await prisma.userSubscription.findUnique({
      where: { userId: user.id },
      include: { plan: true },
    });

    if (!userSubscription) {
      throw new Error(`User with ID ${user.id} does not have a subscription`);
    }

      // Update subscription with new billing period
      return prisma.userSubscription.update({
        where: { userId: user.id },
        data: {
          status: SubscriptionStatus.ACTIVE, // Use Prisma enum
          currentPeriodStart: new Date(((subscription as any).current_period_start || 0) * 1000),
          currentPeriodEnd: new Date(((subscription as any).current_period_end || 0) * 1000),
        remainingQuota: userSubscription.plan.messageQuota, // Reset quota
        cancelAtPeriodEnd: (subscription as any).cancel_at_period_end || false,
      },
    });
  }

  private async handleInvoicePaymentFailed(invoice: Stripe.Invoice): Promise<any> {
    const subscriptionId = (invoice as any).subscription;
    if (!subscriptionId) return { received: true };

    // Find the user by Stripe customer ID
    const user = await prisma.user.findFirst({
      where: { stripeCustomerId: invoice.customer as string },
    });

    if (!user) {
      throw new Error(`User with Stripe customer ID ${invoice.customer} not found`);
    }

      // Update subscription status to PAST_DUE
      return prisma.userSubscription.update({
        where: { userId: user.id },
        data: {
          status: SubscriptionStatus.PAST_DUE, // Use Prisma enum
        },
      });
  }

  private async handleSubscriptionUpdated(subscription: Stripe.Subscription): Promise<any> {
    // Find the user by Stripe customer ID
    const user = await prisma.user.findFirst({
      where: { stripeCustomerId: subscription.customer as string },
    });

    if (!user) {
      throw new Error(`User with Stripe customer ID ${subscription.customer} not found`);
    }

    // Map Stripe status to our Prisma status
    let status: SubscriptionStatus = SubscriptionStatus.INACTIVE; // Use Prisma enum
    switch (subscription.status) {
      case 'active':
        status = SubscriptionStatus.ACTIVE; // Use Prisma enum
        break;
      case 'past_due':
        status = SubscriptionStatus.PAST_DUE; // Use Prisma enum
        break;
      case 'canceled':
        status = SubscriptionStatus.CANCELED; // Use Prisma enum
        break;
      case 'trialing':
        status = SubscriptionStatus.TRIAL; // Use Prisma enum
        break;
      default:
        status = SubscriptionStatus.INACTIVE; // Use Prisma enum
    }

    // Update subscription
    return prisma.userSubscription.update({
      where: { userId: user.id },
      data: {
        status,
        currentPeriodStart: new Date(((subscription as any).current_period_start || 0) * 1000),
        currentPeriodEnd: new Date(((subscription as any).current_period_end || 0) * 1000),
        cancelAtPeriodEnd: (subscription as any).cancel_at_period_end || false,
      },
    });
  }

  private async handleSubscriptionDeleted(subscription: Stripe.Subscription): Promise<any> {
    // Find the user by Stripe customer ID
    const user = await prisma.user.findFirst({
      where: { stripeCustomerId: subscription.customer as string },
    });

    if (!user) {
      throw new Error(`User with Stripe customer ID ${subscription.customer} not found`);
    }

      // Update subscription status to CANCELED
      return prisma.userSubscription.update({
        where: { userId: user.id },
        data: {
          status: SubscriptionStatus.CANCELED, // Use Prisma enum
        },
      });
  }
}

export default new SubscriptionService();

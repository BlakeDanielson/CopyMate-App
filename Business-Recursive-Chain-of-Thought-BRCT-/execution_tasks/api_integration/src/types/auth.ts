/**
 * Authentication types
 */

// Note: Role enum is now imported directly from the generated Prisma client where needed.

// Usage metrics interface
export interface UserMetrics {
  usedMessages: number;
  totalQuota: number;
  remainingMessages: number;
  usagePercentage: number;
  billingPeriodStart: Date;
  billingPeriodEnd: Date;
  messagesPerProvider?: Record<string, number>;
}

// User type definition based on our Prisma schema
export interface User {
  id: string;
  email: string;
  passwordHash: string;
  username?: string | null;
  fullName?: string | null;
  // role: Role; // Use Prisma generated type directly in consuming code
  role: string; // Temporarily use string, will be replaced by Prisma type import
  messageCount: number;
  createdAt: Date;
  updatedAt: Date;
}

export type UserWithoutPassword = Omit<User, 'passwordHash'>;

export interface UserPayload {
  id: string;
  email: string;
  role: string;
}

export interface RegisterUserInput {
  email: string;
  password: string;
  username?: string;
  fullName?: string;
}

export interface LoginUserInput {
  email: string;
  password: string;
}

export interface SignUpUserInput {
  email: string;
  password: string;
  confirmPassword: string;
}
export interface AuthTokens {
  accessToken: string;
}

export interface TokenDecoded {
  userId: string;
  email: string;
  role: string;
  iat: number;
  exp: number;
}

// Express request with user extension
declare global {
  namespace Express {
    interface Request {
      user?: UserPayload;
    }
  }
}

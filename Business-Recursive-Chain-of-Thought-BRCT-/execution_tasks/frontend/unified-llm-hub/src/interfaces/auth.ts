export enum Role {
  USER = "USER",
  ADMIN = "ADMIN",
}

export interface UserMetrics {
  usedMessages: number;
  totalQuota: number;
  remainingMessages: number;
  usagePercentage: number;
  billingPeriodStart: string;
  billingPeriodEnd: string;
  messagesPerProvider?: Record<string, number>;
}

export interface User {
  id: string;
  email: string;
  name?: string;
  profileImage?: string;
  role?: Role;
  createdAt: Date;
  lastLoginAt: Date;
  preferences: UserPreferences;
  subscription?: Subscription;
  metrics?: UserMetrics;
}

export interface UserPreferences {
  theme: "light" | "dark" | "system";
  defaultModel?: string;
  defaultProvider?: string;
  defaultParameters?: {
    temperature: number;
    maxTokens: number;
    topP: number;
  };
}

export interface Subscription {
  id: string;
  plan: "free" | "basic" | "premium" | "enterprise";
  status: "active" | "canceled" | "expired" | "trial";
  currentPeriodStart: Date;
  currentPeriodEnd: Date;
  messageQuota: number;
  messageUsed: number;
  paymentMethod?: {
    type: string;
    last4?: string;
  };
}

export interface SignUpUserInput {
  email: string;
  password: string;
  confirmPassword: string;
}
export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

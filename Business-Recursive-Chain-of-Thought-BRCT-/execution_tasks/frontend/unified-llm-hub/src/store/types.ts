import {
  Conversation,
  LLMModel,
  LLMParameters,
  LLMProvider,
} from "../interfaces/llm";
import { User } from "../interfaces/auth";
import {
  AnalyticsDashboardData,
  ApiPerformanceMetrics,
  LlmPerformanceMetrics,
  TimeWindow,
} from "../interfaces/analytics";

// UI State
export interface Notification {
  id: string;
  type: "success" | "error" | "info" | "warning";
  message: string;
  timestamp: Date;
  read: boolean;
}

export interface UiState {
  sidebarOpen: boolean;
  theme: "light" | "dark" | "system";
  settingsOpen: boolean;
  activeTab: string;
  notifications: Notification[];
}

// Auth State
export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

// Conversation State
export interface ConversationState {
  conversations: Conversation[];
  activeConversation: Conversation | null;
  loading: boolean;
  error: string | null;
  streaming: boolean;
}

// LLM State
export interface LLMState {
  providers: LLMProvider[];
  models: LLMModel[];
  selectedProvider: string | null;
  selectedModel: string | null;
  parameters: LLMParameters;
  loading: boolean;
  error: string | null;
  performanceMetrics: {
    [key: string]: any;
  };
}

// Analytics State
export interface AnalyticsState {
  dashboard: {
    data: AnalyticsDashboardData | null;
    loading: boolean;
    error: string | null;
  };
  apiPerformance: {
    data: ApiPerformanceMetrics[];
    loading: boolean;
    error: string | null;
  };
  llmPerformance: {
    data: LlmPerformanceMetrics[];
    loading: boolean;
    error: string | null;
  };
  filters: {
    timeWindow: TimeWindow;
    startDate: string | null;
    endDate: string | null;
    providers: string[];
    models: string[];
    endpoints: string[];
    successOnly: boolean;
  };
  availableFilters: {
    providers: string[];
    models: Record<string, string[]>;
    endpoints: string[];
    loading: boolean;
    error: string | null;
  };
}

// Subscription State
export interface SubscriptionState {
  plans: any[];
  currentSubscription: any | null;
  loading: boolean;
  error: string | null;
}

// Root State
export interface RootState {
  ui: UiState;
  auth: AuthState;
  conversation: ConversationState;
  llm: LLMState;
  subscription: SubscriptionState;
  analytics: AnalyticsState;
}

// AppDispatch type
export type AppDispatch = any; // We'll define this more precisely once the store is set up

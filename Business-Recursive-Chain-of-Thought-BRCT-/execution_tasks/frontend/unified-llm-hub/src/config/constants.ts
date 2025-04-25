// API URLs
export const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:3002/api/v1";
export const AUTH_API_URL = `${API_BASE_URL}/auth`;
export const LLM_API_URL = `${API_BASE_URL}/llm`;
export const USER_API_URL = `${API_BASE_URL}/users`;
export const CONVERSATIONS_API_URL = `${API_BASE_URL}/conversations`;
export const ADMIN_API_URL = `${API_BASE_URL}/admin`;

// Providers
export const PROVIDERS = {
  OPENAI: "openai",
  ANTHROPIC: "anthropic",
  GEMINI: "gemini",
};

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: "auth_token",
  USER: "user",
  THEME: "theme",
  CONVERSATIONS: "conversations",
  CURRENT_CONVERSATION: "current_conversation",
  SETTINGS: "settings",
};

// Theme
export const THEMES = {
  LIGHT: "light",
  DARK: "dark",
  SYSTEM: "system",
};

// Default parameters
export const DEFAULT_PARAMETERS = {
  temperature: 0.7,
  maxTokens: 1000,
  topP: 0.9,
};

// Message roles
export const MESSAGE_ROLES = {
  USER: "user",
  ASSISTANT: "assistant",
  SYSTEM: "system",
};

// Performance metrics
export const PERFORMANCE_THRESHOLDS = {
  EXCELLENT_TTFT: 100, // Time to first token in ms
  GOOD_TTFT: 300,
  AVERAGE_TTFT: 500,
  SLOW_TTFT: 1000,
};

// Rate limiting
export const RATE_LIMITING = {
  MAX_REQUESTS_PER_MINUTE: 60,
  THROTTLE_INTERVAL: 1000, // ms
};

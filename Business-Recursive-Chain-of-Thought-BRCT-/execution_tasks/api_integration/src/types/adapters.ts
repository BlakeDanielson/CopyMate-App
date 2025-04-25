/**
 * Common types for LLM adapters
 */

/**
 * Unified completion parameters across all LLM providers
 */
export interface CompletionParams {
  temperature: number;
  maxTokens: number;
  topP: number;
  stopSequences?: string[];
  presencePenalty?: number;
  frequencyPenalty?: number;
  model: string;
}

/**
 * Unified completion response across all LLM providers
 */
export interface CompletionResponse {
  text: string;
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  provider: string;
  model: string;
  metrics?: {
    timeToFirstToken?: number;
    totalTime?: number;
    tokensPerSecond?: number;
  };
}

/**
 * Callback function for streaming completions
 */
export type StreamCallback = (chunk: string, done: boolean, error?: Error) => void;

/**
 * Provider-specific error converted to a standard format
 */
export interface LLMError extends Error {
  provider: string;
  statusCode?: number;
  type: LLMErrorType;
  retryable: boolean;
  original?: unknown;
}

/**
 * Standardized error types across providers
 */
export enum LLMErrorType {
  AUTHENTICATION = 'authentication',
  RATE_LIMIT = 'rate_limit',
  CONTEXT_LENGTH = 'context_length',
  CONTENT_FILTER = 'content_filter',
  INVALID_REQUEST = 'invalid_request',
  SERVER_ERROR = 'server_error',
  TIMEOUT = 'timeout',
  UNKNOWN = 'unknown'
}

/**
 * Configuration for initializing a specific provider adapter
 */
export interface AdapterConfig {
  apiKey: string;
  defaultModel: string;
  organization?: string;
  baseUrl?: string;
  timeout?: number;
  maxRetries?: number;
}

/**
 * Usage data collected during LLM interactions
 */
export interface UsageData {
  userId?: string;
  provider: string;
  model: string;
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  timestamp: Date;
  conversationId?: string;
  messageId?: string;
}

/**
 * Provider-specific model configuration
 */
export interface ModelConfig {
  id: string;
  provider: string;
  maxTokens: number;
  trainingCutoff?: Date;
  capabilities: string[];
  defaultParameters?: Partial<CompletionParams>;
  costPer1kTokens?: {
    input: number;
    output: number;
  };
}

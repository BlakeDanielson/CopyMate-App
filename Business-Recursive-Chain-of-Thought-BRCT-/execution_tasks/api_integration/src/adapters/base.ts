/**
 * Base adapter implementation with common functionality for all providers
 */

import { LLMInterface } from './interface';
import {
  AdapterConfig,
  CompletionParams,
  CompletionResponse,
  LLMError,
  LLMErrorType,
  StreamCallback,
  UsageData
} from '../types/adapters';

/**
 * Abstract base class implementing common functionality for all LLM adapters
 */
export abstract class BaseAdapter implements LLMInterface {
  /**
   * Provider name (to be set by subclasses)
   */
  abstract readonly provider: string;

  /**
   * API key for authentication with the provider
   */
  protected apiKey: string;

  /**
   * Default model to use if not specified
   */
  protected defaultModel: string;

  /**
   * Maximum number of retries for API calls
   */
  protected maxRetries: number;

  /**
   * Timeout for API calls in milliseconds
   */
  protected timeout: number;

  /**
   * Usage statistics
   */
  protected usageStats: UsageData[] = [];

  /**
   * Constructor for the base adapter
   * 
   * @param config Configuration options for the adapter
   */
  constructor(config: AdapterConfig) {
    if (!config.apiKey) {
      throw new Error('API key is required');
    }

    this.apiKey = config.apiKey;
    this.defaultModel = config.defaultModel;
    this.maxRetries = config.maxRetries || 3;
    this.timeout = config.timeout || 30000; // 30 seconds default
  }

  /**
   * Abstract methods to be implemented by subclasses
   */
  abstract getAvailableModels(): Promise<string[]>;
  abstract generateCompletion(prompt: string, parameters: CompletionParams): Promise<CompletionResponse>;
  abstract streamCompletion(prompt: string, parameters: CompletionParams, callback: StreamCallback): Promise<void>;
  abstract estimateTokenCount(text: string, modelId?: string): number;

  /**
   * Default implementation of health check - can be overridden by subclasses
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.getAvailableModels();
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Default implementation to get usage statistics
   */
  async getUsageStatistics(): Promise<UsageData | null> {
    if (this.usageStats.length === 0) {
      return null;
    }

    // Calculate aggregate usage
    const totalUsage: UsageData = {
      provider: this.provider,
      model: 'all',
      promptTokens: 0,
      completionTokens: 0,
      totalTokens: 0,
      timestamp: new Date()
    };

    this.usageStats.forEach(stat => {
      totalUsage.promptTokens += stat.promptTokens;
      totalUsage.completionTokens += stat.completionTokens;
      totalUsage.totalTokens += stat.totalTokens;
    });

    return totalUsage;
  }

  /**
   * Log usage data
   * 
   * @param usage Usage data to log
   */
  protected logUsage(usage: UsageData): void {
    this.usageStats.push({
      ...usage,
      timestamp: usage.timestamp || new Date()
    });

    // In a real implementation, this would likely save to a database
    console.log(`Usage logged for ${this.provider}: ${usage.totalTokens} tokens`);
  }

  /**
   * Handle rate limiting errors with exponential backoff
   * 
   * @param error The error that occurred
   * @param retryCount Current retry attempt (starts at 0)
   * @returns A promise that resolves when ready to retry, or rejects if max retries exceeded
   */
  protected async handleRateLimiting(error: any, retryCount: number = 0): Promise<void> {
    // If we've exceeded max retries or the error is not retryable, don't retry
    if (retryCount >= this.maxRetries || !this.isRetryableError(error)) {
      throw this.standardizeError(error);
    }

    // Calculate delay with exponential backoff and jitter
    const baseDelay = 100; // 100ms base delay
    const maxDelay = 10000; // 10 second max delay
    const expBackoff = Math.min(
      maxDelay,
      baseDelay * Math.pow(2, retryCount)
    );
    
    // Add jitter (±10%)
    const jitterFactor = 0.1;
    const jitter = expBackoff * jitterFactor;
    const delay = Math.floor(expBackoff + (Math.random() * 2 - 1) * jitter);

    console.log(`Rate limit hit, retrying in ${delay}ms (attempt ${retryCount + 1}/${this.maxRetries})`);
    
    // Wait before retrying
    return new Promise(resolve => setTimeout(resolve, delay));
  }

  /**
   * Determine if an error should be retried
   * 
   * @param error The error to check
   * @returns True if the error is retryable
   */
  protected isRetryableError(error: any): boolean {
    // Rate limit errors
    if (error.status === 429 || error.statusCode === 429) {
      return true;
    }

    // Server errors (5xx)
    if (error.status >= 500 || error.statusCode >= 500) {
      return true;
    }

    // Network errors
    if (
      error.code === 'ECONNRESET' ||
      error.code === 'ETIMEDOUT' ||
      error.code === 'ECONNABORTED' ||
      error.message?.includes('network') ||
      error.message?.includes('timeout')
    ) {
      return true;
    }

    return false;
  }

  /**
   * Standardize errors from different providers to a common format
   * 
   * @param error The original error
   * @returns A standardized LLMError
   */
  protected standardizeError(error: any): LLMError {
    let type = LLMErrorType.UNKNOWN;
    let statusCode: number | undefined = undefined;
    let message = error.message || 'Unknown error';
    let retryable = false;

    // Extract status code if available
    if (error.status || error.statusCode) {
      statusCode = error.status || error.statusCode;
    }

    // Determine error type based on status code and message
    if (statusCode === 401 || statusCode === 403 || message.includes('auth')) {
      type = LLMErrorType.AUTHENTICATION;
    } else if (statusCode === 429 || message.includes('rate') || message.includes('limit')) {
      type = LLMErrorType.RATE_LIMIT;
      retryable = true;
    } else if (message.includes('context') || message.includes('token') || message.includes('length')) {
      type = LLMErrorType.CONTEXT_LENGTH;
    } else if (message.includes('content') || message.includes('policy') || message.includes('filter')) {
      type = LLMErrorType.CONTENT_FILTER;
    } else if (statusCode === 400 || statusCode === 404) {
      type = LLMErrorType.INVALID_REQUEST;
    } else if (statusCode && statusCode >= 500) {
      type = LLMErrorType.SERVER_ERROR;
      retryable = true;
    } else if (message.includes('timeout') || error.code === 'ETIMEDOUT') {
      type = LLMErrorType.TIMEOUT;
      retryable = true;
    }

    // Create standardized error object
    const llmError = new Error(message) as LLMError;
    llmError.provider = this.provider;
    llmError.statusCode = statusCode;
    llmError.type = type;
    llmError.retryable = retryable;
    llmError.original = error;
    llmError.name = 'LLMError';

    return llmError;
  }

  /**
   * Validate and normalize completion parameters
   * 
   * @param params User-provided parameters
   * @returns Normalized parameters with defaults applied
   */
  protected normalizeParams(params: Partial<CompletionParams>): CompletionParams {
    return {
      temperature: params.temperature !== undefined ? params.temperature : 0.7,
      maxTokens: params.maxTokens !== undefined ? params.maxTokens : 1000,
      topP: params.topP !== undefined ? params.topP : 1.0,
      stopSequences: params.stopSequences || [],
      presencePenalty: params.presencePenalty || 0,
      frequencyPenalty: params.frequencyPenalty || 0,
      model: params.model || this.defaultModel
    };
  }

  /**
   * Calculate response metrics
   * 
   * @param startTime Start time of the request
   * @param firstTokenTime Time when first token was received (optional)
   * @param totalTokens Number of tokens in the response
   * @returns Metrics object
   */
  protected calculateMetrics(startTime: number, firstTokenTime: number | null, totalTokens: number): CompletionResponse['metrics'] {
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    
    const metrics: CompletionResponse['metrics'] = {
      totalTime
    };

    if (firstTokenTime) {
      metrics.timeToFirstToken = firstTokenTime - startTime;
    }

    if (totalTokens > 0 && totalTime > 0) {
      // Calculate tokens per second (tokenCount / (totalTime / 1000))
      metrics.tokensPerSecond = (totalTokens / totalTime) * 1000;
    }

    return metrics;
  }
}

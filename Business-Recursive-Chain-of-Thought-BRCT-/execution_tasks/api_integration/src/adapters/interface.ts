/**
 * LLM Interface defining the contract for all provider adapters
 */

import { 
  CompletionParams, 
  CompletionResponse, 
  StreamCallback, 
  LLMError,
  UsageData
} from '../types/adapters';

/**
 * Core interface that all LLM adapters must implement
 */
export interface LLMInterface {
  /**
   * Provider name (e.g., "openai", "anthropic", "gemini")
   */
  readonly provider: string;

  /**
   * Get a list of available models for this provider
   */
  getAvailableModels(): Promise<string[]>;

  /**
   * Generate a completion for the given prompt
   * 
   * @param prompt The input text to get a completion for
   * @param parameters Configuration parameters for the completion
   * @returns A completion response with the generated text
   * @throws LLMError if the request fails
   */
  generateCompletion(prompt: string, parameters: CompletionParams): Promise<CompletionResponse>;

  /**
   * Stream a completion for the given prompt, delivering chunks as they become available
   * 
   * @param prompt The input text to get a completion for
   * @param parameters Configuration parameters for the completion
   * @param callback Function called for each chunk of the response
   * @throws LLMError if the request fails
   */
  streamCompletion(prompt: string, parameters: CompletionParams, callback: StreamCallback): Promise<void>;

  /**
   * Check if the adapter's API connection is healthy
   * 
   * @returns True if the connection is healthy, false otherwise
   */
  healthCheck(): Promise<boolean>;

  /**
   * Estimate token count for a given text
   * 
   * @param text The text to estimate tokens for
   * @param modelId Optional model ID (different models may count tokens differently)
   * @returns Estimated token count
   */
  estimateTokenCount(text: string, modelId?: string): number;

  /**
   * Get the current usage data for this adapter
   * 
   * @returns Usage statistics or null if not available
   */
  getUsageStatistics(): Promise<UsageData | null>;
}

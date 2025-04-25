/**
 * Factory for creating LLM adapters
 */

import { OpenAIAdapter } from './openai';
import { AnthropicAdapter } from './anthropic';
import { GeminiAdapter } from './gemini';
import { LLMInterface } from './interface';
import { AdapterConfig } from '../types/adapters';

/**
 * Factory class for creating provider-specific adapters
 */
export class AdapterFactory {
  /**
   * Create an adapter instance for the specified provider
   * 
   * @param provider Provider name (e.g., 'openai', 'anthropic', 'gemini')
   * @param config Configuration for the adapter
   * @returns An instance of the appropriate adapter
   * @throws Error if the provider is not supported
   */
  static createAdapter(provider: string, config: AdapterConfig): LLMInterface {
    switch (provider.toLowerCase()) {
      case 'openai':
        return new OpenAIAdapter(config);
      
      case 'anthropic':
        return new AnthropicAdapter(config);
      
      case 'gemini':
        return new GeminiAdapter(config);
      
      default:
        throw new Error(`Unsupported provider: ${provider}`);
    }
  }

  /**
   * Get all supported provider names
   * 
   * @returns Array of supported provider names
   */
  static getSupportedProviders(): string[] {
    return ['openai', 'anthropic', 'gemini'];
  }

  /**
   * Get default model for a specific provider
   * 
   * @param provider Provider name
   * @returns Default model name for the provider
   */
  static getDefaultModel(provider: string): string {
    switch (provider.toLowerCase()) {
      case 'openai':
        return 'gpt-4';
      
      case 'anthropic':
        return 'claude-3-sonnet-20240229';
      
      case 'gemini':
        return 'gemini-pro';
      
      default:
        throw new Error(`Unsupported provider: ${provider}`);
    }
  }

  /**
   * Check if a provider is supported
   * 
   * @param provider Provider name to check
   * @returns True if the provider is supported
   */
  static isProviderSupported(provider: string): boolean {
    return this.getSupportedProviders().includes(provider.toLowerCase());
  }
}

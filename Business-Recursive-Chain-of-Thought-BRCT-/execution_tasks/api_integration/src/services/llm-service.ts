/**
 * LLM Service for managing adapters and provider access
 */

import { LLMInterface } from '../adapters/interface';
import { AdapterFactory } from '../adapters/factory';
import { KeyManager } from '../utils/key-management';
import { LlmPerformanceTracker } from '../utils/llm-performance-tracker';
import {
  AdapterConfig,
  CompletionParams,
  CompletionResponse,
  StreamCallback,
  UsageData
} from '../types/adapters';

/**
 * Service for unified access to multiple LLM providers
 */
export class LLMService {
  /**
   * Active adapters, keyed by provider name
   */
  private adapters: Map<string, LLMInterface> = new Map();
  
  /**
   * Key manager for API key storage and retrieval
   */
  private keyManager: KeyManager;
  
  /**
   * Map of the default models for each provider
   */
  private defaultModels: Map<string, string> = new Map();
  
  /**
   * Flag indicating if the service is ready to use
   */
  private isInitialized = false;

  /**
   * Constructor
   * 
   * @param keyManager Key manager instance
   * @param defaultModels Optional map of default models to use for each provider
   */
  constructor(keyManager: KeyManager, defaultModels?: Record<string, string>) {
    this.keyManager = keyManager;
    
    // Set default models
    const supportedProviders = AdapterFactory.getSupportedProviders();
    supportedProviders.forEach(provider => {
      const defaultModel = defaultModels?.[provider] || AdapterFactory.getDefaultModel(provider);
      this.defaultModels.set(provider, defaultModel);
    });
  }

  /**
   * Initialize the service by creating adapters for all available providers
   * 
   * @returns True if initialization was successful
   */
  async initialize(): Promise<boolean> {
    try {
      const supportedProviders = AdapterFactory.getSupportedProviders();
      const initializedAdapters: string[] = [];
      
      for (const provider of supportedProviders) {
        // Check if we have a valid API key for this provider
        const apiKey = this.keyManager.getKey(provider);
        if (!apiKey) {
          console.log(`No API key found for ${provider}, skipping initialization`);
          continue;
        }
        
        try {
          // Create adapter config
          const config: AdapterConfig = {
            apiKey,
            defaultModel: this.defaultModels.get(provider) || AdapterFactory.getDefaultModel(provider)
          };
          
          // Create and initialize adapter
          const adapter = AdapterFactory.createAdapter(provider, config);
          
          // Test connection with health check
          const healthy = await adapter.healthCheck();
          if (!healthy) {
            console.error(`Health check failed for ${provider}`);
            continue;
          }
          
          // Add to active adapters
          this.adapters.set(provider, adapter);
          initializedAdapters.push(provider);
        } catch (error) {
          console.error(`Error initializing adapter for ${provider}:`, error);
        }
      }
      
      console.log(`Initialized adapters: ${initializedAdapters.join(', ')}`);
      this.isInitialized = initializedAdapters.length > 0;
      return this.isInitialized;
    } catch (error) {
      console.error('Error initializing LLM service:', error);
      return false;
    }
  }

  /**
   * Get an adapter for a specific provider
   * 
   * @param provider Provider name
   * @returns Adapter instance or null if not available
   */
  getAdapter(provider: string): LLMInterface | null {
    if (!this.isInitialized) {
      throw new Error('LLM service not initialized');
    }
    
    const normalizedProvider = provider.toLowerCase();
    return this.adapters.get(normalizedProvider) || null;
  }

  /**
   * Execute a completion using a specific provider
   * 
   * @param provider Provider to use
   * @param prompt Input text
   * @param params Completion parameters
   * @returns Completion response
   */
  async executeCompletion(
    provider: string,
    prompt: string,
    params?: Partial<CompletionParams>
  ): Promise<CompletionResponse> {
    if (!this.isInitialized) {
      throw new Error('LLM service not initialized');
    }
    
    const adapter = this.getAdapter(provider);
    if (!adapter) {
      throw new Error(`No adapter available for provider: ${provider}`);
    }
    
    // Apply default model if not specified
    const normalizedParams: CompletionParams = {
      temperature: params?.temperature ?? 0.7,
      maxTokens: params?.maxTokens ?? 1000,
      topP: params?.topP ?? 1.0,
      stopSequences: params?.stopSequences,
      presencePenalty: params?.presencePenalty,
      frequencyPenalty: params?.frequencyPenalty,
      model: params?.model || this.defaultModels.get(provider.toLowerCase()) || ''
    };
    
    // Extract user ID from request context (if available)
    const userId = (global as any)?.currentUser?.id;
    
    // Track and execute the LLM completion with performance monitoring
    return LlmPerformanceTracker.trackCompletion(
      provider.toLowerCase(),
      normalizedParams.model,
      'completion',
      userId,
      () => adapter.generateCompletion(prompt, normalizedParams),
      normalizedParams
    );
  }

  /**
   * Execute a streaming completion using a specific provider
   * 
   * @param provider Provider to use
   * @param prompt Input text
   * @param callback Function to call with each chunk
   * @param params Completion parameters
   */
  async executeStreamingCompletion(
    provider: string,
    prompt: string,
    callback: StreamCallback,
    params?: Partial<CompletionParams>
  ): Promise<void> {
    if (!this.isInitialized) {
      throw new Error('LLM service not initialized');
    }
    
    const adapter = this.getAdapter(provider);
    if (!adapter) {
      throw new Error(`No adapter available for provider: ${provider}`);
    }
    
    // Apply default model if not specified
    const normalizedParams: CompletionParams = {
      temperature: params?.temperature ?? 0.7,
      maxTokens: params?.maxTokens ?? 1000,
      topP: params?.topP ?? 1.0,
      stopSequences: params?.stopSequences,
      presencePenalty: params?.presencePenalty,
      frequencyPenalty: params?.frequencyPenalty,
      model: params?.model || this.defaultModels.get(provider.toLowerCase()) || ''
    };
    
    // Extract user ID from request context (if available)
    const userId = (global as any)?.currentUser?.id;
    
    // Track and execute the LLM streaming completion with performance monitoring
    return LlmPerformanceTracker.trackStreamingCompletion(
      provider.toLowerCase(),
      normalizedParams.model,
      'streaming_completion',
      userId,
      (wrappedCallback) => adapter.streamCompletion(prompt, normalizedParams, wrappedCallback),
      callback,
      normalizedParams
    );
  }

  /**
   * Execute completions across multiple providers for comparison
   * 
   * @param prompt Input text
   * @param providers Array of providers to use (defaults to all available)
   * @param params Completion parameters
   * @returns Map of provider to completion response
   */
  async compareCompletions(
    prompt: string,
    providers?: string[],
    params?: Partial<CompletionParams>
  ): Promise<Map<string, CompletionResponse>> {
    if (!this.isInitialized) {
      throw new Error('LLM service not initialized');
    }
    
    const providerList = providers || Array.from(this.adapters.keys());
    const results = new Map<string, CompletionResponse>();
    
    // Execute completions in parallel
    const completionPromises = providerList.map(async provider => {
      try {
        const response = await this.executeCompletion(provider, prompt, params);
        results.set(provider, response);
      } catch (error) {
        console.error(`Error executing completion for ${provider}:`, error);
      }
    });
    
    await Promise.all(completionPromises);
    return results;
  }

  /**
   * Get a list of available providers
   * 
   * @returns Array of provider names
   */
  getAvailableProviders(): string[] {
    return Array.from(this.adapters.keys());
  }

  /**
   * Get a list of available models for a provider
   * 
   * @param provider Provider name
   * @returns Array of model names
   */
  async getAvailableModels(provider: string): Promise<string[]> {
    if (!this.isInitialized) {
      throw new Error('LLM service not initialized');
    }
    
    const adapter = this.getAdapter(provider);
    if (!adapter) {
      throw new Error(`No adapter available for provider: ${provider}`);
    }
    
    return adapter.getAvailableModels();
  }

  /**
   * Get usage statistics for all providers
   * 
   * @returns Map of provider to usage data
   */
  async getUsageStatistics(): Promise<Map<string, UsageData | null>> {
    if (!this.isInitialized) {
      throw new Error('LLM service not initialized');
    }
    
    const usageStats = new Map<string, UsageData | null>();
    
    for (const [provider, adapter] of this.adapters.entries()) {
      try {
        const stats = await adapter.getUsageStatistics();
        usageStats.set(provider, stats);
      } catch (error) {
        console.error(`Error getting usage stats for ${provider}:`, error);
        usageStats.set(provider, null);
      }
    }
    
    return usageStats;
  }

  /**
   * Add a new provider with API key
   * 
   * @param provider Provider name
   * @param apiKey API key
   * @param defaultModel Default model to use
   * @returns True if successful
   */
  async addProvider(provider: string, apiKey: string, defaultModel?: string): Promise<boolean> {
    if (!AdapterFactory.isProviderSupported(provider)) {
      throw new Error(`Provider ${provider} is not supported`);
    }
    
    // Store the API key
    const keyStored = this.keyManager.storeKey(provider, apiKey);
    if (!keyStored) {
      return false;
    }
    
    // Set default model
    if (defaultModel) {
      this.defaultModels.set(provider.toLowerCase(), defaultModel);
    }
    
    // Create adapter config
    const config: AdapterConfig = {
      apiKey,
      defaultModel: defaultModel || this.defaultModels.get(provider.toLowerCase()) || AdapterFactory.getDefaultModel(provider)
    };
    
    try {
      // Create and initialize adapter
      const adapter = AdapterFactory.createAdapter(provider, config);
      
      // Test connection with health check
      const healthy = await adapter.healthCheck();
      if (!healthy) {
        console.error(`Health check failed for ${provider}`);
        return false;
      }
      
      // Add to active adapters
      this.adapters.set(provider.toLowerCase(), adapter);
      
      // Mark as initialized if not already
      if (!this.isInitialized) {
        this.isInitialized = true;
      }
      
      return true;
    } catch (error) {
      console.error(`Error initializing adapter for ${provider}:`, error);
      return false;
    }
  }

  /**
   * Remove a provider
   * 
   * @param provider Provider name
   * @returns True if successful
   */
  removeProvider(provider: string): boolean {
    const normalizedProvider = provider.toLowerCase();
    
    // Remove from adapters
    this.adapters.delete(normalizedProvider);
    
    // Remove API key
    return this.keyManager.removeKey(normalizedProvider);
  }

  /**
   * Rotate API key for a provider
   * 
   * @param provider Provider name
   * @param newApiKey New API key
   * @returns True if successful
   */
  async rotateApiKey(provider: string, newApiKey: string): Promise<boolean> {
    const normalizedProvider = provider.toLowerCase();
    
    // Update the key
    const keyUpdated = this.keyManager.rotateKey(normalizedProvider, newApiKey);
    if (!keyUpdated) {
      return false;
    }
    
    // Re-initialize the adapter
    if (this.adapters.has(normalizedProvider)) {
      // Get current default model
      const defaultModel = this.defaultModels.get(normalizedProvider) || 
                          AdapterFactory.getDefaultModel(normalizedProvider);
      
      // Create new config
      const config: AdapterConfig = {
        apiKey: newApiKey,
        defaultModel
      };
      
      try {
        // Create and test new adapter
        const adapter = AdapterFactory.createAdapter(normalizedProvider, config);
        const healthy = await adapter.healthCheck();
        
        if (!healthy) {
          // Revert to old key if health check fails
          console.error(`Health check failed for new API key for ${provider}`);
          const oldKey = this.keyManager.getKey(normalizedProvider);
          if (oldKey) {
            this.keyManager.storeKey(normalizedProvider, oldKey);
          }
          return false;
        }
        
        // Replace adapter
        this.adapters.set(normalizedProvider, adapter);
        return true;
      } catch (error) {
        console.error(`Error rotating API key for ${provider}:`, error);
        return false;
      }
    }
    
    return true;
  }
}

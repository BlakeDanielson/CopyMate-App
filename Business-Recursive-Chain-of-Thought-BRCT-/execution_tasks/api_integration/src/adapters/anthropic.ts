/**
 * Anthropic adapter implementation
 */

import { BaseAdapter } from './base';
import {
  AdapterConfig,
  CompletionParams,
  CompletionResponse,
  StreamCallback,
  UsageData
} from '../types/adapters';
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { Readable } from 'stream';

/**
 * Adapter for Anthropic API
 */
export class AnthropicAdapter extends BaseAdapter {
  /**
   * Provider name
   */
  readonly provider = 'anthropic';

  /**
   * Axios instance for API calls
   */
  private client: AxiosInstance;

  /**
   * Anthropic API base URL
   */
  private baseUrl: string;

  /**
   * Available models cache
   */
  private availableModelsCache: string[] | null = null;

  /**
   * Constructor for Anthropic adapter
   * 
   * @param config Configuration options
   */
  constructor(config: AdapterConfig) {
    super(config);

    this.baseUrl = config.baseUrl || 'https://api.anthropic.com/v1';
    
    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: this.timeout,
      headers: {
        'x-api-key': this.apiKey,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
      }
    });
  }

  /**
   * Get list of available models from Anthropic
   * 
   * @returns Promise resolving to a list of model IDs
   */
  async getAvailableModels(): Promise<string[]> {
    // Anthropic doesn't have a models endpoint as of their current API
    // Return a hardcoded list of known models
    if (this.availableModelsCache !== null) {
      return this.availableModelsCache;
    }

    // In a real implementation, we'd probably check for model availability
    // by making a lightweight request to the API
    try {
      // Simplified check: just ping the API with a minimal request
      await this.client.post('/complete', {
        model: 'claude-instant-1',
        prompt: '\n\nHuman: Hi\n\nAssistant:',
        max_tokens_to_sample: 1
      });

      // If we get here, the API is available
      // Return the list of supported Claude models
      this.availableModelsCache = [
        'claude-instant-1',
        'claude-1',
        'claude-2',
        'claude-2.1',
        'claude-3-opus-20240229',
        'claude-3-sonnet-20240229',
        'claude-3-haiku-20240307'
      ];
      
      return this.availableModelsCache;
    } catch (error) {
      throw this.standardizeError(error);
    }
  }

  /**
   * Generate a completion using Anthropic API
   * 
   * @param prompt Input text
   * @param parameters Completion parameters
   * @returns Promise resolving to completion response
   */
  async generateCompletion(
    prompt: string,
    parameters: CompletionParams
  ): Promise<CompletionResponse> {
    const params = this.normalizeParams(parameters);
    const anthropicParams = this.mapParameters(params);
    const startTime = Date.now();
    let retryCount = 0;

    // Format prompt for Anthropic's conversation format
    const formattedPrompt = this.formatPrompt(prompt);

    while (true) {
      try {
        const response = await this.client.post('/complete', {
          ...anthropicParams,
          prompt: formattedPrompt
        });

        const result: CompletionResponse = {
          text: response.data.completion || '',
          usage: {
            // Anthropic doesn't provide token counts directly in their basic API
            // We'll estimate them
            promptTokens: this.estimateTokenCount(formattedPrompt),
            completionTokens: this.estimateTokenCount(response.data.completion),
            totalTokens: this.estimateTokenCount(formattedPrompt) + 
                         this.estimateTokenCount(response.data.completion)
          },
          provider: this.provider,
          model: params.model,
          metrics: this.calculateMetrics(
            startTime,
            null, // No first token time for non-streaming
            this.estimateTokenCount(response.data.completion)
          )
        };

        // Log usage for tracking
        this.logUsage({
          provider: this.provider,
          model: params.model,
          promptTokens: result.usage.promptTokens,
          completionTokens: result.usage.completionTokens,
          totalTokens: result.usage.totalTokens,
          timestamp: new Date()
        });

        return result;
      } catch (error: any) {
        if (this.isRetryableError(error) && retryCount < this.maxRetries) {
          await this.handleRateLimiting(error, retryCount);
          retryCount++;
        } else {
          throw this.standardizeError(error);
        }
      }
    }
  }

  /**
   * Stream a completion using Anthropic API
   * 
   * @param prompt Input text
   * @param parameters Completion parameters
   * @param callback Function to call with each chunk
   */
  async streamCompletion(
    prompt: string,
    parameters: CompletionParams,
    callback: StreamCallback
  ): Promise<void> {
    const params = this.normalizeParams(parameters);
    const anthropicParams = this.mapParameters(params);
    const startTime = Date.now();
    let firstTokenTime: number | null = null;
    let retryCount = 0;
    let completionTokens = 0;
    let fullText = '';

    // Format prompt for Anthropic's conversation format
    const formattedPrompt = this.formatPrompt(prompt);

    while (true) {
      try {
        // Configure request for streaming
        const config: AxiosRequestConfig = {
          responseType: 'stream',
          headers: {
            'content-type': 'application/json',
            'x-api-key': this.apiKey,
            'anthropic-version': '2023-06-01'
          }
        };

        const response = await this.client.post('/complete', {
          ...anthropicParams,
          prompt: formattedPrompt,
          stream: true
        }, config);

        const stream = response.data as Readable;
        
        // Process the streaming response
        return new Promise((resolve, reject) => {
          let buffer = '';
          
          stream.on('data', (chunk: Buffer) => {
            try {
              // Anthropic sends data events with one or more SSE messages
              buffer += chunk.toString('utf8');
              
              // Process any complete SSE messages
              while (buffer.includes('\n\n')) {
                const splitPoint = buffer.indexOf('\n\n');
                const message = buffer.substring(0, splitPoint);
                buffer = buffer.substring(splitPoint + 2);
                
                // Skip non-data messages
                if (!message.startsWith('data: ')) continue;
                
                // Parse the JSON data
                const data = JSON.parse(message.substring(6));
                
                if (data.completion) {
                  if (firstTokenTime === null) {
                    firstTokenTime = Date.now();
                  }
                  
                  // We just get the delta (new content) in each message
                  const newContent = data.completion;
                  fullText += newContent;
                  completionTokens += this.estimateTokenCountInChunk(newContent);
                  callback(newContent, false);
                }
                
                // Check for stop condition
                if (data.stop_reason) {
                  // End of stream
                  callback('', true);
                  
                  // Log usage
                  const usage: UsageData = {
                    provider: this.provider,
                    model: params.model,
                    promptTokens: this.estimateTokenCount(formattedPrompt),
                    completionTokens,
                    totalTokens: this.estimateTokenCount(formattedPrompt) + completionTokens,
                    timestamp: new Date()
                  };
                  
                  this.logUsage(usage);
                  resolve();
                }
              }
            } catch (error) {
              console.error('Error parsing stream chunk', error);
            }
          });
          
          stream.on('error', (error: Error) => {
            callback('', true, this.standardizeError(error));
            reject(this.standardizeError(error));
          });
          
          stream.on('end', () => {
            // If we get here without seeing a stop_reason, we need to finalize
            if (fullText.length > 0) {
              // Log usage
              const usage: UsageData = {
                provider: this.provider,
                model: params.model,
                promptTokens: this.estimateTokenCount(formattedPrompt),
                completionTokens,
                totalTokens: this.estimateTokenCount(formattedPrompt) + completionTokens,
                timestamp: new Date()
              };
              
              this.logUsage(usage);
              
              // Signal completion
              callback('', true);
              resolve();
            }
          });
        });
        
      } catch (error: any) {
        if (this.isRetryableError(error) && retryCount < this.maxRetries) {
          await this.handleRateLimiting(error, retryCount);
          retryCount++;
        } else {
          callback('', true, this.standardizeError(error));
          throw this.standardizeError(error);
        }
      }
    }
  }

  /**
   * Estimate the number of tokens in a text
   * 
   * @param text Text to estimate tokens for
   * @param modelId Optional model ID (ignored for Anthropic)
   * @returns Estimated token count
   */
  estimateTokenCount(text: string, modelId?: string): number {
    // This is a simple approximation for Claude models
    // In a production environment, use a proper tokenizer library
    // such as the Claude tokenizer for accurate token counting
    
    // Words-to-tokens approximation (avg 4 chars per token)
    return Math.ceil(text.length / 4);
  }

  /**
   * Estimate tokens in a small chunk of text
   * Used during streaming to track token usage
   * 
   * @param chunk Small text chunk
   * @returns Estimated token count
   */
  private estimateTokenCountInChunk(chunk: string): number {
    // For small chunks, simpler approximation
    return Math.max(1, Math.ceil(chunk.length / 4));
  }

  /**
   * Format a prompt for Anthropic's conversation format
   * 
   * @param prompt Raw prompt text
   * @returns Formatted prompt for Anthropic
   */
  private formatPrompt(prompt: string): string {
    // If the prompt already contains \n\nHuman: and \n\nAssistant:, assume it's already formatted
    if (prompt.includes('\n\nHuman:') && prompt.includes('\n\nAssistant:')) {
      // Make sure it ends with Assistant:
      if (!prompt.endsWith('\n\nAssistant:')) {
        return prompt + '\n\nAssistant:';
      }
      return prompt;
    }
    
    // Otherwise, format as a simple Human/Assistant conversation
    return `\n\nHuman: ${prompt}\n\nAssistant:`;
  }

  /**
   * Map unified parameters to Anthropic-specific parameters
   * 
   * @param params Unified parameters
   * @returns Anthropic-specific parameters
   */
  private mapParameters(params: CompletionParams): any {
    return {
      model: params.model,
      temperature: params.temperature,
      max_tokens_to_sample: params.maxTokens,
      top_p: params.topP,
      stop_sequences: params.stopSequences && params.stopSequences.length > 0 
        ? params.stopSequences 
        : undefined
      // Anthropic doesn't have presence_penalty or frequency_penalty
    };
  }
}

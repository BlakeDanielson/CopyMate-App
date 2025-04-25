/**
 * Google Gemini (Generative AI) adapter implementation
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

/**
 * Adapter for Google's Gemini (Generative AI) API
 */
export class GeminiAdapter extends BaseAdapter {
  /**
   * Provider name
   */
  readonly provider = 'gemini';

  /**
   * Axios instance for API calls
   */
  private client: AxiosInstance;

  /**
   * Gemini API base URL
   */
  private baseUrl: string;

  /**
   * Available models cache
   */
  private availableModelsCache: string[] | null = null;

  /**
   * Constructor for Gemini adapter
   * 
   * @param config Configuration options
   */
  constructor(config: AdapterConfig) {
    super(config);

    this.baseUrl = config.baseUrl || 'https://generativelanguage.googleapis.com/v1beta';
    
    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: this.timeout
      // No default headers - apiKey goes in query params
    });
  }

  /**
   * Get list of available models from Gemini
   * 
   * @returns Promise resolving to a list of model IDs
   */
  async getAvailableModels(): Promise<string[]> {
    if (this.availableModelsCache !== null) {
      return this.availableModelsCache;
    }

    try {
      const response = await this.client.get(`/models?key=${this.apiKey}`);
      
      // Filter for only Gemini models
      const models = response.data.models
        .filter((model: any) => model.name.includes('gemini'))
        .map((model: any) => model.name.split('/').pop());
      
      this.availableModelsCache = models;
      return models;
    } catch (error) {
      throw this.standardizeError(error);
    }
  }

  /**
   * Generate a completion using Gemini API
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
    const geminiParams = this.mapParameters(params);
    const startTime = Date.now();
    let retryCount = 0;
    
    // Extract model name for API URL 
    const modelName = this.getModelName(params.model);

    while (true) {
      try {
        const response = await this.client.post(
          `/models/${modelName}:generateContent?key=${this.apiKey}`,
          {
            contents: [
              {
                role: 'user',
                parts: [{ text: prompt }]
              }
            ],
            generationConfig: geminiParams
          }
        );

        // Extract text from response
        const content = response.data.candidates[0]?.content;
        const text = content.parts[0]?.text || '';
        
        // Extract usage stats if available
        const usageMetadata = response.data.usageMetadata || {};
        
        const result: CompletionResponse = {
          text,
          usage: {
            promptTokens: usageMetadata.promptTokenCount || this.estimateTokenCount(prompt),
            completionTokens: usageMetadata.candidatesTokenCount || this.estimateTokenCount(text),
            totalTokens: usageMetadata.totalTokenCount || 
                         (this.estimateTokenCount(prompt) + this.estimateTokenCount(text))
          },
          provider: this.provider,
          model: params.model,
          metrics: this.calculateMetrics(
            startTime,
            null, // No first token time for non-streaming
            usageMetadata.candidatesTokenCount || this.estimateTokenCount(text)
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
   * Stream a completion using Gemini API
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
    const geminiParams = this.mapParameters(params);
    const startTime = Date.now();
    let firstTokenTime: number | null = null;
    let retryCount = 0;
    let completionTokens = 0;
    let fullText = '';
    
    // Extract model name for API URL 
    const modelName = this.getModelName(params.model);

    while (true) {
      try {
        // Configure request payload for streaming
        const payload = {
          contents: [
            {
              role: 'user',
              parts: [{ text: prompt }]
            }
          ],
          generationConfig: geminiParams
        };

        // Google's API uses Server-Sent Events for streaming
        // We'll manually set up a stream parser
        const response = await this.client.post(
          `/models/${modelName}:streamGenerateContent?key=${this.apiKey}`,
          payload, 
          { responseType: 'stream' }
        );

        const stream = response.data;
        
        // Process the streaming response
        return new Promise((resolve, reject) => {
          let buffer = '';
          
          stream.on('data', (chunk: Buffer) => {
            try {
              const content = chunk.toString('utf8');
              buffer += content;
              
              // SSE messages are separated by double newlines
              const lines = buffer.split('\n\n');
              buffer = lines.pop() || ''; // Last line might be incomplete
              
              for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                
                // Parse JSON data
                const jsonData = line.substring(6);
                if (jsonData === '[DONE]') {
                  // End of stream marker
                  continue;
                }
                
                const data = JSON.parse(jsonData);
                
                // Check if we have content
                const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
                if (text) {
                  if (firstTokenTime === null) {
                    firstTokenTime = Date.now();
                  }
                  
                  fullText += text;
                  completionTokens += this.estimateTokenCountInChunk(text);
                  callback(text, false);
                }
                
                // Check for stop condition
                if (data.candidates?.[0]?.finishReason) {
                  // Stream is done
                  callback('', true);
                  
                  // Log usage
                  const usage: UsageData = {
                    provider: this.provider,
                    model: params.model,
                    promptTokens: this.estimateTokenCount(prompt),
                    completionTokens,
                    totalTokens: this.estimateTokenCount(prompt) + completionTokens,
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
            // If we get here without seeing a finishReason, we need to finalize
            if (fullText.length > 0) {
              // Log usage
              const usage: UsageData = {
                provider: this.provider,
                model: params.model,
                promptTokens: this.estimateTokenCount(prompt),
                completionTokens,
                totalTokens: this.estimateTokenCount(prompt) + completionTokens,
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
   * @param modelId Optional model ID (ignored for Gemini)
   * @returns Estimated token count
   */
  estimateTokenCount(text: string, modelId?: string): number {
    // This is a simple approximation for Gemini models
    // In a production environment, use a proper tokenizer
    
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
   * Map unified parameters to Gemini-specific parameters
   * 
   * @param params Unified parameters
   * @returns Gemini-specific parameters
   */
  private mapParameters(params: CompletionParams): any {
    return {
      temperature: params.temperature,
      maxOutputTokens: params.maxTokens,
      topP: params.topP,
      stopSequences: params.stopSequences && params.stopSequences.length > 0 
        ? params.stopSequences 
        : undefined
      // Gemini doesn't have presence_penalty or frequency_penalty
    };
  }

  /**
   * Get clean model name for API calls 
   * 
   * @param model Model identifier
   * @returns Clean model name for API
   */
  private getModelName(model: string): string {
    // Handle full model names (e.g., "models/gemini-pro")
    if (model.includes('/')) {
      return model;
    }
    
    // Handle short names (e.g., "gemini-pro")
    if (model.startsWith('gemini-')) {
      return model;
    }
    
    // Default to gemini-pro if unknown
    return 'gemini-pro';
  }
}

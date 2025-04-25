/**
 * OpenAI adapter implementation
 */

import { Configuration, OpenAIApi } from 'openai';
import { BaseAdapter } from './base';
import {
  AdapterConfig,
  CompletionParams,
  CompletionResponse,
  StreamCallback,
  UsageData
} from '../types/adapters';
import { IncomingMessage } from 'http';

/**
 * Adapter for OpenAI API
 */
export class OpenAIAdapter extends BaseAdapter {
  /**
   * Provider name
   */
  readonly provider = 'openai';

  /**
   * OpenAI API client
   */
  private client: OpenAIApi;

  /**
   * Constructor for OpenAI adapter
   * 
   * @param config Configuration options
   */
  constructor(config: AdapterConfig) {
    super(config);

    const configuration = new Configuration({
      apiKey: this.apiKey,
      organization: config.organization
    });

    this.client = new OpenAIApi(configuration);
  }

  /**
   * Get list of available models from OpenAI
   * 
   * @returns Promise resolving to a list of model IDs
   */
  async getAvailableModels(): Promise<string[]> {
    try {
      const response = await this.client.listModels();
      return response.data.data
        .map(model => model.id)
        .filter(id => id.startsWith('gpt-')); // Only return GPT models
    } catch (error) {
      throw this.standardizeError(error);
    }
  }

  /**
   * Generate a completion using OpenAI API
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
    const openaiParams = this.mapParameters(params);
    const startTime = Date.now();
    let retryCount = 0;

    while (true) {
      try {
        const response = await this.client.createChatCompletion({
          model: openaiParams.model,
          messages: [{ role: 'user', content: prompt }],
          temperature: openaiParams.temperature,
          max_tokens: openaiParams.max_tokens,
          top_p: openaiParams.top_p,
          presence_penalty: openaiParams.presence_penalty,
          frequency_penalty: openaiParams.frequency_penalty,
          stop: openaiParams.stop,
        });

        const result: CompletionResponse = {
          text: response.data.choices[0]?.message?.content || '',
          usage: {
            promptTokens: response.data.usage?.prompt_tokens || 0,
            completionTokens: response.data.usage?.completion_tokens || 0,
            totalTokens: response.data.usage?.total_tokens || 0
          },
          provider: this.provider,
          model: params.model,
          metrics: this.calculateMetrics(
            startTime,
            null, // No first token time for non-streaming
            response.data.usage?.completion_tokens || 0
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
   * Stream a completion using OpenAI API
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
    const openaiParams = this.mapParameters(params);
    const startTime = Date.now();
    let firstTokenTime: number | null = null;
    let retryCount = 0;
    let completionTokens = 0;
    let fullText = '';

    while (true) {
      try {
        console.log('Attempting OpenAI stream API call with params:', openaiParams);
        const response = await this.client.createChatCompletion({
          model: openaiParams.model,
          messages: [{ role: 'user', content: prompt }],
          temperature: openaiParams.temperature,
          max_tokens: openaiParams.max_tokens,
          top_p: openaiParams.top_p,
          presence_penalty: openaiParams.presence_penalty,
          frequency_penalty: openaiParams.frequency_penalty,
          stop: openaiParams.stop,
          stream: true
        }, { responseType: 'stream' });

        // The OpenAI SDK doesn't properly type the streaming response
        // We need to cast it to the correct type (IncomingMessage)
        const stream = response.data as unknown as IncomingMessage;
        console.log('OpenAI stream API call successful, stream received.');
        
        stream.on('data', (chunk: Buffer) => {
          try {
            const lines = chunk
              .toString('utf8')
              .split('\n')
              .filter(line => line.trim() !== '' && line.trim() !== 'data: [DONE]');

            for (const line of lines) {
              if (!line.startsWith('data: ')) continue;
              
              if (firstTokenTime === null) {
                firstTokenTime = Date.now();
              }

              const data = JSON.parse(line.substring(6));
              const content = data.choices[0]?.delta?.content || '';
              if (content) {
                fullText += content;
                completionTokens += this.estimateTokenCountInChunk(content);
                callback(content, false);
              }
            }
          } catch (error) {
            console.error('Error parsing stream chunk', error);
          }
        });

        // Handle stream end
        return new Promise((resolve, reject) => {
          stream.on('end', () => {
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
            
            // Calculate metrics for final callback
            const metrics = this.calculateMetrics(
              startTime,
              firstTokenTime,
              completionTokens
            );
            
            // Signal completion with metrics
            callback('', true);
            resolve();
          });

          stream.on('error', (error: Error) => {
            console.error('Error received from OpenAI stream:', error);
            callback('', true, this.standardizeError(error));
            reject(this.standardizeError(error));
          });
        });
        
      } catch (error: any) {
        console.error('Error during OpenAI stream API call attempt:', error);
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
   * @param modelId Optional model ID (ignored for OpenAI)
   * @returns Estimated token count
   */
  estimateTokenCount(text: string, modelId?: string): number {
    // This is a simple approximation for GPT models
    // In a production environment, use a proper tokenizer library
    // such as tiktoken for accurate token counting
    
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
   * Map unified parameters to OpenAI-specific parameters
   * 
   * @param params Unified parameters
   * @returns OpenAI-specific parameters
   */
  private mapParameters(params: CompletionParams): any {
    return {
      model: params.model,
      temperature: params.temperature,
      max_tokens: params.maxTokens,
      top_p: params.topP,
      presence_penalty: params.presencePenalty,
      frequency_penalty: params.frequencyPenalty,
      stop: params.stopSequences && params.stopSequences.length > 0 
        ? params.stopSequences 
        : undefined
    };
  }
}

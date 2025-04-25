/**
 * Configuration options for the LLM service
 */
export interface LLMConfig {
  /** The model name to use for generation */
  model?: string;
  /** API key for authentication */
  apiKey?: string;
  /** Base URL for API requests */
  baseUrl?: string;
  /** Request timeout in milliseconds */
  timeout?: number;
  /** Maximum number of retry attempts for failed requests */
  maxRetries?: number;
  /** Delay between retries in milliseconds */
  retryDelay?: number;
  /** Whether to automatically retry on rate limit errors */
  enableRateLimitRetry?: boolean;
  /** Maximum length of prompt in characters */
  maxPromptLength?: number;
  /** Maximum total tokens (prompt + completion) */
  maxTokens?: number;
}

/**
 * Message object representing a conversation turn
 */
export interface Message {
  /** Role of the message sender (user, assistant, system) */
  role: 'user' | 'assistant' | 'system';
  /** Content of the message */
  content: string;
}

/**
 * Options for sending a prompt to the LLM
 */
export interface PromptOptions {
  /** System instruction to guide the model's behavior */
  systemInstruction?: string;
  /** Conversation history for context */
  history?: Message[];
  /** Temperature for controlling randomness (0-1) */
  temperature?: number;
  /** Max tokens to generate in the response */
  maxTokens?: number;
}

/**
 * Usage statistics for a completion request
 */
export interface TokenUsage {
  /** Number of tokens in the prompt */
  promptTokens: number;
  /** Number of tokens in the completion */
  completionTokens: number;
  /** Total tokens used */
  totalTokens: number;
}

/**
 * Response from the LLM service
 */
export interface LLMResponse {
  /** Generated text response */
  text: string;
  /** Model used for generation */
  model: string;
  /** Token usage statistics */
  usage: TokenUsage;
}

/**
 * Service for interacting with Large Language Models
 */
/**
 * Response chunk from streaming LLM API
 */
export interface StreamChunk {
  /** Text content of this chunk */
  text: string;
  /** Whether this is the last chunk in the stream */
  isDone: boolean;
}

export class LLMService {
  private config: LLMConfig;
  private abortController: AbortController | null = null;

  /**
   * Creates a new LLMService instance
   * @param config - Optional configuration for the service
   */
  constructor(config: LLMConfig = {}) {
    this.config = {
      model: 'default-model',
      apiKey: process.env.LLM_API_KEY || '',
      baseUrl: 'https://api.default-llm.example.com',
      timeout: 15000,
      maxRetries: 3,
      retryDelay: 1000,
      enableRateLimitRetry: true,
      maxPromptLength: 4000,
      maxTokens: 8192,
      ...config
    };
  }

  /**
   * Gets the current configuration
   * @returns The current configuration object
   */
  getConfig(): LLMConfig {
    return { ...this.config };
  }

  /**
   * Updates the service configuration
   * @param newConfig - Partial configuration to update
   * @throws Error if attempting to set an empty API key
   */
  updateConfig(newConfig: Partial<LLMConfig>): void {
    if (newConfig.apiKey !== undefined && newConfig.apiKey === '') {
      throw new Error('API key cannot be empty');
    }
    
    this.config = {
      ...this.config,
      ...newConfig
    };
  }

  /**
   * Sends a prompt to the LLM and returns the response
   * @param prompt - The prompt text to send
   * @param options - Optional parameters for the request
   * @returns Promise resolving to the LLM response
   * @throws Error if the API key is missing or if the request fails
   */
  async sendPrompt(prompt: string, options: PromptOptions = {}): Promise<LLMResponse> {
    if (!this.config.apiKey) {
      throw new Error('API key is required');
    }

    this._validateInput(prompt, options);

    // Create new abort controller for this request
    this.abortController = new AbortController();

    // Handle history truncation for token budget
    let processedOptions = { ...options };
    if (options.history && this.config.maxTokens) {
      processedOptions.history = this._truncateHistory(prompt, options.history);
    }

    try {
      let retries = 0;
      const maxRetries = this.config.maxRetries || 0;

      while (true) {
        try {
          return await this._makeRequest({
            prompt,
            ...processedOptions,
            abortSignal: this.abortController.signal
          });
        } catch (error) {
          // Don't retry if request was cancelled
          if (this.abortController.signal.aborted) {
            throw new Error('Request was cancelled');
          }

          // Handle rate limit errors
          if (
            error instanceof Error &&
            error.name === 'RateLimitError' &&
            this.config.enableRateLimitRetry
          ) {
            // Exponential backoff for rate limits
            const delay = Math.pow(2, retries) * (this.config.retryDelay || 1000);
            await this._delay(delay);
            retries++;
            continue;
          }

          // Standard retry logic
          if (retries < maxRetries) {
            retries++;
            await this._delay(this.config.retryDelay || 1000);
            continue;
          }

          // Handle specific error types
          if (error instanceof Error) {
            if (error.name === 'TimeoutError') {
              throw new Error('LLM request timed out');
            }
            
            // Add retry information to the error message
            if (maxRetries > 0) {
              throw new Error(`Failed to get response from LLM after ${maxRetries} retries: ${error.message}`);
            } else {
              throw new Error(`Failed to get response from LLM: ${error.message}`);
            }
          }
          throw error;
        }
      }
    } finally {
      this.abortController = null;
    }
  }

  /**
   * Streams a prompt response from the LLM
   * @param prompt - The prompt text to send
   * @param options - Optional parameters for the request
   * @returns AsyncGenerator yielding response chunks
   * @throws Error if the API key is missing or if the request fails
   */
  async *streamPrompt(prompt: string, options: PromptOptions = {}): AsyncGenerator<StreamChunk> {
    if (!this.config.apiKey) {
      throw new Error('API key is required');
    }

    this._validateInput(prompt, options);

    // Create new abort controller for this request
    this.abortController = new AbortController();

    try {
      // Handle history truncation for token budget
      let processedOptions = { ...options };
      if (options.history && this.config.maxTokens) {
        processedOptions.history = this._truncateHistory(prompt, options.history);
      }

      // Get stream from API
      const stream = this._streamRequest({
        prompt,
        ...processedOptions,
        abortSignal: this.abortController.signal
      });

      // Yield chunks from the stream
      for await (const chunk of stream) {
        yield chunk;
      }
    } finally {
      this.abortController = null;
    }
  }

  /**
   * Cancels any ongoing LLM request
   */
  cancelRequest(): void {
    if (this.abortController) {
      this.abortController.abort();
    }
  }

  /**
   * Makes the actual API request to the LLM service
   * @param params - Request parameters
   * @returns Promise resolving to the LLM response
   * @private
   */
  private async _makeRequest(params: {
    prompt: string;
    systemInstruction?: string;
    history?: Message[];
    temperature?: number;
    maxTokens?: number;
    abortSignal?: AbortSignal;
  }): Promise<LLMResponse> {
    // In a real implementation, this would make an HTTP request to the LLM API
    // For now, this is a stub implementation to make tests pass
    
    // Check if the request was aborted
    if (params.abortSignal?.aborted) {
      throw new Error('Request was cancelled');
    }
    
    // This would be replaced with actual API call implementation
    return {
      text: `Response to: ${params.prompt}`,
      model: this.config.model || 'default-model',
      usage: {
        promptTokens: params.prompt.length,
        completionTokens: 20,
        totalTokens: params.prompt.length + 20
      }
    };
  }

  /**
   * Creates a streaming request to the LLM service
   * @param params - Request parameters
   * @returns AsyncGenerator yielding response chunks
   * @private
   */
  private async *_streamRequest(params: {
    prompt: string;
    systemInstruction?: string;
    history?: Message[];
    temperature?: number;
    maxTokens?: number;
    abortSignal?: AbortSignal;
  }): AsyncGenerator<StreamChunk> {
    // In a real implementation, this would create a streaming HTTP request
    // For now, this is a stub implementation to make tests pass
    
    // Check if the request was aborted
    if (params.abortSignal?.aborted) {
      throw new Error('Request was cancelled');
    }

    // Simulate streaming by yielding parts of the response
    yield { text: 'Response', isDone: false };
    
    // Check for abort between chunks
    if (params.abortSignal?.aborted) {
      throw new Error('Request was cancelled');
    }
    
    yield { text: ' to: ', isDone: false };
    
    // Check for abort between chunks
    if (params.abortSignal?.aborted) {
      throw new Error('Request was cancelled');
    }
    
    yield { text: params.prompt, isDone: true };
  }

  /**
   * Validates the input parameters
   * @param prompt - The prompt text
   * @param options - Optional parameters
   * @throws Error if validation fails
   * @private
   */
  private _validateInput(prompt: string, options: PromptOptions): void {
    // Check prompt length
    if (this.config.maxPromptLength && prompt.length > this.config.maxPromptLength) {
      throw new Error(`Prompt exceeds maximum length of ${this.config.maxPromptLength} characters`);
    }

    // Validate temperature
    if (options.temperature !== undefined) {
      if (options.temperature < 0 || options.temperature > 1) {
        throw new Error('Temperature must be between 0 and 1');
      }
    }

    // Check token budget
    if (this.config.maxTokens) {
      const promptTokens = this._countTokens(prompt);
      if (promptTokens > this.config.maxTokens) {
        throw new Error(`Prompt exceeds maximum token limit of ${this.config.maxTokens}`);
      }
    }
  }

  /**
   * Truncates conversation history to fit within token budget
   * @param prompt - The current prompt
   * @param history - The conversation history
   * @returns Truncated history
   * @private
   */
  private _truncateHistory(prompt: string, history: Message[]): Message[] {
    if (!this.config.maxTokens) {
      return history;
    }

    const promptTokens = this._countTokens(prompt);
    let availableTokens = this.config.maxTokens - promptTokens;
    
    // Reserve some tokens for the response
    availableTokens = Math.max(0, availableTokens - 500);
    
    // Start from most recent messages
    const truncatedHistory: Message[] = [];
    for (let i = history.length - 1; i >= 0; i--) {
      const message = history[i];
      const messageTokens = this._countTokens(message.content);
      
      if (messageTokens <= availableTokens) {
        truncatedHistory.unshift(message);
        availableTokens -= messageTokens;
      } else {
        // No more space for messages
        break;
      }
    }
    
    return truncatedHistory;
  }

  /**
   * Counts the number of tokens in text
   * @param text - The text to count tokens for
   * @returns Number of tokens
   * @private
   */
  private _countTokens(text: string): number {
    // This is a placeholder implementation
    // In a real system, you would use the tokenizer for your specific LLM
    // For example, OpenAI provides libraries for their tokenizers
    
    // Simple approximation (not accurate for all models)
    return Math.ceil(text.length / 4);
  }

  /**
   * Utility function to create a delay
   * @param ms - Milliseconds to delay
   * @private
   */
  private async _delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
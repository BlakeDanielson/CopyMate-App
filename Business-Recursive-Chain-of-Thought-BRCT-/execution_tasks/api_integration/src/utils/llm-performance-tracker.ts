import { prisma } from '../lib/prisma';
import { LlmPerformanceLogEntry } from '../types/analytics';
import { CompletionParams, StreamCallback } from '../types/adapters';

/**
 * Utility to track and record LLM performance metrics
 */
export class LlmPerformanceTracker {
  /**
   * Track and log performance metrics for a completion request
   * 
   * @param provider LLM provider name
   * @param model LLM model name
   * @param operation Type of operation (e.g., 'completion', 'chat')
   * @param userId Optional user ID
   * @param originalFn Original function to execute
   * @param params Additional parameters to log
   * @returns The result of the original function
   */
  static async trackCompletion<T>(
    provider: string,
    model: string,
    operation: string,
    userId: string | undefined,
    originalFn: () => Promise<T>,
    params?: Partial<CompletionParams>
  ): Promise<T> {
    // Record start time
    const startTime = process.hrtime();
    
    // Performance log entry
    const perfEntry: LlmPerformanceLogEntry = {
      provider,
      model,
      operation,
      userId,
      totalDuration: 0,
      success: false,
      metadata: {
        temperature: params?.temperature,
        maxTokens: params?.maxTokens,
        topP: params?.topP,
        // Clean stopSequences to avoid storing large arrays
        stopSequencesCount: params?.stopSequences?.length || 0,
        presencePenalty: params?.presencePenalty,
        frequencyPenalty: params?.frequencyPenalty
      }
    };
    
    try {
      // Execute the original function
      const result = await originalFn();
      
      // Calculate duration
      const hrDuration = process.hrtime(startTime);
      const durationMs = Math.round(hrDuration[0] * 1000 + hrDuration[1] / 1000000);
      
      // Update performance entry
      perfEntry.totalDuration = durationMs;
      perfEntry.success = true;
      
      // Store performance metrics asynchronously
      this.storePerformanceMetrics(perfEntry).catch(err => {
        console.error('Failed to store LLM performance metrics:', err);
      });
      
      return result;
    } catch (error) {
      // Calculate duration even for errors
      const hrDuration = process.hrtime(startTime);
      const durationMs = Math.round(hrDuration[0] * 1000 + hrDuration[1] / 1000000);
      
      // Update performance entry with error information
      perfEntry.totalDuration = durationMs;
      perfEntry.success = false;
      perfEntry.errorCode = error instanceof Error ? error.name : 'Unknown';
      perfEntry.errorMessage = error instanceof Error ? error.message : String(error);
      
      // Store performance metrics asynchronously
      this.storePerformanceMetrics(perfEntry).catch(err => {
        console.error('Failed to store LLM performance metrics:', err);
      });
      
      // Re-throw the error
      throw error;
    }
  }

  /**
   * Track and log performance metrics for a streaming completion request
   * 
   * @param provider LLM provider name
   * @param model LLM model name
   * @param operation Type of operation (e.g., 'streaming_completion', 'chat_streaming')
   * @param userId Optional user ID
   * @param originalFn Original function to execute
   * @param params Additional parameters to log
   * @returns The result of the original function
   */
  static async trackStreamingCompletion(
    provider: string,
    model: string,
    operation: string,
    userId: string | undefined,
    originalFn: (wrappedCallback: StreamCallback) => Promise<void>,
    callback: StreamCallback,
    params?: Partial<CompletionParams>
  ): Promise<void> {
    // Record start time
    const startTime = process.hrtime();
    let firstTokenReceived = false;
    let timeToFirstToken: number | undefined;
    
    // Performance log entry
    const perfEntry: LlmPerformanceLogEntry = {
      provider,
      model,
      operation,
      userId,
      totalDuration: 0,
      success: false,
      metadata: {
        temperature: params?.temperature,
        maxTokens: params?.maxTokens,
        topP: params?.topP,
        // Clean stopSequences to avoid storing large arrays
        stopSequencesCount: params?.stopSequences?.length || 0,
        presencePenalty: params?.presencePenalty,
        frequencyPenalty: params?.frequencyPenalty,
        streaming: true
      }
    };
    
    // Wrap the callback to measure time to first token
    const wrappedCallback: StreamCallback = (chunk, done) => {
      // Measure time to first token if this is the first chunk
      if (!firstTokenReceived && chunk) {
        firstTokenReceived = true;
        const hrFirstToken = process.hrtime(startTime);
        timeToFirstToken = Math.round(hrFirstToken[0] * 1000 + hrFirstToken[1] / 1000000);
      }
      
      // Forward to the original callback
      callback(chunk, done);
    };
    
    try {
      // Execute the original function with our wrapped callback
      await originalFn(wrappedCallback);
      
      // Calculate total duration
      const hrDuration = process.hrtime(startTime);
      const durationMs = Math.round(hrDuration[0] * 1000 + hrDuration[1] / 1000000);
      
      // Update performance entry
      perfEntry.totalDuration = durationMs;
      perfEntry.timeToFirstToken = timeToFirstToken;
      perfEntry.success = true;
      
      // Store performance metrics asynchronously
      this.storePerformanceMetrics(perfEntry).catch(err => {
        console.error('Failed to store LLM performance metrics:', err);
      });
    } catch (error) {
      // Calculate duration even for errors
      const hrDuration = process.hrtime(startTime);
      const durationMs = Math.round(hrDuration[0] * 1000 + hrDuration[1] / 1000000);
      
      // Update performance entry with error information
      perfEntry.totalDuration = durationMs;
      perfEntry.timeToFirstToken = timeToFirstToken;
      perfEntry.success = false;
      perfEntry.errorCode = error instanceof Error ? error.name : 'Unknown';
      perfEntry.errorMessage = error instanceof Error ? error.message : String(error);
      
      // Store performance metrics asynchronously
      this.storePerformanceMetrics(perfEntry).catch(err => {
        console.error('Failed to store LLM performance metrics:', err);
      });
      
      // Re-throw the error
      throw error;
    }
  }

  /**
   * Store LLM performance metrics in the database
   * 
   * @param entry Performance log entry
   */
  private static async storePerformanceMetrics(entry: LlmPerformanceLogEntry): Promise<void> {
    try {
      await prisma.llmPerformanceLog.create({
        data: {
          provider: entry.provider,
          model: entry.model,
          operation: entry.operation,
          timeToFirstToken: entry.timeToFirstToken,
          totalDuration: entry.totalDuration,
          tokenCount: entry.tokenCount,
          success: entry.success,
          errorCode: entry.errorCode,
          errorMessage: entry.errorMessage,
          userId: entry.userId,
          metadata: entry.metadata as any
        }
      });
    } catch (error) {
      console.error('Error storing LLM performance metrics:', error);
      // We intentionally don't rethrow - metrics storage failure shouldn't affect the app
    }
  }
}

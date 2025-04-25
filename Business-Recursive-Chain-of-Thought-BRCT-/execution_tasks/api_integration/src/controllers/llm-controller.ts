/**
 * Controller for LLM API endpoints
 */

import { Request, Response } from 'express';
import { LLMService } from '../services/llm-service';
import { StreamCallback } from '../types/adapters';

/**
 * Controller for handling LLM API requests
 */
export class LLMController {
  /**
   * LLM service instance
   */
  private llmService: LLMService;

  /**
   * Constructor
   * 
   * @param llmService LLM service instance
   */
  constructor(llmService: LLMService) {
    this.llmService = llmService;
  }

  /**
   * Get available providers
   * 
   * @param req Express request
   * @param res Express response
   */
  getProviders = async (req: Request, res: Response): Promise<void> => {
    try {
      const providers = this.llmService.getAvailableProviders();
      
      res.json({
        success: true,
        data: {
          providers
        }
      });
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  };

  /**
   * Get available models for a provider
   * 
   * @param req Express request
   * @param res Express response
   */
  getModels = async (req: Request, res: Response): Promise<void> => {
    try {
      const { provider } = req.params;
      
      if (!provider) {
        res.status(400).json({
          success: false,
          error: 'Provider is required'
        });
        return;
      }
      
      const models = await this.llmService.getAvailableModels(provider);
      
      res.json({
        success: true,
        data: {
          provider,
          models
        }
      });
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  };

  /**
   * Generate a completion
   * 
   * @param req Express request
   * @param res Express response
   */
  generateCompletion = async (req: Request, res: Response): Promise<void> => {
    try {
      const { provider } = req.params;
      const { prompt, model, temperature, maxTokens, topP, stopSequences } = req.body;
      
      if (!provider || !prompt) {
        res.status(400).json({
          success: false,
          error: 'Provider and prompt are required'
        });
        return;
      }
      
      const completion = await this.llmService.executeCompletion(provider, prompt, {
        model,
        temperature,
        maxTokens,
        topP,
        stopSequences
      });
      
      res.json({
        success: true,
        data: completion
      });
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  };

  /**
   * Generate a streaming completion
   * 
   * @param req Express request
   * @param res Express response
   */
  streamCompletion = async (req: Request, res: Response): Promise<void> => {
    try {
      const { provider } = req.params;
      // Read prompt from query parameters for streaming requests
      const { prompt } = req.query as { prompt?: string };
      // Read all parameters from query for GET requests
      const { model, temperature, maxTokens, topP, stopSequences } = req.query as {
        model?: string;
        temperature?: string;
        maxTokens?: string;
        topP?: string;
        stopSequences?: string | string[]; // Allow single string or array
      };

      if (!provider || !prompt) {
        res.status(400).json({
          success: false,
          error: 'Provider and prompt (in query) are required for streaming'
        });
        return;
      }
      
      // Set up SSE response
      res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
      });
      
      // Callback for streaming responses
      const streamCallback: StreamCallback = (chunk, done, error) => {
        if (error) {
          res.write(`data: ${JSON.stringify({ error: error.message })}\n\n`);
          res.end();
          return;
        }
        
        if (done) {
          res.write('data: [DONE]\n\n');
          res.end();
          return;
        }
        
        res.write(`data: ${JSON.stringify({ content: chunk })}\n\n`);
      };
      
      // Execute streaming completion
      await this.llmService.executeStreamingCompletion(
        provider,
        prompt as string, // Assert prompt is string after check
        streamCallback,
        {
          model,
          // Parse numeric and array parameters from query strings
          temperature: temperature ? parseFloat(temperature) : undefined,
          maxTokens: maxTokens ? parseInt(maxTokens, 10) : undefined,
          topP: topP ? parseFloat(topP) : undefined,
          // Handle stopSequences which might be a single string or need splitting
          stopSequences: typeof stopSequences === 'string' ? stopSequences.split(',') : stopSequences
        }
      );
    } catch (error: any) {
      // If headers aren't sent yet, send error response
      if (!res.headersSent) {
        res.status(500).json({
          success: false,
          error: error.message
        });
      } else {
        // Otherwise send error in stream format
        res.write(`data: ${JSON.stringify({ error: error.message })}\n\n`);
        res.end();
      }
    }
  };

  /**
   * Compare completions across providers
   * 
   * @param req Express request
   * @param res Express response
   */
  compareCompletions = async (req: Request, res: Response): Promise<void> => {
    try {
      const { prompt, providers, model, temperature, maxTokens, topP, stopSequences } = req.body;
      
      if (!prompt) {
        res.status(400).json({
          success: false,
          error: 'Prompt is required'
        });
        return;
      }
      
      const results = await this.llmService.compareCompletions(
        prompt,
        providers,
        {
          model,
          temperature,
          maxTokens,
          topP,
          stopSequences
        }
      );
      
      // Convert Map to object for JSON response
      const comparisons: Record<string, any> = {};
      results.forEach((value, key) => {
        comparisons[key] = value;
      });
      
      res.json({
        success: true,
        data: {
          prompt,
          comparisons
        }
      });
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  };

  /**
   * Get usage statistics
   * 
   * @param req Express request
   * @param res Express response
   */
  getUsageStats = async (req: Request, res: Response): Promise<void> => {
    try {
      const usageStats = await this.llmService.getUsageStatistics();
      
      // Convert Map to object for JSON response
      const stats: Record<string, any> = {};
      usageStats.forEach((value, key) => {
        stats[key] = value;
      });
      
      res.json({
        success: true,
        data: {
          stats
        }
      });
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  };
}

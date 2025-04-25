import { TRPCError } from '@trpc/server';
import { z } from 'zod';
import { createTRPCRouter, publicProcedure } from '../trpc';
import { LLMService } from '../../services/LLMService';

// Create a single instance of the LLM service to be used across requests
// Export for testing purposes
export const llmService = new LLMService();

/**
 * Chat router providing procedures for chat functionality
 */
export const chatRouter = createTRPCRouter({
  /**
   * Sends a message to the LLM and returns the response
   */
  sendMessage: publicProcedure
    // Input validation
    .input(z.object({ message: z.string().min(1) }))
    // Output definition
    .output(z.object({ reply: z.string() }))
    // Mutation handler
    .mutation(async ({ input }) => {
      try {
        // Send the prompt to the LLM service
        const llmResponse = await llmService.sendPrompt(input.message);
        
        // Return the text field from the response as the reply
        return { reply: llmResponse.text };
      } catch (error) {
        // Log error and throw TRPCError
        console.error("LLM Service failed", error);
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to communicate with the LLM service.',
        });
      }
    }),
});
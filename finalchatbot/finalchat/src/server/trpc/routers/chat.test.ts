/**
 * @jest-environment node
 */

import { TRPCError } from '@trpc/server';

// Import LLMService and router before mocks to ensure they're initialized
import { LLMService } from '../../services/LLMService';
import { chatRouter, llmService } from './chat';

// Create a spy on the actual service instance's sendPrompt method
jest.spyOn(llmService, 'sendPrompt');

describe('chatRouter', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Reset the mock
    (llmService.sendPrompt as jest.Mock).mockReset();
  });
  
  describe('sendMessage procedure', () => {
    it('should define the sendMessage procedure', () => {
      expect(chatRouter.sendMessage).toBeDefined();
    });
    
    it('should successfully process a message and return a reply', async () => {
      // Setup mock response
      const mockResponse = {
        text: 'This is the LLM response',
        model: 'test-model',
        usage: { promptTokens: 5, completionTokens: 5, totalTokens: 10 }
      };
      
      // Mock the sendPrompt method to return the response
      (llmService.sendPrompt as jest.Mock).mockResolvedValue(mockResponse);
      
      // We can't easily access the internal handler because of tRPC's structure,
      // so we'll test the integration by creating a mock caller
      const mockCaller = async (input: any) => {
        try {
          // Use the actual implementation, but with mocked dependencies
          const procedure = chatRouter.sendMessage;
          const ctx = {};
          
          // We need to call the resolver function directly
          const resolver = (procedure as any)._def.resolver;
          return await resolver({ 
            ctx, 
            input, 
            type: 'mutation' 
          });
        } catch (error) {
          throw error;
        }
      };
      
      // Call our test function
      const result = await mockCaller({ message: 'Hello LLM' });
      
      // Verify the LLM service was called with the correct input
      expect(llmService.sendPrompt).toHaveBeenCalledWith('Hello LLM');
      
      // Verify the correct response was returned
      expect(result).toEqual({ reply: 'This is the LLM response' });
    });
    
    it('should throw a TRPCError when the LLM service fails', async () => {
      // Setup mock error
      (llmService.sendPrompt as jest.Mock).mockRejectedValue(new Error('LLM service error'));
      
      // Create our test caller
      const mockCaller = async (input: any) => {
        // Use the actual implementation, but with mocked dependencies
        const procedure = chatRouter.sendMessage;
        const ctx = {};
        
        // We need to call the resolver function directly
        const resolver = (procedure as any)._def.resolver;
        return await resolver({ 
          ctx, 
          input, 
          type: 'mutation' 
        });
      };
      
      // Verify it throws a TRPCError
      await expect(mockCaller({ message: 'Hello LLM' }))
        .rejects.toThrow(TRPCError);
        
      // Test the specific error details
      try {
        await mockCaller({ message: 'Hello LLM' });
      } catch (error) {
        expect(error).toBeInstanceOf(TRPCError);
        expect((error as TRPCError).code).toBe('INTERNAL_SERVER_ERROR');
        expect((error as TRPCError).message).toContain('Failed to communicate with the LLM service');
      }
    });
  });
});
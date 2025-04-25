/**
 * Conversation controller
 * Handles HTTP requests for conversation operations
 */

import { Request, Response } from 'express';
import conversationService from '../services/conversation.service';
import { CreateConversationInput, UpdateConversationInput, CreateMessageInput, MessageRole } from '../types/conversation';

export class ConversationController {
  /**
   * Create a new conversation
   */
  async createConversation(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.user?.id;

      if (!userId) {
        res.status(401).json({
          success: false,
          error: 'Unauthorized',
          message: 'Authentication required'
        });
        return;
      }

      const data: CreateConversationInput = req.body;
      const conversation = await conversationService.createConversation(userId, data);

      res.status(201).json({
        success: true,
        data: conversation,
        message: 'Conversation created successfully'
      });
    } catch (error: any) {
      console.error('Create conversation error:', error);
      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred creating the conversation'
      });
    }
  }

  /**
   * Get all conversations for a user
   */
  async getUserConversations(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.user?.id;

      if (!userId) {
        res.status(401).json({
          success: false,
          error: 'Unauthorized',
          message: 'Authentication required'
        });
        return;
      }

      const conversations = await conversationService.getUserConversations(userId);

      res.status(200).json({
        success: true,
        data: conversations,
        count: conversations.length,
        message: 'Conversations retrieved successfully'
      });
    } catch (error: any) {
      console.error('Get conversations error:', error);
      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred retrieving conversations'
      });
    }
  }

  /**
   * Get a conversation by ID
   */
  async getConversation(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.user?.id;
      const conversationId = req.params.id;

      if (!userId) {
        res.status(401).json({
          success: false,
          error: 'Unauthorized',
          message: 'Authentication required'
        });
        return;
      }

      if (!conversationId) {
        res.status(400).json({
          success: false,
          error: 'Bad Request',
          message: 'Conversation ID is required'
        });
        return;
      }

      const conversation = await conversationService.getConversationById(conversationId, userId);

      if (!conversation) {
        res.status(404).json({
          success: false,
          error: 'Not Found',
          message: 'Conversation not found'
        });
        return;
      }

      res.status(200).json({
        success: true,
        data: conversation,
        message: 'Conversation retrieved successfully'
      });
    } catch (error: any) {
      console.error('Get conversation error:', error);
      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred retrieving the conversation'
      });
    }
  }

  /**
   * Update a conversation
   */
  async updateConversation(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.user?.id;
      const conversationId = req.params.id;
      const data: UpdateConversationInput = req.body;

      if (!userId) {
        res.status(401).json({
          success: false,
          error: 'Unauthorized',
          message: 'Authentication required'
        });
        return;
      }

      if (!conversationId) {
        res.status(400).json({
          success: false,
          error: 'Bad Request',
          message: 'Conversation ID is required'
        });
        return;
      }

      try {
        const conversation = await conversationService.updateConversation(conversationId, userId, data);
        
        res.status(200).json({
          success: true,
          data: conversation,
          message: 'Conversation updated successfully'
        });
      } catch (error: any) {
        if (error.message && error.message.includes('not found')) {
          res.status(404).json({
            success: false,
            error: 'Not Found',
            message: error.message
          });
          return;
        }
        throw error;
      }
    } catch (error: any) {
      console.error('Update conversation error:', error);
      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred updating the conversation'
      });
    }
  }

  /**
   * Delete a conversation
   */
  async deleteConversation(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.user?.id;
      const conversationId = req.params.id;

      if (!userId) {
        res.status(401).json({
          success: false,
          error: 'Unauthorized',
          message: 'Authentication required'
        });
        return;
      }

      if (!conversationId) {
        res.status(400).json({
          success: false,
          error: 'Bad Request',
          message: 'Conversation ID is required'
        });
        return;
      }

      try {
        await conversationService.deleteConversation(conversationId, userId);
        
        res.status(200).json({
          success: true,
          message: 'Conversation deleted successfully'
        });
      } catch (error: any) {
        if (error.message && error.message.includes('not found')) {
          res.status(404).json({
            success: false,
            error: 'Not Found',
            message: error.message
          });
          return;
        }
        throw error;
      }
    } catch (error: any) {
      console.error('Delete conversation error:', error);
      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred deleting the conversation'
      });
    }
  }

  /**
   * Add a message to a conversation
   */
  async addMessage(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.user?.id;
      const conversationId = req.params.id;
      const { content, role, modelUsed, parameters }: CreateMessageInput = req.body;

      if (!userId) {
        res.status(401).json({
          success: false,
          error: 'Unauthorized',
          message: 'Authentication required'
        });
        return;
      }

      if (!conversationId) {
        res.status(400).json({
          success: false,
          error: 'Bad Request',
          message: 'Conversation ID is required'
        });
        return;
      }

      if (!content) {
        res.status(400).json({
          success: false,
          error: 'Bad Request',
          message: 'Message content is required'
        });
        return;
      }

      const messageRole = role || MessageRole.USER;

      try {
        const message = await conversationService.addMessage(userId, {
          conversationId,
          content,
          role: messageRole,
          modelUsed,
          parameters
        });
        
        res.status(201).json({
          success: true,
          data: message,
          message: 'Message added successfully'
        });
      } catch (error: any) {
        if (error.message && error.message.includes('not found')) {
          res.status(404).json({
            success: false,
            error: 'Not Found',
            message: error.message
          });
          return;
        }
        throw error;
      }
    } catch (error: any) {
      console.error('Add message error:', error);
      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred adding the message'
      });
    }
  }

  /**
   * Get messages for a conversation
   */
  async getMessages(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.user?.id;
      const conversationId = req.params.id;

      if (!userId) {
        res.status(401).json({
          success: false,
          error: 'Unauthorized',
          message: 'Authentication required'
        });
        return;
      }

      if (!conversationId) {
        res.status(400).json({
          success: false,
          error: 'Bad Request',
          message: 'Conversation ID is required'
        });
        return;
      }

      try {
        const messages = await conversationService.getConversationMessages(conversationId, userId);
        
        res.status(200).json({
          success: true,
          data: messages,
          count: messages.length,
          message: 'Messages retrieved successfully'
        });
      } catch (error: any) {
        if (error.message && error.message.includes('not found')) {
          res.status(404).json({
            success: false,
            error: 'Not Found',
            message: error.message
          });
          return;
        }
        throw error;
      }
    } catch (error: any) {
      console.error('Get messages error:', error);
      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred retrieving messages'
      });
    }
  }
}

// Create a singleton instance
export const conversationController = new ConversationController();

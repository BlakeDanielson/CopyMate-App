/**
 * Conversation routes
 */

import { Router } from 'express';
import { conversationController } from '../controllers/conversation.controller';
import { authMiddleware } from '../middleware/auth.middleware';

export const createConversationRoutes = (): Router => {
  const router = Router();

  // All conversation routes require authentication
  router.use(authMiddleware);

  /**
   * @route   POST /api/v1/conversations
   * @desc    Create a new conversation
   * @access  Private (requires authentication)
   */
  router.post('/', (req, res) => conversationController.createConversation(req, res));

  /**
   * @route   GET /api/v1/conversations
   * @desc    Get all conversations for the authenticated user
   * @access  Private (requires authentication)
   */
  router.get('/', (req, res) => conversationController.getUserConversations(req, res));

  /**
   * @route   GET /api/v1/conversations/:id
   * @desc    Get a conversation by ID (including its messages)
   * @access  Private (requires authentication)
   */
  router.get('/:id', (req, res) => conversationController.getConversation(req, res));

  /**
   * @route   PUT /api/v1/conversations/:id
   * @desc    Update a conversation (e.g., change title)
   * @access  Private (requires authentication)
   */
  router.put('/:id', (req, res) => conversationController.updateConversation(req, res));

  /**
   * @route   DELETE /api/v1/conversations/:id
   * @desc    Delete a conversation
   * @access  Private (requires authentication)
   */
  router.delete('/:id', (req, res) => conversationController.deleteConversation(req, res));

  /**
   * @route   POST /api/v1/conversations/:id/messages
   * @desc    Add a message to a conversation
   * @access  Private (requires authentication)
   */
  router.post('/:id/messages', (req, res) => conversationController.addMessage(req, res));

  /**
   * @route   GET /api/v1/conversations/:id/messages
   * @desc    Get all messages for a conversation
   * @access  Private (requires authentication)
   */
  router.get('/:id/messages', (req, res) => conversationController.getMessages(req, res));

  return router;
};

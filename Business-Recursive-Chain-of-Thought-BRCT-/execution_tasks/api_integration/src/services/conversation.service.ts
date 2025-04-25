import { PrismaClient } from '@prisma/client';
import { 
  Conversation, 
  Message, 
  CreateConversationInput, 
  UpdateConversationInput, 
  CreateMessageInput,
  MessageRole,
  ConversationHistoryItem
} from '../types/conversation';
import { prisma } from '../lib/prisma';

/**
 * Service for handling conversation history operations
 */
class ConversationService {
  private prisma: PrismaClient;

  constructor() {
    this.prisma = prisma;
  }

  /**
   * Create a new conversation for a user
   */
  async createConversation(userId: string, data: CreateConversationInput): Promise<Conversation> {
    return this.prisma.conversation.create({
      data: {
        userId,
        title: data.title || null,
      },
    });
  }

  /**
   * Get a conversation by ID
   */
  async getConversationById(conversationId: string, userId: string): Promise<Conversation | null> {
    return this.prisma.conversation.findFirst({
      where: {
        id: conversationId,
        userId,
      },
      include: {
        messages: {
          orderBy: {
            createdAt: 'asc',
          },
        },
      },
    });
  }

  /**
   * Get all conversations for a user
   */
  async getUserConversations(userId: string): Promise<ConversationHistoryItem[]> {
    const conversations = await this.prisma.conversation.findMany({
      where: {
        userId,
      },
      orderBy: {
        updatedAt: 'desc',
      },
      include: {
        messages: {
          orderBy: {
            createdAt: 'desc',
          },
          take: 1,
        },
        _count: {
          select: {
            messages: true,
          },
        },
      },
    });

    // Define type for the conversation result from Prisma
    interface ConversationWithMessagesAndCount {
      id: string;
      title: string | null;
      updatedAt: Date;
      messages: {
        content: string;
        createdAt: Date;
      }[];
      _count: {
        messages: number;
      };
    }

    return conversations.map((conv: ConversationWithMessagesAndCount) => ({
      id: conv.id,
      title: conv.title,
      updatedAt: conv.updatedAt,
      messageCount: conv._count.messages,
      lastMessage: conv.messages.length > 0 ? {
        content: conv.messages[0].content,
        createdAt: conv.messages[0].createdAt,
      } : undefined,
    }));
  }

  /**
   * Update a conversation
   */
  async updateConversation(
    conversationId: string, 
    userId: string, 
    data: UpdateConversationInput
  ): Promise<Conversation> {
    // Check if the conversation belongs to the user
    const conversation = await this.prisma.conversation.findFirst({
      where: {
        id: conversationId,
        userId,
      },
    });

    if (!conversation) {
      throw new Error('Conversation not found or unauthorized');
    }

    return this.prisma.conversation.update({
      where: {
        id: conversationId,
      },
      data,
    });
  }

  /**
   * Delete a conversation
   */
  async deleteConversation(conversationId: string, userId: string): Promise<void> {
    // Check if the conversation belongs to the user
    const conversation = await this.prisma.conversation.findFirst({
      where: {
        id: conversationId,
        userId,
      },
    });

    if (!conversation) {
      throw new Error('Conversation not found or unauthorized');
    }

    await this.prisma.conversation.delete({
      where: {
        id: conversationId,
      },
    });
  }

  /**
   * Add a message to a conversation
   */
  async addMessage(userId: string, data: CreateMessageInput): Promise<Message> {
    // Check if the conversation belongs to the user
    const conversation = await this.prisma.conversation.findFirst({
      where: {
        id: data.conversationId,
        userId,
      },
    });

    if (!conversation) {
      throw new Error('Conversation not found or unauthorized');
    }

    // Update the conversation's updatedAt timestamp
    await this.prisma.conversation.update({
      where: {
        id: data.conversationId,
      },
      data: {
        updatedAt: new Date(),
      },
    });

    // Increment user's message count if it's a user message
    if (data.role === MessageRole.USER) {
      await this.prisma.user.update({
        where: { id: userId },
        data: {
          messageCount: {
            increment: 1
          }
        }
      });
    }

    // Create the message
    return this.prisma.message.create({
      data: {
        conversationId: data.conversationId,
        role: data.role,
        content: data.content,
        modelUsed: data.modelUsed || null,
        parameters: data.parameters ? (data.parameters as any) : null,
      },
    });
  }

  /**
   * Get messages for a conversation
   */
  async getConversationMessages(conversationId: string, userId: string): Promise<Message[]> {
    // Check if the conversation belongs to the user
    const conversation = await this.prisma.conversation.findFirst({
      where: {
        id: conversationId,
        userId,
      },
    });

    if (!conversation) {
      throw new Error('Conversation not found or unauthorized');
    }

    return this.prisma.message.findMany({
      where: {
        conversationId,
      },
      orderBy: {
        createdAt: 'asc',
      },
    });
  }
}

export default new ConversationService();

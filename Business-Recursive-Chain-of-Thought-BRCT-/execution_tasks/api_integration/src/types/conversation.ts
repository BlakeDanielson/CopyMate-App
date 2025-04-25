/**
 * Conversation History types
 */

import { User, UserWithoutPassword } from './auth';

// Message Role Enum matching our Prisma schema
export enum MessageRole {
  USER = 'USER',
  ASSISTANT = 'ASSISTANT'
}

// Conversation type definition based on our Prisma schema
export interface Conversation {
  id: string;
  title: string | null;
  userId: string;
  createdAt: Date;
  updatedAt: Date;
  messages?: Message[];
  user?: User;
}

// Message type definition based on our Prisma schema
export interface Message {
  id: string;
  conversationId: string;
  role: MessageRole;
  content: string;
  modelUsed: string | null;
  parameters: any | null; // Using 'any' for JSON type
  createdAt: Date;
  conversation?: Conversation;
}

// Conversation with user but without sensitive data
export interface ConversationWithUser extends Omit<Conversation, 'user'> {
  user?: UserWithoutPassword;
}

// Input types for creating conversations and messages
export interface CreateConversationInput {
  title?: string;
}

export interface UpdateConversationInput {
  title?: string;
}

export interface CreateMessageInput {
  conversationId: string;
  role: MessageRole;
  content: string;
  modelUsed?: string;
  parameters?: Record<string, any>; // Using Record for JSON
}

// Response types
export interface ConversationResponse {
  conversation: Conversation;
  messages: Message[];
}

export interface ConversationListResponse {
  conversations: ConversationWithUser[];
  total: number;
}

export interface MessageResponse {
  message: Message;
}

// Used for chat history
export interface ConversationHistoryItem {
  id: string;
  title: string | null;
  updatedAt: Date;
  messageCount: number;
  lastMessage?: {
    content: string;
    createdAt: Date;
  };
}

import { apiService } from "./api.service";
import { Conversation, Message } from "../../interfaces/llm";
import { CONVERSATIONS_API_URL } from "../../config/constants";

export class ConversationService {
  /**
   * Get all conversations for the current user
   */
  public async getConversations(page = 1, limit = 10): Promise<Conversation[]> {
    const response = await apiService.get<{
      data: Conversation[];
      success: boolean;
    }>(`${CONVERSATIONS_API_URL}?page=${page}&limit=${limit}`);
    // Extract the data array from the response
    return response.data || [];
  }

  /**
   * Get a specific conversation by ID
   */
  public async getConversation(conversationId: string): Promise<Conversation> {
    const response = await apiService.get<{
      data: Conversation;
      success: boolean;
    }>(`${CONVERSATIONS_API_URL}/${conversationId}`);
    return response.data;
  }

  /**
   * Create a new conversation
   */
  public async createConversation(title: string): Promise<Conversation> {
    const response = await apiService.post<{
      data: Conversation;
      success: boolean;
    }>(`${CONVERSATIONS_API_URL}`, { title });
    return response.data;
  }

  /**
   * Update a conversation
   */
  public async updateConversation(
    conversationId: string,
    data: { title?: string }
  ): Promise<Conversation> {
    const response = await apiService.put<{
      data: Conversation;
      success: boolean;
    }>(`${CONVERSATIONS_API_URL}/${conversationId}`, data);
    return response.data;
  }

  /**
   * Delete a conversation
   */
  public async deleteConversation(conversationId: string): Promise<void> {
    const response = await apiService.delete<{
      success: boolean;
      message: string;
    }>(`${CONVERSATIONS_API_URL}/${conversationId}`);
    // No data to return for delete operation
    return;
  }

  /**
   * Get all messages for a conversation
   */
  public async getMessages(conversationId: string): Promise<Message[]> {
    const response = await apiService.get<{ data: Message[]; success: boolean }>(
      `${CONVERSATIONS_API_URL}/${conversationId}/messages`
    );
    return response.data || [];
  }

  /**
   * Add a message to a conversation
   */
  public async addMessage(
    conversationId: string,
    content: string,
    role: "user" | "assistant",
    modelUsed?: string,
    parameters?: any
  ): Promise<Message> {
    const response = await apiService.post<{ data: Message; success: boolean }>(
      `${CONVERSATIONS_API_URL}/${conversationId}/messages`,
      {
        content,
        role,
        modelUsed,
        parameters,
      }
    );
    return response.data;
  }
}

// Singleton instance
export const conversationService = new ConversationService();

import { apiService } from "./api.service";
import {
  Conversation,
  LLMParameters,
  Message,
  LLMProvider,
  LLMModel,
} from "../../interfaces/llm";
import { LLM_API_URL } from "../../config/constants";

export class LLMService {
  /**
   * Get available LLM providers
   */
  public async getProviders(): Promise<LLMProvider[]> {
    return apiService.get<LLMProvider[]>(`${LLM_API_URL}/providers`);
  }

  /**
   * Get available models for a specific provider
   */
  public async getModels(providerId: string): Promise<LLMModel[]> {
    return apiService.get<LLMModel[]>(
      `${LLM_API_URL}/providers/${providerId}/models`
    );
  }

  /**
   * Send a message to an LLM and get a response (non-streaming)
   */
  public async sendMessage(
    message: string,
    conversationId: string | null,
    parameters: LLMParameters
  ): Promise<{
    messages: Message[];
    conversation?: Conversation;
  }> {
    // Get provider from parameters
    const providerId = parameters.provider || "openai";

    return apiService.post<{
      messages: Message[];
      conversation?: Conversation;
    }>(`${LLM_API_URL}/completions/${providerId}`, {
      prompt: message,
      conversationId,
      model: parameters.model,
      temperature: parameters.temperature,
      maxTokens: parameters.maxTokens,
      topP: parameters.topP,
      stopSequences: parameters.stopSequences,
    });
  }

  /**
   * Send a message to an LLM and get a streaming response
   */
  public streamMessage(
    message: string,
    conversationId: string | null,
    parameters: LLMParameters
  ) {
    // Get provider from parameters
    const providerId = parameters.provider || "openai";

    const queryParams = new URLSearchParams({
      prompt: message,
      ...(conversationId && { conversationId }),
      ...(parameters.model && { model: parameters.model }),
      ...(parameters.temperature !== undefined && {
        temperature: parameters.temperature.toString(),
      }),
      ...(parameters.maxTokens !== undefined && {
        maxTokens: parameters.maxTokens.toString(),
      }),
      ...(parameters.topP !== undefined && {
        topP: parameters.topP.toString(),
      }),
    }).toString();

    return apiService.createEventSource(
      `/llm/completions/${providerId}/stream?${queryParams}` // Use relative path
    );
  }

  /**
   * Get conversation history
   */
  public async getConversations(page = 1, limit = 10): Promise<Conversation[]> {
    return apiService.get<Conversation[]>(
      `${LLM_API_URL}/conversations?page=${page}&limit=${limit}`
    );
  }

  /**
   * Get a specific conversation by ID
   */
  public async getConversation(conversationId: string) {
    return apiService.get<Conversation>(
      `${LLM_API_URL}/conversations/${conversationId}`
    );
  }

  /**
   * Create a new conversation
   */
  public async createConversation(title: string) {
    return apiService.post<Conversation>(`${LLM_API_URL}/conversations`, {
      title,
    });
  }

  /**
   * Update a conversation
   */
  public async updateConversation(
    conversationId: string,
    data: Partial<Conversation>
  ) {
    return apiService.put<Conversation>(
      `${LLM_API_URL}/conversations/${conversationId}`,
      data
    );
  }

  /**
   * Delete a conversation
   */
  public async deleteConversation(conversationId: string) {
    return apiService.delete(`${LLM_API_URL}/conversations/${conversationId}`);
  }

  /**
   * Get performance metrics for a model
   */
  public async getPerformanceMetrics(providerId: string, modelId: string) {
    return apiService.get(`${LLM_API_URL}/metrics/${providerId}/${modelId}`);
  }

  /**
   * Compare performance metrics across models
   */
  public async compareModels(
    models: { providerId: string; modelId: string }[]
  ) {
    return apiService.post(`${LLM_API_URL}/metrics/compare`, { models });
  }
}

// Singleton instance
export const llmService = new LLMService();

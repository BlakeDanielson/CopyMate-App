export interface LLMProvider {
  id: string;
  name: string;
  description: string;
  models: LLMModel[];
  icon?: string;
}

export interface LLMModel {
  id: string;
  name: string;
  description: string;
  maxTokens: number;
  provider: string;
  capabilities: string[];
}

export interface LLMParameters {
  provider?: string;
  model?: string;
  temperature: number;
  maxTokens: number;
  topP: number;
  stopSequences?: string[];
  presencePenalty?: number;
  frequencyPenalty?: number;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  model?: string;
  provider?: string;
  metrics?: MessageMetrics;
}

export interface MessageMetrics {
  timeToFirstToken?: number;
  tokensPerSecond?: number;
  totalTokens?: number;
  totalCost?: number;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  model?: string;
  provider?: string;
}

export interface ConversationSettings {
  model: string;
  provider: string;
  parameters: LLMParameters;
}

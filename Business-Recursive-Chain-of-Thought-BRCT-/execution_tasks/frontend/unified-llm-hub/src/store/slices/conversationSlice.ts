import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { Conversation, Message } from "../../interfaces/llm";
import { llmService } from "../../services/api/llm.service";
import { conversationService } from "../../services/api/conversation.service";
import { v4 as uuidv4 } from "uuid";

interface ConversationState {
  conversations: Conversation[];
  activeConversation: Conversation | null;
  loading: boolean;
  error: string | null;
  streaming: boolean;
}

const initialState: ConversationState = {
  conversations: [],
  activeConversation: null,
  loading: false,
  error: null,
  streaming: false,
};

// Async thunks
export const fetchConversations = createAsyncThunk<Conversation[]>(
  "conversation/fetchConversations",
  async (_, { rejectWithValue }) => {
    try {
      const response = await conversationService.getConversations();
      return response;
    } catch (error) {
      return rejectWithValue("Failed to fetch conversations");
    }
  }
);

export const fetchConversation = createAsyncThunk<Conversation, string>(
  "conversation/fetchConversation",
  async (conversationId: string, { rejectWithValue }) => {
    try {
      const response = await conversationService.getConversation(
        conversationId
      );
      return response;
    } catch (error) {
      return rejectWithValue("Failed to fetch conversation");
    }
  }
);

export const createNewConversation = createAsyncThunk<Conversation, string>(
  "conversation/createNewConversation",
  async (title: string, { rejectWithValue }) => {
    try {
      const response = await conversationService.createConversation(title);
      return response;
    } catch (error) {
      return rejectWithValue("Failed to create conversation");
    }
  }
);

export const deleteConversationThunk = createAsyncThunk<string, string>(
  "conversation/deleteConversation",
  async (conversationId: string, { rejectWithValue }) => {
    try {
      await conversationService.deleteConversation(conversationId);
      return conversationId;
    } catch (error) {
      return rejectWithValue("Failed to delete conversation");
    }
  }
);

export const addMessageToConversation = createAsyncThunk<
  Message,
  {
    conversationId: string;
    content: string;
    role: "user" | "assistant";
    modelUsed?: string;
    parameters?: any;
  }
>(
  "conversation/addMessageToConversation",
  async (
    { conversationId, content, role, modelUsed, parameters },
    { rejectWithValue }
  ) => {
    try {
      const response = await conversationService.addMessage(
        conversationId,
        content,
        role,
        modelUsed,
        parameters
      );
      return response;
    } catch (error) {
      return rejectWithValue("Failed to add message to conversation");
    }
  }
);

interface SendMessagePayload {
  message: string;
  conversationId: string | null;
  parameters: any;
}

interface SendMessageResponse {
  messages: Message[];
  conversation?: Conversation;
}

export const sendMessage = createAsyncThunk<
  SendMessageResponse,
  SendMessagePayload
>(
  "conversation/sendMessage",
  async (
    { message, conversationId, parameters }: SendMessagePayload,
    { dispatch, rejectWithValue }
  ) => {
    try {
      // Create a new conversation if we don't have one
      let actualConversationId = conversationId;

      if (!actualConversationId) {
        // Create a new conversation with a default title (first few words of message)
        const title =
          message.length > 30 ? message.substring(0, 27) + "..." : message;
        const newConversation = await conversationService.createConversation(
          title
        );
        actualConversationId = newConversation.id;

        // Update our store with the new conversation
        dispatch(
          createNewConversation.fulfilled(
            newConversation,
            "createNewConversation",
            title
          )
        );
      }

      // First, add the user message to the conversation
      await conversationService.addMessage(
        actualConversationId,
        message,
        "user"
      );

      // Then get the AI response using the LLM service
      const response = await llmService.sendMessage(
        message,
        actualConversationId,
        parameters
      );

      // If we get a response with messages, add the assistant message to our conversation history
      if (response.messages && response.messages.length > 0) {
        const assistantMessage = response.messages.find(
          (m) => m.role === "assistant"
        );
        if (assistantMessage) {
          await conversationService.addMessage(
            actualConversationId,
            assistantMessage.content,
            "assistant",
            parameters.model,
            parameters
          );
        }
      }

      return response;
    } catch (error) {
      return rejectWithValue("Failed to send message");
    }
  }
);

const conversationSlice = createSlice({
  name: "conversation",
  initialState,
  reducers: {
    setActiveConversation: (
      state,
      action: PayloadAction<Conversation | null>
    ) => {
      state.activeConversation = action.payload;
    },
    addMessage: (state, action: PayloadAction<Message>) => {
      if (state.activeConversation) {
        state.activeConversation.messages.push(action.payload);
        state.activeConversation.updatedAt = new Date();
      }
    },
    startStreaming: (state) => {
      state.streaming = true;
    },
    stopStreaming: (state) => {
      state.streaming = false;
    },
    updateStreamingMessage: (
      state,
      action: PayloadAction<{ content: string }>
    ) => {
      if (
        state.activeConversation &&
        state.activeConversation.messages.length > 0
      ) {
        const lastMessage =
          state.activeConversation.messages[
            state.activeConversation.messages.length - 1
          ];
        if (lastMessage.role === "assistant") {
          lastMessage.content = action.payload.content;
        }
      }
    },
    // For local creation of a new conversation (before API call)
    createLocalConversation: (state, action: PayloadAction<string>) => {
      const newConversation: Conversation = {
        id: uuidv4(),
        title: action.payload,
        messages: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      state.conversations.unshift(newConversation);
      state.activeConversation = newConversation;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // fetchConversations
      .addCase(fetchConversations.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchConversations.fulfilled, (state, action) => {
        state.loading = false;
        state.conversations = action.payload;
      })
      .addCase(fetchConversations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // fetchConversation
      .addCase(fetchConversation.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchConversation.fulfilled, (state, action) => {
        state.loading = false;
        state.activeConversation = action.payload;
      })
      .addCase(fetchConversation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // createNewConversation
      .addCase(createNewConversation.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createNewConversation.fulfilled, (state, action) => {
        state.loading = false;
        state.conversations.unshift(action.payload);
        state.activeConversation = action.payload;
      })
      .addCase(createNewConversation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // deleteConversation
      .addCase(deleteConversationThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteConversationThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.conversations = state.conversations.filter(
          (conv) => conv.id !== action.payload
        );
        if (
          state.activeConversation &&
          state.activeConversation.id === action.payload
        ) {
          state.activeConversation = null;
        }
      })
      .addCase(deleteConversationThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // sendMessage
      .addCase(sendMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.loading = false;
        // Update active conversation with new messages
        if (state.activeConversation) {
          // The response might contain both the user message and assistant response
          const newMessages = action.payload.messages || [];
          if (newMessages.length > 0) {
            state.activeConversation.messages.push(...newMessages);
          }
          state.activeConversation.updatedAt = new Date();
        }
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  setActiveConversation,
  addMessage,
  startStreaming,
  stopStreaming,
  updateStreamingMessage,
  createLocalConversation,
  clearError,
} = conversationSlice.actions;

export default conversationSlice.reducer;

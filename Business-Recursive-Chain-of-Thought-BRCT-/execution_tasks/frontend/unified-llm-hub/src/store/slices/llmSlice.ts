import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { LLMProvider, LLMModel, LLMParameters } from "../../interfaces/llm";
import { llmService } from "../../services/api/llm.service";
import { DEFAULT_PARAMETERS, PROVIDERS } from "../../config/constants";

interface LLMState {
  providers: LLMProvider[];
  models: LLMModel[];
  selectedProvider: string | null;
  selectedModel: string | null;
  parameters: LLMParameters;
  loading: boolean;
  error: string | null;
  performanceMetrics: {
    [key: string]: any; // Provider/model specific metrics
  };
}

const initialState: LLMState = {
  providers: [],
  models: [],
  selectedProvider: null,
  selectedModel: null,
  parameters: DEFAULT_PARAMETERS,
  loading: false,
  error: null,
  performanceMetrics: {},
};

// Async thunks
export const fetchProviders = createAsyncThunk<LLMProvider[]>(
  "llm/fetchProviders",
  async (_, { rejectWithValue }) => {
    try {
      const providers = await llmService.getProviders();
      return providers;
    } catch (error) {
      return rejectWithValue("Failed to fetch LLM providers");
    }
  }
);

export const fetchModels = createAsyncThunk<LLMModel[], string>(
  "llm/fetchModels",
  async (providerId, { rejectWithValue }) => {
    try {
      const models = await llmService.getModels(providerId);
      return models;
    } catch (error) {
      return rejectWithValue(
        "Failed to fetch models for the selected provider"
      );
    }
  }
);

export const fetchPerformanceMetrics = createAsyncThunk<
  any,
  { providerId: string; modelId: string }
>(
  "llm/fetchPerformanceMetrics",
  async ({ providerId, modelId }, { rejectWithValue }) => {
    try {
      const metrics = await llmService.getPerformanceMetrics(
        providerId,
        modelId
      );
      return { providerId, modelId, metrics };
    } catch (error) {
      return rejectWithValue("Failed to fetch performance metrics");
    }
  }
);

// Helper function to get mock initial data
const getMockProviders = (): LLMProvider[] => [
  {
    id: PROVIDERS.OPENAI,
    name: "OpenAI",
    description: "Leading AI research lab and creator of GPT models",
    models: [],
    icon: "openai-logo.svg",
  },
  {
    id: PROVIDERS.ANTHROPIC,
    name: "Anthropic",
    description: "AI safety company and creator of Claude models",
    models: [],
    icon: "anthropic-logo.svg",
  },
  {
    id: PROVIDERS.GEMINI,
    name: "Google Gemini",
    description: "Google's multimodal AI system",
    models: [],
    icon: "gemini-logo.svg",
  },
];

const getMockModels = (providerId: string): LLMModel[] => {
  switch (providerId) {
    case PROVIDERS.OPENAI:
      return [
        {
          id: "gpt-4",
          name: "GPT-4",
          description: "Most capable model, best for complex tasks",
          maxTokens: 8192,
          provider: PROVIDERS.OPENAI,
          capabilities: ["text", "code", "reasoning"],
        },
        {
          id: "gpt-3.5-turbo",
          name: "GPT-3.5 Turbo",
          description: "Fast and efficient model for most tasks",
          maxTokens: 4096,
          provider: PROVIDERS.OPENAI,
          capabilities: ["text", "code"],
        },
      ];
    case PROVIDERS.ANTHROPIC:
      return [
        {
          id: "claude-3-opus",
          name: "Claude 3 Opus",
          description: "Most capable Claude model for complex tasks",
          maxTokens: 100000,
          provider: PROVIDERS.ANTHROPIC,
          capabilities: ["text", "code", "reasoning"],
        },
        {
          id: "claude-3-sonnet",
          name: "Claude 3 Sonnet",
          description: "Balanced for performance and intelligence",
          maxTokens: 72000,
          provider: PROVIDERS.ANTHROPIC,
          capabilities: ["text", "code"],
        },
        {
          id: "claude-3-haiku",
          name: "Claude 3 Haiku",
          description: "Fastest and most compact Claude model",
          maxTokens: 48000,
          provider: PROVIDERS.ANTHROPIC,
          capabilities: ["text"],
        },
      ];
    case PROVIDERS.GEMINI:
      return [
        {
          id: "gemini-1.5-pro",
          name: "Gemini 1.5 Pro",
          description: "High capability model designed for complex tasks",
          maxTokens: 32000,
          provider: PROVIDERS.GEMINI,
          capabilities: ["text", "code", "reasoning"],
        },
        {
          id: "gemini-1.5-flash",
          name: "Gemini 1.5 Flash",
          description: "Fast and efficient model for most tasks",
          maxTokens: 16000,
          provider: PROVIDERS.GEMINI,
          capabilities: ["text", "code"],
        },
      ];
    default:
      return [];
  }
};

const llmSlice = createSlice({
  name: "llm",
  initialState,
  reducers: {
    setSelectedProvider: (state, action: PayloadAction<string>) => {
      state.selectedProvider = action.payload;
      // Clear selected model when provider changes
      state.selectedModel = null;
    },
    setSelectedModel: (state, action: PayloadAction<string>) => {
      state.selectedModel = action.payload;
    },
    updateParameters: (
      state,
      action: PayloadAction<Partial<LLMParameters>>
    ) => {
      state.parameters = {
        ...state.parameters,
        ...action.payload,
      };
    },
    resetParameters: (state) => {
      state.parameters = DEFAULT_PARAMETERS;
    },
    // For demo/testing: initialize with mock data
    initializeMockData: (state) => {
      state.providers = getMockProviders();
      if (state.providers.length > 0) {
        state.selectedProvider = state.providers[0].id;

        // Get models for the selected provider
        const models = getMockModels(state.selectedProvider);
        state.models = models;

        if (models.length > 0) {
          state.selectedModel = models[0].id;
        }
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // fetchProviders
      .addCase(fetchProviders.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProviders.fulfilled, (state, action) => {
        state.loading = false;
        state.providers = action.payload;

        // Select first provider if none is selected
        if (!state.selectedProvider && action.payload.length > 0) {
          state.selectedProvider = action.payload[0].id;
        }
      })
      .addCase(fetchProviders.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // fetchModels
      .addCase(fetchModels.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchModels.fulfilled, (state, action) => {
        state.loading = false;
        state.models = action.payload;

        // Select first model if none is selected
        if (!state.selectedModel && action.payload.length > 0) {
          state.selectedModel = action.payload[0].id;
        }
      })
      .addCase(fetchModels.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // fetchPerformanceMetrics
      .addCase(fetchPerformanceMetrics.fulfilled, (state, action) => {
        const { providerId, modelId, metrics } = action.payload;
        state.performanceMetrics[`${providerId}:${modelId}`] = metrics;
      });
  },
});

export const {
  setSelectedProvider,
  setSelectedModel,
  updateParameters,
  resetParameters,
  initializeMockData,
} = llmSlice.actions;

export default llmSlice.reducer;

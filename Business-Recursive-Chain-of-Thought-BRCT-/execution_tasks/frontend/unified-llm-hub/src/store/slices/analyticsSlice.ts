import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { analyticsService } from "../../services/api/analytics.service";
import {
  TimeWindow,
  AnalyticsDashboardData,
  ApiPerformanceMetrics,
  LlmPerformanceMetrics,
  ProviderModelMap,
  AnalyticsDashboardResponse,
  ApiPerformanceResponse,
  LlmPerformanceResponse,
  EndpointsResponse,
  ProviderModelsResponse,
} from "../../interfaces/analytics";

// State interface
interface AnalyticsState {
  dashboard: {
    data: AnalyticsDashboardData | null;
    loading: boolean;
    error: string | null;
  };
  apiPerformance: {
    data: ApiPerformanceMetrics[];
    loading: boolean;
    error: string | null;
  };
  llmPerformance: {
    data: LlmPerformanceMetrics[];
    loading: boolean;
    error: string | null;
  };
  filters: {
    timeWindow: TimeWindow;
    startDate: string | null;
    endDate: string | null;
    providers: string[];
    models: string[];
    endpoints: string[];
    successOnly: boolean;
  };
  availableFilters: {
    providers: string[];
    models: Record<string, string[]>;
    endpoints: string[];
    loading: boolean;
    error: string | null;
  };
}

// Initial state
const initialState: AnalyticsState = {
  dashboard: {
    data: null,
    loading: false,
    error: null,
  },
  apiPerformance: {
    data: [],
    loading: false,
    error: null,
  },
  llmPerformance: {
    data: [],
    loading: false,
    error: null,
  },
  filters: {
    timeWindow: TimeWindow.DAY,
    startDate: null,
    endDate: null,
    providers: [],
    models: [],
    endpoints: [],
    successOnly: false,
  },
  availableFilters: {
    providers: [],
    models: {},
    endpoints: [],
    loading: false,
    error: null,
  },
};

// Async thunks
export const fetchDashboardData = createAsyncThunk(
  "analytics/fetchDashboard",
  async (
    filters: {
      timeWindow?: TimeWindow;
      startDate?: Date;
      endDate?: Date;
      providers?: string[];
      models?: string[];
      endpoints?: string[];
    },
    { rejectWithValue }
  ) => {
    try {
      const response: AnalyticsDashboardResponse =
        await analyticsService.getDashboardData(
          filters.timeWindow,
          filters.startDate,
          filters.endDate,
          {
            providers: filters.providers,
            models: filters.models,
            endpoints: filters.endpoints,
          }
        );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch dashboard data"
      );
    }
  }
);

export const fetchApiPerformance = createAsyncThunk(
  "analytics/fetchApiPerformance",
  async (
    filters: {
      timeWindow?: TimeWindow;
      startDate?: Date;
      endDate?: Date;
      endpoints?: string[];
    },
    { rejectWithValue }
  ) => {
    try {
      const response: ApiPerformanceResponse =
        await analyticsService.getApiPerformanceMetrics(
          filters.timeWindow,
          filters.startDate,
          filters.endDate,
          filters.endpoints
        );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message ||
          "Failed to fetch API performance metrics"
      );
    }
  }
);

export const fetchLlmPerformance = createAsyncThunk(
  "analytics/fetchLlmPerformance",
  async (
    filters: {
      timeWindow?: TimeWindow;
      startDate?: Date;
      endDate?: Date;
      providers?: string[];
      models?: string[];
      successOnly?: boolean;
    },
    { rejectWithValue }
  ) => {
    try {
      const response: LlmPerformanceResponse =
        await analyticsService.getLlmPerformanceMetrics(
          filters.timeWindow,
          filters.startDate,
          filters.endDate,
          {
            providers: filters.providers,
            models: filters.models,
            successOnly: filters.successOnly,
          }
        );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message ||
          "Failed to fetch LLM performance metrics"
      );
    }
  }
);

export const fetchAvailableFilters = createAsyncThunk(
  "analytics/fetchAvailableFilters",
  async (_, { rejectWithValue }) => {
    try {
      const [endpointsResponse, providerModelsResponse]: [
        EndpointsResponse,
        ProviderModelsResponse
      ] = await Promise.all([
        analyticsService.getUniqueEndpoints(),
        analyticsService.getUniqueProviderModels(),
      ]);

      return {
        endpoints: endpointsResponse.data,
        providerModels: providerModelsResponse.data,
      };
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch available filters"
      );
    }
  }
);

// Create slice
const analyticsSlice = createSlice({
  name: "analytics",
  initialState,
  reducers: {
    setTimeWindow: (state, action: PayloadAction<TimeWindow>) => {
      state.filters.timeWindow = action.payload;
    },
    setDateRange: (
      state,
      action: PayloadAction<{
        startDate: string | null;
        endDate: string | null;
      }>
    ) => {
      state.filters.startDate = action.payload.startDate;
      state.filters.endDate = action.payload.endDate;
    },
    setProviders: (state, action: PayloadAction<string[]>) => {
      state.filters.providers = action.payload;
    },
    setModels: (state, action: PayloadAction<string[]>) => {
      state.filters.models = action.payload;
    },
    setEndpoints: (state, action: PayloadAction<string[]>) => {
      state.filters.endpoints = action.payload;
    },
    setSuccessOnly: (state, action: PayloadAction<boolean>) => {
      state.filters.successOnly = action.payload;
    },
    resetFilters: (state) => {
      state.filters = initialState.filters;
    },
  },
  extraReducers: (builder) => {
    // Dashboard data
    builder.addCase(fetchDashboardData.pending, (state) => {
      state.dashboard.loading = true;
      state.dashboard.error = null;
    });
    builder.addCase(fetchDashboardData.fulfilled, (state, action) => {
      state.dashboard.loading = false;
      state.dashboard.data = action.payload;
    });
    builder.addCase(fetchDashboardData.rejected, (state, action) => {
      state.dashboard.loading = false;
      state.dashboard.error = action.payload as string;
    });

    // API performance
    builder.addCase(fetchApiPerformance.pending, (state) => {
      state.apiPerformance.loading = true;
      state.apiPerformance.error = null;
    });
    builder.addCase(fetchApiPerformance.fulfilled, (state, action) => {
      state.apiPerformance.loading = false;
      state.apiPerformance.data = action.payload;
    });
    builder.addCase(fetchApiPerformance.rejected, (state, action) => {
      state.apiPerformance.loading = false;
      state.apiPerformance.error = action.payload as string;
    });

    // LLM performance
    builder.addCase(fetchLlmPerformance.pending, (state) => {
      state.llmPerformance.loading = true;
      state.llmPerformance.error = null;
    });
    builder.addCase(fetchLlmPerformance.fulfilled, (state, action) => {
      state.llmPerformance.loading = false;
      state.llmPerformance.data = action.payload;
    });
    builder.addCase(fetchLlmPerformance.rejected, (state, action) => {
      state.llmPerformance.loading = false;
      state.llmPerformance.error = action.payload as string;
    });

    // Available filters
    builder.addCase(fetchAvailableFilters.pending, (state) => {
      state.availableFilters.loading = true;
      state.availableFilters.error = null;
    });
    builder.addCase(fetchAvailableFilters.fulfilled, (state, action) => {
      state.availableFilters.loading = false;
      state.availableFilters.endpoints = action.payload.endpoints;

      // Extract providers and models
      const providerModels = action.payload.providerModels as ProviderModelMap;
      state.availableFilters.providers = Object.keys(providerModels.byProvider);
      state.availableFilters.models = providerModels.byProvider;
    });
    builder.addCase(fetchAvailableFilters.rejected, (state, action) => {
      state.availableFilters.loading = false;
      state.availableFilters.error = action.payload as string;
    });
  },
});

// Export actions
export const {
  setTimeWindow,
  setDateRange,
  setProviders,
  setModels,
  setEndpoints,
  setSuccessOnly,
  resetFilters,
} = analyticsSlice.actions;

// Export reducer
export default analyticsSlice.reducer;

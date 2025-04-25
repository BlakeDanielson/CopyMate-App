import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import subscriptionService, {
  SubscriptionPlan,
  UserSubscription,
  SubscriptionQuota,
} from "../../services/api/subscription.service";
import { StoreState } from "../store";

// State type
interface SubscriptionState {
  plans: {
    data: SubscriptionPlan[];
    loading: boolean;
    error: string | null;
  };
  currentSubscription: {
    data: UserSubscription | null;
    loading: boolean;
    error: string | null;
  };
  quota: {
    data: SubscriptionQuota | null;
    loading: boolean;
    error: string | null;
  };
  checkout: {
    loading: boolean;
    error: string | null;
  };
}

// Initial state
const initialState: SubscriptionState = {
  plans: {
    data: [],
    loading: false,
    error: null,
  },
  currentSubscription: {
    data: null,
    loading: false,
    error: null,
  },
  quota: {
    data: null,
    loading: false,
    error: null,
  },
  checkout: {
    loading: false,
    error: null,
  },
};

// Async thunks
export const fetchSubscriptionPlans = createAsyncThunk(
  "subscription/fetchPlans",
  async (_, { rejectWithValue }) => {
    try {
      return await subscriptionService.getSubscriptionPlans();
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch subscription plans"
      );
    }
  }
);

export const fetchCurrentSubscription = createAsyncThunk(
  "subscription/fetchCurrent",
  async (_, { rejectWithValue }) => {
    try {
      return await subscriptionService.getCurrentSubscription();
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch current subscription"
      );
    }
  }
);

export const fetchSubscriptionQuota = createAsyncThunk(
  "subscription/fetchQuota",
  async (_, { rejectWithValue }) => {
    try {
      return await subscriptionService.getSubscriptionQuota();
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch subscription quota"
      );
    }
  }
);

export const createCheckoutSession = createAsyncThunk(
  "subscription/createCheckout",
  async (planId: string, { rejectWithValue }) => {
    try {
      const response = await subscriptionService.createCheckoutSession(planId);
      // Redirect to Stripe checkout
      window.location.href = response.url;
      return response;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to create checkout session"
      );
    }
  }
);

export const openCustomerPortal = createAsyncThunk(
  "subscription/openPortal",
  async (_, { rejectWithValue }) => {
    try {
      const response = await subscriptionService.createCustomerPortalSession();
      // Redirect to Stripe customer portal
      window.location.href = response.url;
      return response;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to open customer portal"
      );
    }
  }
);

// Slice
const subscriptionSlice = createSlice({
  name: "subscription",
  initialState,
  reducers: {
    resetErrors: (state) => {
      state.plans.error = null;
      state.currentSubscription.error = null;
      state.quota.error = null;
      state.checkout.error = null;
    },
  },
  extraReducers: (builder) => {
    // Subscription plans
    builder
      .addCase(fetchSubscriptionPlans.pending, (state) => {
        state.plans.loading = true;
        state.plans.error = null;
      })
      .addCase(
        fetchSubscriptionPlans.fulfilled,
        (state, action: PayloadAction<SubscriptionPlan[]>) => {
          state.plans.loading = false;
          state.plans.data = action.payload;
        }
      )
      .addCase(fetchSubscriptionPlans.rejected, (state, action) => {
        state.plans.loading = false;
        state.plans.error = action.payload as string;
      });

    // Current subscription
    builder
      .addCase(fetchCurrentSubscription.pending, (state) => {
        state.currentSubscription.loading = true;
        state.currentSubscription.error = null;
      })
      .addCase(
        fetchCurrentSubscription.fulfilled,
        (state, action: PayloadAction<UserSubscription | null>) => {
          state.currentSubscription.loading = false;
          state.currentSubscription.data = action.payload;
        }
      )
      .addCase(fetchCurrentSubscription.rejected, (state, action) => {
        state.currentSubscription.loading = false;
        state.currentSubscription.error = action.payload as string;
      });

    // Subscription quota
    builder
      .addCase(fetchSubscriptionQuota.pending, (state) => {
        state.quota.loading = true;
        state.quota.error = null;
      })
      .addCase(
        fetchSubscriptionQuota.fulfilled,
        (state, action: PayloadAction<SubscriptionQuota | null>) => {
          state.quota.loading = false;
          state.quota.data = action.payload;
        }
      )
      .addCase(fetchSubscriptionQuota.rejected, (state, action) => {
        state.quota.loading = false;
        state.quota.error = action.payload as string;
      });

    // Checkout session
    builder
      .addCase(createCheckoutSession.pending, (state) => {
        state.checkout.loading = true;
        state.checkout.error = null;
      })
      .addCase(createCheckoutSession.fulfilled, (state) => {
        state.checkout.loading = false;
      })
      .addCase(createCheckoutSession.rejected, (state, action) => {
        state.checkout.loading = false;
        state.checkout.error = action.payload as string;
      });

    // Customer portal
    builder
      .addCase(openCustomerPortal.pending, (state) => {
        state.checkout.loading = true;
        state.checkout.error = null;
      })
      .addCase(openCustomerPortal.fulfilled, (state) => {
        state.checkout.loading = false;
      })
      .addCase(openCustomerPortal.rejected, (state, action) => {
        state.checkout.loading = false;
        state.checkout.error = action.payload as string;
      });
  },
});

// Actions
export const { resetErrors } = subscriptionSlice.actions;

// Selectors
export const selectSubscriptionPlans = (state: StoreState) =>
  state.subscription.plans;
export const selectCurrentSubscription = (state: StoreState) =>
  state.subscription.currentSubscription;
export const selectSubscriptionQuota = (state: StoreState) =>
  state.subscription.quota;
export const selectCheckoutState = (state: StoreState) =>
  state.subscription.checkout;

// Helper selectors
export const selectIsSubscribed = (state: StoreState) => {
  const subscription = state.subscription.currentSubscription.data;
  return !!subscription && subscription.status === "ACTIVE";
};

export const selectUsagePercentage = (state: StoreState) => {
  const quota = state.subscription.quota.data;
  return quota ? quota.usagePercentage : 0;
};

export const selectRemainingQuota = (state: StoreState) => {
  const quota = state.subscription.quota.data;
  return quota ? quota.remainingQuota : 0;
};

export default subscriptionSlice.reducer;

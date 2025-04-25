import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { AuthState, User, UserMetrics } from "../../interfaces/auth";
import { STORAGE_KEYS } from "../../config/constants";
import { authService } from "../../services/api/auth.service";

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  loading: false,
  error: null,
};

// Async thunks
export const login = createAsyncThunk<
  User,
  { email: string; password: string }
>("auth/login", async (credentials, { rejectWithValue }) => {
  try {
    const user = await authService.login(
      credentials.email,
      credentials.password
    );
    return user;
  } catch (error) {
    return rejectWithValue("Login failed. Please check your credentials.");
  }
});

export const logout = createAsyncThunk("auth/logout", async () => {
  await authService.logout();
  return true;
});

export const checkAuth = createAsyncThunk<User | null>(
  "auth/checkAuth",
  async () => {
    return authService.checkAuth();
  }
);

export const updateProfile = createAsyncThunk<User, Partial<User>>(
  "auth/updateProfile",
  async (userData, { rejectWithValue }) => {
    try {
      return await authService.updateProfile(userData);
    } catch (error) {
      return rejectWithValue("Failed to update profile.");
    }
  }
);

export const fetchUserMetrics = createAsyncThunk<UserMetrics>(
  "auth/fetchUserMetrics",
  async (_, { rejectWithValue }) => {
    try {
      return await authService.getUserMetrics();
    } catch (error) {
      return rejectWithValue("Failed to fetch usage metrics.");
    }
  }
);

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<User | null>) => {
      state.user = action.payload;
      state.isAuthenticated = !!action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    updateUserPreferences: (
      state,
      action: PayloadAction<Partial<User["preferences"]>>
    ) => {
      if (state.user) {
        state.user.preferences = {
          ...state.user.preferences,
          ...action.payload,
        };

        // Update in local storage too
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(state.user));
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
      })
      // logout
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.isAuthenticated = false;
      })
      // checkAuth
      .addCase(checkAuth.fulfilled, (state, action) => {
        state.user = action.payload;
        state.isAuthenticated = !!action.payload;
      })
      // updateProfile
      .addCase(updateProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(updateProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // fetchUserMetrics
      .addCase(fetchUserMetrics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserMetrics.fulfilled, (state, action) => {
        state.loading = false;
        if (state.user) {
          state.user.metrics = action.payload;
        }
      })
      .addCase(fetchUserMetrics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { setUser, clearError, updateUserPreferences } = authSlice.actions;

export default authSlice.reducer;

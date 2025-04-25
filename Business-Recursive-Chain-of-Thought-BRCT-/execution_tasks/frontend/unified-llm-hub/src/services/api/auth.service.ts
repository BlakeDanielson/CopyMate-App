import { apiService } from "./api.service";
import { User, UserMetrics, SignUpUserInput } from "../../interfaces/auth"; // Added SignUpUserInput
import { AUTH_API_URL, STORAGE_KEYS } from "../../config/constants";

// Response interfaces for our backend
interface AuthTokenResponse {
  success: boolean;
  data: {
    accessToken: string;
  };
  message: string;
}

interface UserProfileResponse {
  success: boolean;
  data: {
    id: string;
    email: string;
    username?: string;
    fullName?: string;
    role: string;
    messageCount: number;
    createdAt: string;
    updatedAt: string;
  };
  message: string;
}

interface UserMetricsResponse {
  success: boolean;
  data: UserMetrics;
  message: string;
}

export class AuthService {
  /**
   * Login with email and password
   */
  public async login(email: string, password: string): Promise<User> {
    try {
      // Call backend API for login
      const response = await apiService.post<AuthTokenResponse>(
        `${AUTH_API_URL}/login`,
        { email, password }
      );

      // Extract token from response
      const { accessToken } = response.data;

      // Store token in localStorage
      localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, accessToken);

      // Fetch user profile with the token
      return this.fetchUserProfile();
    } catch (error) {
      console.error("Login error:", error);
      throw new Error("Login failed. Please check your credentials.");
    }
  }

  /**
   * Login using the test endpoint (no credentials needed)
   */
  public async testLogin(): Promise<User> {
    try {
      // Call backend API for test login
      const response = await apiService.post<AuthTokenResponse>(
        `${AUTH_API_URL}/test-login`,
        {} // No body needed for test login
      );

      // Extract token from response
      const { accessToken } = response.data;

      // Store token in localStorage
      localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, accessToken);

      // Fetch user profile with the token
      return this.fetchUserProfile();
    } catch (error) {
      console.error("Test login error:", error);
      // Provide a more specific error message if possible
      if ((error as any)?.response?.status === 403) {
        throw new Error("Test login is disabled in the backend configuration.");
      }
      throw new Error(
        "Test login failed. Please check backend configuration and logs."
      );
    }
  }

  /**
   * Register a new user
   */
  public async register(
    email: string,
    password: string,
    name?: string
  ): Promise<User> {
    try {
      // Call backend API for registration
      const userData = {
        email,
        password,
        username: name,
        fullName: name,
      };

      const response = await apiService.post<AuthTokenResponse>(
        `${AUTH_API_URL}/register`,
        userData
      );

      // Extract token from response
      const { accessToken } = response.data;

      // Store token in localStorage
      localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, accessToken);

      // Fetch user profile with the token
      return this.fetchUserProfile();
    } catch (error) {
      console.error("Registration error:", error);
      throw new Error("Registration failed. Please try again.");
    }
  }

/**
   * Sign up a new user
   */
  public async signup(userData: SignUpUserInput): Promise<void> {
    try {
      // Call backend API for signup
      // The backend returns the created user, but we don't need it here
      // as the component handles redirection.
      await apiService.post<UserProfileResponse>( // Assuming backend returns similar structure to profile on success
        `${AUTH_API_URL}/signup`,
        userData
      );
      // No need to store token or fetch profile here, redirection happens in component
    } catch (error) {
      console.error("Signup error:", error);
      // Re-throw the error to be handled by the component
      // The component will extract specific messages (e.g., email exists)
      throw error;
    }
  }
  /**
   * Logout the current user
   */
  public async logout(): Promise<void> {
    try {
      // No need to call API for logout, just remove token
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER);
    } catch (error) {
      console.error("Logout error:", error);
      // Still remove local storage items even if there's an error
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER);
    }
  }

  /**
   * Check if user is authenticated
   */
  public async checkAuth(): Promise<User | null> {
    try {
      const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);

      if (!token) {
        return null;
      }

      // Try to fetch profile with stored token
      return await this.fetchUserProfile();
    } catch (error) {
      console.error("Auth check error:", error);
      // Clear storage if token is invalid
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER);
      return null;
    }
  }

  /**
   * Update user profile
   */
  public async updateProfile(data: Partial<User>): Promise<User> {
    try {
      // For now, we'll just update the local storage
      // In the future, this would hit a backend endpoint
      const userJson = localStorage.getItem(STORAGE_KEYS.USER);
      if (!userJson) {
        throw new Error("User not found");
      }

      const user: User = JSON.parse(userJson);
      const updatedUser: User = {
        ...user,
        ...data,
        preferences: {
          ...user.preferences,
          ...(data.preferences || {}),
        },
      };

      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(updatedUser));
      return updatedUser;
    } catch (error) {
      console.error("Update profile error:", error);
      throw new Error("Failed to update profile");
    }
  }

  /**
   * Fetch user profile from backend and create frontend User object
   * This handles the mapping between backend and frontend user objects
   */
  /**
   * Fetch user metrics from backend
   */
  public async getUserMetrics(): Promise<UserMetrics> {
    try {
      // Get metrics from backend
      const response = await apiService.get<UserMetricsResponse>(
        `${AUTH_API_URL}/metrics`
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching user metrics:", error);
      throw new Error("Failed to retrieve usage metrics");
    }
  }

  /**
   * Fetch user profile from backend and create frontend User object
   * This handles the mapping between backend and frontend user objects
   */
  private async fetchUserProfile(): Promise<User> {
    try {
      // Get profile from backend
      const response = await apiService.get<UserProfileResponse>(
        `${AUTH_API_URL}/profile`
      );
      const backendUser = response.data;

      // Try to get metrics
      let metrics: UserMetrics | undefined = undefined;
      try {
        metrics = await this.getUserMetrics();
      } catch (error) {
        console.warn(
          "Could not fetch metrics, continuing without them:",
          error
        );
      }

      // Map backend user to frontend User format
      const user: User = {
        id: backendUser.id,
        email: backendUser.email,
        name:
          backendUser.fullName ||
          backendUser.username ||
          backendUser.email.split("@")[0],
        createdAt: new Date(backendUser.createdAt),
        lastLoginAt: new Date(), // Use current time as login time
        preferences: {
          theme: "system", // Default preference
        },
        subscription: {
          id: "sub_1", // Default subscription
          plan: "basic",
          status: "active",
          currentPeriodStart: new Date(),
          currentPeriodEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days
          messageQuota: 1000,
          messageUsed: backendUser.messageCount || 0,
        },
        metrics: metrics,
      };

      // Cache user data in localStorage for faster access
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));

      return user;
    } catch (error) {
      console.error("Error fetching user profile:", error);
      throw error;
    }
  }
}

// Singleton instance
export const authService = new AuthService();

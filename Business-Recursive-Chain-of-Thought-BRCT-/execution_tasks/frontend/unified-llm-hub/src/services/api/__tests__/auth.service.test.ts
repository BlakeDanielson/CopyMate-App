import axios from 'axios';
import { authService } from '../auth.service';
import { AUTH_API_URL, STORAGE_KEYS } from '../../../config/constants';

// Mock axios
jest.mock('axios');
const mockAxios = axios as jest.Mocked<typeof axios>;

// Mock localStorage
const mockLocalStorage = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
    length: 0,
    key: jest.fn((index: number) => ''),
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

describe('AuthService', () => {
  beforeEach(() => {
    // Clear mocks and localStorage before each test
    jest.clearAllMocks();
    mockLocalStorage.clear();
  });

  describe('signup method', () => {
    const signupData = {
      email: 'test@example.com',
      password: 'StrongPassword123!',
      confirmPassword: 'StrongPassword123!'
    };

    const mockApiResponse = {
      status: 201,
      data: {
        success: true,
        data: {
          id: 'user-123',
          email: 'test@example.com',
          role: 'USER'
        },
        message: 'User signed up successfully'
      }
    };

    it('should call the correct API endpoint with signup data', async () => {
      // Mock successful API response
      mockAxios.post.mockResolvedValueOnce(mockApiResponse);

      // Call the signup method
      await authService.signup(signupData);

      // Verify correct endpoint and data
      expect(mockAxios.post).toHaveBeenCalledWith(
        `${AUTH_API_URL}/signup`,
        signupData
      );
    });

    it('should not store token or user in localStorage after successful signup', async () => {
      // Mock successful API response
      mockAxios.post.mockResolvedValueOnce(mockApiResponse);

      // Call the signup method
      await authService.signup(signupData);

      // Verify localStorage was not updated (as mentioned in the code comments)
      expect(mockLocalStorage.setItem).not.toHaveBeenCalledWith(
        STORAGE_KEYS.AUTH_TOKEN,
        expect.any(String)
      );
      expect(mockLocalStorage.setItem).not.toHaveBeenCalledWith(
        STORAGE_KEYS.USER,
        expect.any(String)
      );
    });

    it('should throw an error when the API call fails', async () => {
      // Mock API error
      const errorResponse = {
        response: {
          status: 409,
          data: {
            success: false,
            error: 'Conflict',
            message: 'An account with this email address already exists.'
          }
        }
      };
      mockAxios.post.mockRejectedValueOnce(errorResponse);

      // Call the signup method and expect it to throw
      await expect(authService.signup(signupData))
        .rejects.toEqual(errorResponse);

      // Verify API was called
      expect(mockAxios.post).toHaveBeenCalledWith(
        `${AUTH_API_URL}/signup`,
        signupData
      );
    });
  });
});
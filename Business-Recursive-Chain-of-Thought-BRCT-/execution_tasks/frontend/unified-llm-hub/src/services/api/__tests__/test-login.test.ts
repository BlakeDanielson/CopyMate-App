import axios from 'axios';
import { authService } from '../auth.service';
import { AUTH_API_URL, STORAGE_KEYS } from '../../../config/constants';

// Mock axios
jest.mock('axios', () => ({
  create: jest.fn(() => mockAxios),
  post: jest.fn(),
  get: jest.fn(),
  interceptors: {
    request: { use: jest.fn() },
    response: { use: jest.fn() }
  },
  defaults: { headers: { common: {} } }
}));

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
    key: jest.fn(() => null)
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

describe('Test Login Functionality', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.clear();
  });

  it('should successfully call test login endpoint when available', async () => {
    // Arrange
    const mockApiResponse = {
      data: {
        success: true,
        data: {
          accessToken: 'test-token'
        },
        message: 'Test login successful'
      }
    };
    
    const mockProfileResponse = {
      data: {
        success: true,
        data: {
          id: 'test-user-id',
          email: 'test@example.com',
          username: 'Test User',
          role: 'USER',
          messageCount: 0,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        },
        message: 'Profile retrieved successfully'
      }
    };
    
    const mockMetricsResponse = {
      data: {
        usedMessages: 0,
        totalQuota: 1000,
        remainingMessages: 1000,
        usagePercentage: 0,
        billingPeriodStart: new Date().toISOString(),
        billingPeriodEnd: new Date().toISOString(),
        messagesPerProvider: {}
      }
    };
    
    // Mock the test login endpoint response
    mockAxios.post.mockImplementation((url) => {
      if (url === `${AUTH_API_URL}/test-login`) {
        return Promise.resolve(mockApiResponse);
      }
      return Promise.reject(new Error('Unexpected URL'));
    });
    
    // Mock the profile and metrics endpoint responses
    mockAxios.get.mockImplementation((url) => {
      if (url === `${AUTH_API_URL}/profile`) {
        return Promise.resolve(mockProfileResponse);
      } else if (url === `${AUTH_API_URL}/metrics`) {
        return Promise.resolve(mockMetricsResponse);
      }
      return Promise.reject(new Error('Unexpected URL'));
    });
    
    // Act
    const result = await authService.testLogin();
    
    // Assert
    expect(mockAxios.post).toHaveBeenCalledWith(
      `${AUTH_API_URL}/test-login`,
      {} // No body needed for test login
    );
    
    expect(localStorage.setItem).toHaveBeenCalledWith(
      STORAGE_KEYS.AUTH_TOKEN,
      'test-token'
    );
    
    expect(mockAxios.get).toHaveBeenCalledWith(`${AUTH_API_URL}/profile`);
    
    // Verify user object is returned
    expect(result).toEqual(expect.objectContaining({
      id: 'test-user-id',
      email: 'test@example.com',
      name: expect.any(String)
    }));
  });

  it('should handle 403 error when test login is disabled', async () => {
    // Arrange
    const errorResponse = {
      response: {
        status: 403,
        data: {
          success: false,
          error: 'Forbidden',
          message: 'Test login is disabled in production environment'
        }
      }
    };
    
    // Mock the test login endpoint to return 403
    mockAxios.post.mockRejectedValueOnce(errorResponse);
    
    // Act & Assert
    await expect(authService.testLogin()).rejects.toThrow(
      'Test login is disabled in the backend configuration.'
    );
    
    expect(mockAxios.post).toHaveBeenCalledWith(
      `${AUTH_API_URL}/test-login`,
      {} // No body needed for test login
    );
    
    // Verify token was not stored
    expect(localStorage.setItem).not.toHaveBeenCalled();
  });

  it('should handle 404 error when test login endpoint does not exist', async () => {
    // Arrange
    const errorResponse = {
      response: {
        status: 404,
        data: {
          success: false,
          error: 'Not Found',
          message: 'Route not found'
        }
      }
    };
    
    // Mock the test login endpoint to return 404
    mockAxios.post.mockRejectedValueOnce(errorResponse);
    
    // Act & Assert
    await expect(authService.testLogin()).rejects.toThrow(
      'Test login failed. Please check backend configuration and logs.'
    );
    
    expect(mockAxios.post).toHaveBeenCalledWith(
      `${AUTH_API_URL}/test-login`,
      {} // No body needed for test login
    );
    
    // Verify token was not stored
    expect(localStorage.setItem).not.toHaveBeenCalled();
  });

  it('should handle other errors from test login endpoint', async () => {
    // Arrange
    const errorResponse = {
      response: {
        status: 500,
        data: {
          success: false,
          error: 'Internal Server Error',
          message: 'An unexpected error occurred'
        }
      }
    };
    
    // Mock the test login endpoint to return 500
    mockAxios.post.mockRejectedValueOnce(errorResponse);
    
    // Act & Assert
    await expect(authService.testLogin()).rejects.toThrow(
      'Test login failed. Please check backend configuration and logs.'
    );
    
    expect(mockAxios.post).toHaveBeenCalledWith(
      `${AUTH_API_URL}/test-login`,
      {} // No body needed for test login
    );
    
    // Verify token was not stored
    expect(localStorage.setItem).not.toHaveBeenCalled();
  });
});
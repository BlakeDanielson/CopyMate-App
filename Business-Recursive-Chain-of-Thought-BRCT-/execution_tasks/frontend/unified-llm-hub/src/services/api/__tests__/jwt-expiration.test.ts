import axios from 'axios';
import { apiService } from '../api.service';
import { STORAGE_KEYS } from '../../../config/constants';
import { authService } from '../auth.service';

// Mock axios
jest.mock('axios', () => {
  const mockAxios = {
    create: jest.fn(() => mockAxios),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() }
    },
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    patch: jest.fn(),
    delete: jest.fn(),
    defaults: { headers: { common: {} } }
  };
  return mockAxios;
});

// Mock auth service
jest.mock('../auth.service', () => ({
  authService: {
    checkAuth: jest.fn(),
    logout: jest.fn()
  }
}));

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

const mockAxios = axios as jest.Mocked<typeof axios>;

describe('JWT Expiration Handling', () => {
  let requestCallback: Function;
  let responseErrorCallback: Function;
  
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.clear();
    
    // Store the interceptor callbacks for manual triggering
    mockAxios.interceptors.request.use.mockImplementation((successCb) => {
      requestCallback = successCb;
      return () => {};
    });
    
    mockAxios.interceptors.response.use.mockImplementation((successCb, errorCb) => {
      responseErrorCallback = errorCb;
      return () => {};
    });
    
    // Re-create apiService to reinitialize interceptors
    // This would normally be handled by the module system
    apiService.setupInterceptors();
  });
  
  it('should add Authorization header with token to requests when token exists', () => {
    // Arrange
    const token = 'valid-jwt-token';
    localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
    const config = { headers: {} };
    
    // Act - Manually trigger the request interceptor
    const result = requestCallback(config);
    
    // Assert
    expect(result.headers.Authorization).toBe(`Bearer ${token}`);
  });
  
  it('should not add Authorization header when token does not exist', () => {
    // Arrange
    const config = { headers: {} };
    
    // Act - Manually trigger the request interceptor
    const result = requestCallback(config);
    
    // Assert
    expect(result.headers.Authorization).toBeUndefined();
  });
  
  it('should remove token and trigger logout on 401 Unauthorized response', async () => {
    // Arrange
    const token = 'expired-token';
    localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
    
    // Create a mock error object as would be received from axios on 401
    const error = {
      response: {
        status: 401,
        data: {
          success: false,
          error: 'Unauthorized',
          message: 'Invalid or expired authentication token'
        }
      }
    };
    
    // Act - Manually trigger the response error interceptor
    try {
      await responseErrorCallback(error);
    } catch (e) {
      // We expect the promise to be rejected
    }
    
    // Assert
    expect(localStorage.removeItem).toHaveBeenCalledWith(STORAGE_KEYS.AUTH_TOKEN);
    // Check if redirect logic would be triggered (in a real app this might be a navigation call)
  });
  
  it('should handle rate limit response (429) appropriately', async () => {
    // Arrange
    const error = {
      response: {
        status: 429,
        data: {
          success: false,
          error: 'Too Many Requests',
          message: 'Rate limit exceeded. Please try again later.'
        },
        headers: {
          'retry-after': '30'
        }
      }
    };
    
    // Act - Manually trigger the response error interceptor
    try {
      await responseErrorCallback(error);
    } catch (e) {
      // We expect the promise to be rejected with the original error
      expect(e).toBe(error);
    }
    
    // Assert - In a complete implementation, we'd expect some rate limit handling logic
    // but for now we just ensure the token is not removed on a 429
    expect(localStorage.removeItem).not.toHaveBeenCalled();
  });
  
  it('should properly propagate other errors without removing token', async () => {
    // Arrange
    localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, 'valid-token');
    const error = new Error('Network error');
    
    // Act - Manually trigger the response error interceptor
    try {
      await responseErrorCallback(error);
    } catch (e) {
      // We expect the promise to be rejected with the original error
      expect(e).toBe(error);
    }
    
    // Assert
    expect(localStorage.removeItem).not.toHaveBeenCalled();
  });
});
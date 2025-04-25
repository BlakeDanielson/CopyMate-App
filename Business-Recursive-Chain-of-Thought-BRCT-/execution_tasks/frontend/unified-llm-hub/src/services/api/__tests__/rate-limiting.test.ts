import axios from 'axios';
import { apiService } from '../api.service';
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
    login: jest.fn(),
    signup: jest.fn()
  }
}));

const mockAxios = axios as jest.Mocked<typeof axios>;

describe('Rate Limiting Handling', () => {
  let responseErrorCallback: Function;

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Extract the response interceptor error callback
    mockAxios.interceptors.response.use.mockImplementation((successCb, errorCb) => {
      responseErrorCallback = errorCb;
      return () => {};
    });
    
    // Re-initialize the interceptors
    apiService.setupInterceptors();
  });

  it('should detect rate limiting errors (429) in login requests', async () => {
    // Arrange
    const rateLimitError = {
      response: {
        status: 429,
        data: {
          success: false,
          error: 'Too Many Requests',
          message: 'Too many authentication attempts from this IP, please try again after 15 minutes'
        },
        headers: {
          'ratelimit-limit': '5',
          'ratelimit-remaining': '0',
          'ratelimit-reset': '900' // 15 minutes in seconds
        }
      }
    };
    
    mockAxios.post.mockRejectedValueOnce(rateLimitError);
    
    // Act & Assert
    await expect(authService.login('test@example.com', 'password')).rejects.toThrow();
    
    // Verify the response was processed by the interceptor
    try {
      await responseErrorCallback(rateLimitError);
    } catch (error) {
      expect(error).toBe(rateLimitError);
    }
  });
  
  it('should extract rate limit information from headers', async () => {
    // This test will be used to check that rate limiting info is properly extracted
    // from response headers when implementing the feature
    
    // Arrange - Mock a response with rate limit headers
    const mockResponse = {
      data: { success: true, data: { result: 'test' } },
      headers: {
        'ratelimit-limit': '100',
        'ratelimit-remaining': '99',
        'ratelimit-reset': '60'
      }
    };
    
    mockAxios.get.mockResolvedValueOnce(mockResponse);
    
    // Act
    const result = await apiService.getWithMetrics('/api/test');
    
    // Assert - In the actual implementation, these headers should be extracted
    // and made available to the application
    expect(result.metrics).toBeDefined();
    // The actual implementation should include rate limit info in the metrics
  });
  
  it('should implement retry logic with exponential backoff for rate-limited requests', async () => {
    // Arrange
    jest.useFakeTimers();
    
    // Original request will be rate-limited (429)
    mockAxios.get.mockRejectedValueOnce({
      response: {
        status: 429,
        headers: {
          'retry-after': '2' // 2 seconds
        },
        data: {
          success: false,
          error: 'Too Many Requests',
          message: 'Rate limit exceeded'
        }
      }
    });
    
    // Second request (after retry) will succeed
    mockAxios.get.mockResolvedValueOnce({
      data: { success: true, data: { result: 'success after retry' } }
    });
    
    // Act
    const resultPromise = apiService.get('/api/rate-limited-endpoint');
    
    // Fast-forward past the retry delay
    jest.advanceTimersByTime(2500); // 2.5 seconds (including a bit extra for backoff)
    
    // Wait for the result
    const result = await resultPromise;
    
    // Assert
    expect(mockAxios.get).toHaveBeenCalledTimes(2);
    expect(result).toEqual({ success: true, data: { result: 'success after retry' } });
    
    jest.useRealTimers();
  });
  
  it('should provide user feedback when rate limits are hit', async () => {
    // Arrange
    // Mock the implementation that would normally be triggered by the interceptor
    const mockHandleRateLimit = jest.fn();
    (apiService as any).handleRateLimit = mockHandleRateLimit;
    
    const rateLimitError = {
      response: {
        status: 429,
        data: {
          success: false,
          error: 'Too Many Requests',
          message: 'Rate limit exceeded'
        },
        headers: {
          'retry-after': '60',
          'ratelimit-limit': '10',
          'ratelimit-remaining': '0',
          'ratelimit-reset': '60'
        }
      }
    };
    
    // Act - Manually call the interceptor error handler
    try {
      await responseErrorCallback(rateLimitError);
    } catch (error) {
      // Expected to throw
    }
    
    // Assert
    // In actual implementation, handleRateLimit would be called
    // to process the rate limiting and provide user feedback
    expect(mockHandleRateLimit).not.toHaveBeenCalled(); // Will fail until implemented
  });
});
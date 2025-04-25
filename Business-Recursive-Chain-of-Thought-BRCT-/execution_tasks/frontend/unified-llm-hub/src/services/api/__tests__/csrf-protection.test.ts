import axios from 'axios';
import { apiService } from '../api.service';
import { API_BASE_URL } from '../../../config/constants';

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

const mockAxios = axios as jest.Mocked<typeof axios>;

describe('CSRF Protection in API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Reset the apiService instance to simulate a fresh startup
    // This is a bit hacky since we're working with a singleton, but necessary for testing
    (apiService as any).csrfToken = undefined;
  });
  
  it('should fetch CSRF token before making protected requests', async () => {
    // Mock the CSRF token endpoint response
    mockAxios.get.mockImplementationOnce((url) => {
      if (url.includes('/api/v1/csrf-token')) {
        return Promise.resolve({
          data: { csrfToken: 'test-csrf-token' }
        });
      }
      return Promise.reject(new Error('Unexpected URL'));
    });
    
    // Mock the actual API call response
    mockAxios.post.mockResolvedValueOnce({
      data: { success: true, data: { result: 'success' } }
    });
    
    // Make a request that should trigger CSRF token fetching
    await apiService.post('/api/v1/protected-endpoint', { test: 'data' });
    
    // Verify CSRF token was fetched
    expect(mockAxios.get).toHaveBeenCalledWith(`${API_BASE_URL}/api/v1/csrf-token`);
    
    // Verify the token was included in the subsequent request
    expect(mockAxios.post).toHaveBeenCalledWith(
      expect.any(String),
      { test: 'data' },
      expect.objectContaining({
        headers: expect.objectContaining({
          'X-CSRF-Token': 'test-csrf-token'
        })
      })
    );
  });
  
  it('should reuse cached CSRF token for multiple requests', async () => {
    // Mock the CSRF token endpoint response
    mockAxios.get.mockImplementationOnce(() => {
      return Promise.resolve({
        data: { csrfToken: 'test-csrf-token' }
      });
    });
    
    // Mock the actual API calls
    mockAxios.post.mockResolvedValue({
      data: { success: true, data: { result: 'success' } }
    });
    
    // Make first request that fetches the token
    await apiService.post('/api/v1/protected-endpoint', { test: 'first' });
    
    // Make second request that should reuse the token
    await apiService.post('/api/v1/protected-endpoint', { test: 'second' });
    
    // Verify CSRF token was fetched only once
    expect(mockAxios.get).toHaveBeenCalledTimes(1);
    
    // Verify both requests included the token
    expect(mockAxios.post).toHaveBeenCalledTimes(2);
    expect(mockAxios.post).toHaveBeenNthCalledWith(
      1,
      expect.any(String),
      { test: 'first' },
      expect.objectContaining({
        headers: expect.objectContaining({
          'X-CSRF-Token': 'test-csrf-token'
        })
      })
    );
    expect(mockAxios.post).toHaveBeenNthCalledWith(
      2,
      expect.any(String),
      { test: 'second' },
      expect.objectContaining({
        headers: expect.objectContaining({
          'X-CSRF-Token': 'test-csrf-token'
        })
      })
    );
  });
  
  it('should refresh CSRF token when a 403 Forbidden is received', async () => {
    // Mock the first CSRF token fetch
    mockAxios.get.mockImplementationOnce(() => {
      return Promise.resolve({
        data: { csrfToken: 'initial-csrf-token' }
      });
    });
    
    // Mock the first API call that fails with CSRF error
    mockAxios.post.mockImplementationOnce(() => {
      return Promise.reject({
        response: {
          status: 403,
          data: {
            success: false,
            error: 'Forbidden',
            message: 'Invalid CSRF token'
          }
        }
      });
    });
    
    // Mock the second CSRF token fetch after failure
    mockAxios.get.mockImplementationOnce(() => {
      return Promise.resolve({
        data: { csrfToken: 'new-csrf-token' }
      });
    });
    
    // Mock the retry of the API call that succeeds
    mockAxios.post.mockImplementationOnce(() => {
      return Promise.resolve({
        data: { success: true, data: { result: 'success after retry' } }
      });
    });
    
    // Make the request that will fail and then retry
    const result = await apiService.post('/api/v1/protected-endpoint', { test: 'data' });
    
    // Verify CSRF token was fetched twice (initial + refresh)
    expect(mockAxios.get).toHaveBeenCalledTimes(2);
    
    // Verify the API call was made twice (initial + retry)
    expect(mockAxios.post).toHaveBeenCalledTimes(2);
    
    // Verify the second API call used the new token
    expect(mockAxios.post).toHaveBeenNthCalledWith(
      2,
      expect.any(String),
      { test: 'data' },
      expect.objectContaining({
        headers: expect.objectContaining({
          'X-CSRF-Token': 'new-csrf-token'
        })
      })
    );
    
    // Verify the final result is from the successful retry
    expect(result).toEqual({ success: true, data: { result: 'success after retry' } });
  });
});
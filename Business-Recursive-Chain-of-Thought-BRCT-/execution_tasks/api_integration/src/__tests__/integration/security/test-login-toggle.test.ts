import request from 'supertest';
import express from 'express';
import { createAuthRoutes } from '../../../routes/auth.routes';
import { authService } from '../../../services/auth.service';

// Mock the auth service
jest.mock('../../../services/auth.service', () => ({
  authService: {
    signup: jest.fn(),
    login: jest.fn(),
    testLogin: jest.fn(),
    getUserById: jest.fn(),
    getUserMetrics: jest.fn()
  }
}));

describe('Test Login Environment Control Tests', () => {
  let app: express.Application;
  const originalNodeEnv = process.env.NODE_ENV;
  
  afterAll(() => {
    // Restore original NODE_ENV
    process.env.NODE_ENV = originalNodeEnv;
  });
  
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });
  
  it('should enable test login endpoint when NODE_ENV is not production', async () => {
    // Set NODE_ENV to development
    process.env.NODE_ENV = 'development';
    
    // Create a new Express app with fresh routes
    app = express();
    app.use(express.json());
    app.use('/api/v1/auth', createAuthRoutes());
    
    // Mock successful test login response
    (authService.testLogin as jest.Mock).mockResolvedValueOnce({
      accessToken: 'test-token'
    });
    
    // Act & Assert - Test login should be available
    const response = await request(app)
      .post('/api/v1/auth/test-login')
      .expect(200);
    
    expect(response.body).toHaveProperty('success', true);
    expect(response.body).toHaveProperty('data.accessToken', 'test-token');
    expect(authService.testLogin).toHaveBeenCalled();
  });
  
  it('should enable test login endpoint when NODE_ENV is test', async () => {
    // Set NODE_ENV to test
    process.env.NODE_ENV = 'test';
    
    // Create a new Express app with fresh routes
    app = express();
    app.use(express.json());
    app.use('/api/v1/auth', createAuthRoutes());
    
    // Mock successful test login response
    (authService.testLogin as jest.Mock).mockResolvedValueOnce({
      accessToken: 'test-token'
    });
    
    // Act & Assert - Test login should be available
    const response = await request(app)
      .post('/api/v1/auth/test-login')
      .expect(200);
    
    expect(response.body).toHaveProperty('success', true);
    expect(response.body).toHaveProperty('data.accessToken', 'test-token');
    expect(authService.testLogin).toHaveBeenCalled();
  });
  
  it('should disable test login endpoint when NODE_ENV is production', async () => {
    // Set NODE_ENV to production
    process.env.NODE_ENV = 'production';
    
    // Create a new Express app with fresh routes
    app = express();
    app.use(express.json());
    app.use('/api/v1/auth', createAuthRoutes());
    
    // Act & Assert - Test login should not be available (route doesn't exist)
    const response = await request(app)
      .post('/api/v1/auth/test-login')
      .expect(404);
    
    expect(authService.testLogin).not.toHaveBeenCalled();
  });
  
  it('should disable test login via service when ENABLE_TEST_AUTH is not set to true', async () => {
    // Set NODE_ENV to development but ENABLE_TEST_AUTH to undefined
    process.env.NODE_ENV = 'development';
    const originalEnableTestAuth = process.env.ENABLE_TEST_AUTH;
    process.env.ENABLE_TEST_AUTH = undefined;
    
    // Create a new Express app with fresh routes
    app = express();
    app.use(express.json());
    app.use('/api/v1/auth', createAuthRoutes());
    
    // Mock testLogin to throw an error
    (authService.testLogin as jest.Mock).mockRejectedValueOnce(
      new Error('Test login feature is disabled.')
    );
    
    // Act & Assert - Test login route exists but service rejects it
    const response = await request(app)
      .post('/api/v1/auth/test-login')
      .expect(400);
    
    expect(response.body).toHaveProperty('success', false);
    expect(response.body.message).toContain('Test login feature is disabled');
    
    // Restore ENABLE_TEST_AUTH
    process.env.ENABLE_TEST_AUTH = originalEnableTestAuth;
  });
});
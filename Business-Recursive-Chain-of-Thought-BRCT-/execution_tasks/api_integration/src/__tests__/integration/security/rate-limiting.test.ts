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

describe('Rate Limiting Tests', () => {
  let app: express.Application;

  beforeEach(() => {
    // Create a new Express app for each test
    app = express();
    app.use(express.json());
    app.use('/api/v1/auth', createAuthRoutes());
    
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  it('should include rate limit headers in the response', async () => {
    // Arrange
    const userData = {
      email: 'test@example.com',
      password: 'Password123!',
      confirmPassword: 'Password123!'
    };
    
    (authService.signup as jest.Mock).mockResolvedValueOnce({
      id: 'user-123',
      email: 'test@example.com',
      role: 'USER'
    });
    
    // Act & Assert
    const response = await request(app)
      .post('/api/v1/auth/signup')
      .send(userData)
      .expect(201);
    
    // Check for rate limit headers
    expect(response.headers).toHaveProperty('ratelimit-limit');
    expect(response.headers).toHaveProperty('ratelimit-remaining');
    expect(response.headers).toHaveProperty('ratelimit-reset');
  });

  it('should return 429 status after exceeding rate limit', async () => {
    // Arrange
    const userData = {
      email: 'test@example.com',
      password: 'Password123!',
      confirmPassword: 'Password123!'
    };
    
    (authService.signup as jest.Mock).mockResolvedValue({
      id: 'user-123',
      email: 'test@example.com',
      role: 'USER'
    });
    
    // Act & Assert
    // Make 5 requests (the limit)
    for (let i = 0; i < 5; i++) {
      await request(app)
        .post('/api/v1/auth/signup')
        .send(userData)
        .expect(201);
    }
    
    // The 6th request should be rate limited
    const response = await request(app)
      .post('/api/v1/auth/signup')
      .send(userData)
      .expect(429);
    
    expect(response.body).toHaveProperty('error', 'Too Many Requests');
    expect(response.body).toHaveProperty('message', expect.stringContaining('Too many authentication attempts'));
  });
});
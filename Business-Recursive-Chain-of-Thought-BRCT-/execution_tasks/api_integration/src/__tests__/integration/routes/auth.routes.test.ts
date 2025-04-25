import request from 'supertest';
import express from 'express';
import { createAuthRoutes } from '../../../routes/auth.routes';
import { authService } from '../../../services/auth.service';
import { Role } from '../../../generated/prisma';

// Mock the auth service
jest.mock('../../../services/auth.service', () => ({
  authService: {
    signup: jest.fn(),
    register: jest.fn(),
    login: jest.fn(),
    testLogin: jest.fn(),
    getUserById: jest.fn(),
    getUserMetrics: jest.fn()
  }
}));

describe('Auth Routes Integration Tests', () => {
  let app: express.Application;

  beforeEach(() => {
    // Create a new Express app for each test
    app = express();
    app.use(express.json());
    app.use('/api/v1/auth', createAuthRoutes());
    
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  describe('POST /api/v1/auth/signup', () => {
    it('should return 201 and created user data on successful signup', async () => {
      // Arrange
      const userData = {
        email: 'test@example.com',
        password: 'Password123!',
        confirmPassword: 'Password123!'
      };
      
      const mockUserResponse = {
        id: 'user-123',
        email: 'test@example.com',
        username: null,
        fullName: null,
        role: Role.USER,
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      (authService.signup as jest.Mock).mockResolvedValueOnce(mockUserResponse);
      
      // Act & Assert
      const response = await request(app)
        .post('/api/v1/auth/signup')
        .send(userData)
        .expect(201);
      
      // Assert response shape and content
      expect(response.body).toEqual({
        success: true,
        data: expect.objectContaining({
          id: 'user-123',
          email: 'test@example.com',
          role: Role.USER
        }),
        message: 'User signed up successfully'
      });
      
      // Assert service was called with correct parameters
      expect(authService.signup).toHaveBeenCalledWith(userData);
      
      // Verify password hash is not returned in response
      expect(response.body.data).not.toHaveProperty('passwordHash');
    });
    
    it('should return 400 when required fields are missing', async () => {
      // Arrange
      const incompleteUserData = {
        email: 'test@example.com'
        // Missing password and confirmPassword
      };
      
      // Act & Assert
      const response = await request(app)
        .post('/api/v1/auth/signup')
        .send(incompleteUserData)
        .expect(400);
      
      expect(response.body).toEqual({
        success: false,
        error: 'Bad Request',
        message: 'Email, password, and confirm password are required'
      });
      
      // Verify service was not called
      expect(authService.signup).not.toHaveBeenCalled();
    });
    
    it('should return 400 when passwords do not match', async () => {
      // Arrange
      const userData = {
        email: 'test@example.com',
        password: 'Password123!',
        confirmPassword: 'DifferentPassword123!'
      };
      
      // Act & Assert
      const response = await request(app)
        .post('/api/v1/auth/signup')
        .send(userData)
        .expect(400);
      
      expect(response.body).toEqual({
        success: false,
        error: 'Bad Request',
        message: 'Passwords do not match'
      });
      
      // Verify service was not called
      expect(authService.signup).not.toHaveBeenCalled();
    });
    
    it('should return 409 when email already exists', async () => {
      // Arrange
      const userData = {
        email: 'existing@example.com',
        password: 'Password123!',
        confirmPassword: 'Password123!'
      };
      
      // Mock the service to throw an error
      (authService.signup as jest.Mock).mockRejectedValueOnce(
        new Error('Email already exists')
      );
      
      // Act & Assert
      const response = await request(app)
        .post('/api/v1/auth/signup')
        .send(userData)
        .expect(409);
      
      expect(response.body).toEqual({
        success: false,
        error: 'Conflict',
        message: 'An account with this email address already exists.'
      });
      
      // Verify service was called with correct parameters
      expect(authService.signup).toHaveBeenCalledWith(userData);
    });
    
    it('should return 400 when email format is invalid', async () => {
      // Arrange
      const userData = {
        email: 'invalid-email',
        password: 'Password123!',
        confirmPassword: 'Password123!'
      };
      
      // Mock the service to throw an error
      (authService.signup as jest.Mock).mockRejectedValueOnce(
        new Error('Invalid email format')
      );
      
      // Act & Assert
      const response = await request(app)
        .post('/api/v1/auth/signup')
        .send(userData)
        .expect(400);
      
      expect(response.body).toEqual({
        success: false,
        error: 'Bad Request',
        message: 'Invalid email format'
      });
      
      // Verify service was called with correct parameters
      expect(authService.signup).toHaveBeenCalledWith(userData);
    });
    
    it('should return 400 when password validation fails', async () => {
      // Arrange
      const userData = {
        email: 'test@example.com',
        password: 'weak',
        confirmPassword: 'weak'
      };
      
      // Mock the service to throw an error
      (authService.signup as jest.Mock).mockRejectedValueOnce(
        new Error('Password validation failed: Password must be at least 8 characters long.')
      );
      
      // Act & Assert
      const response = await request(app)
        .post('/api/v1/auth/signup')
        .send(userData)
        .expect(400);
      
      expect(response.body).toEqual({
        success: false,
        error: 'Bad Request',
        message: 'Password validation failed: Password must be at least 8 characters long.'
      });
      
      // Verify service was called with correct parameters
      expect(authService.signup).toHaveBeenCalledWith(userData);
    });
    
    it('should return 500 on unexpected server error', async () => {
      // Arrange
      const userData = {
        email: 'test@example.com',
        password: 'Password123!',
        confirmPassword: 'Password123!'
      };
      
      // Mock an unexpected error
      (authService.signup as jest.Mock).mockRejectedValueOnce(
        new Error('Database connection error')
      );
      
      // Mock NODE_ENV for consistent error message
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'test';
      
      // Act & Assert
      const response = await request(app)
        .post('/api/v1/auth/signup')
        .send(userData)
        .expect(500);
      
      expect(response.body).toEqual({
        success: false,
        error: 'Internal Server Error',
        message: 'Database connection error' // In test mode we show the actual error
      });
      
      // Restore original NODE_ENV
      process.env.NODE_ENV = originalEnv;
      
      // Verify service was called with correct parameters
      expect(authService.signup).toHaveBeenCalledWith(userData);
    });
  });
});
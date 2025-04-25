import { Request, Response } from 'express';
import { authController } from '../../../controllers/auth.controller';
import { authService } from '../../../services/auth.service';
import { Role } from '../../../generated/prisma';
import { createMockRequest, createMockResponse, createSignUpData, createMockPrismaUser } from '../../utils/test-helpers';

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

describe('AuthController', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('signup', () => {
    it('should return 400 if required fields are missing', async () => {
      // Arrange
      const req = createMockRequest({
        body: {
          email: 'test@example.com',
          // missing password and confirmPassword
        }
      }) as Request;
      const res = createMockResponse() as unknown as Response;

      // Act
      await authController.signup(req, res);

      // Assert
      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          success: false,
          error: 'Bad Request',
          message: 'Email, password, and confirm password are required'
        })
      );
      expect(authService.signup).not.toHaveBeenCalled();
    });

    it('should return 400 if passwords do not match', async () => {
      // Arrange
      const req = createMockRequest({
        body: {
          email: 'test@example.com',
          password: 'Password123!',
          confirmPassword: 'DifferentPassword123!'
        }
      }) as Request;
      const res = createMockResponse() as unknown as Response;

      // Act
      await authController.signup(req, res);

      // Assert
      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          success: false,
          error: 'Bad Request',
          message: 'Passwords do not match'
        })
      );
      expect(authService.signup).not.toHaveBeenCalled();
    });

    it('should return 201 and user data on successful signup', async () => {
      // Arrange
      const signUpData = createSignUpData();
      const req = createMockRequest({ body: signUpData }) as Request;
      const res = createMockResponse() as unknown as Response;

      const mockUser = createMockPrismaUser({
        email: signUpData.email,
        id: 'new-user-id'
      });

      // Remove passwordHash property since it's filtered out for response
      const { passwordHash, ...userWithoutPassword } = mockUser;

      // Mock the service response
      (authService.signup as jest.Mock).mockResolvedValueOnce(userWithoutPassword);

      // Act
      await authController.signup(req, res);

      // Assert
      expect(authService.signup).toHaveBeenCalledWith(signUpData);
      expect(res.status).toHaveBeenCalledWith(201);
      expect(res.json).toHaveBeenCalledWith({
        success: true,
        data: userWithoutPassword,
        message: 'User signed up successfully'
      });
    });

    it('should return 409 if email already exists', async () => {
      // Arrange
      const signUpData = createSignUpData();
      const req = createMockRequest({ body: signUpData }) as Request;
      const res = createMockResponse() as unknown as Response;

      // Mock the service to throw an 'Email already exists' error
      (authService.signup as jest.Mock).mockRejectedValueOnce(
        new Error('Email already exists')
      );

      // Act
      await authController.signup(req, res);

      // Assert
      expect(authService.signup).toHaveBeenCalledWith(signUpData);
      expect(res.status).toHaveBeenCalledWith(409);
      expect(res.json).toHaveBeenCalledWith({
        success: false,
        error: 'Conflict',
        message: 'An account with this email address already exists.'
      });
    });

    it('should return 400 if password validation fails', async () => {
      // Arrange
      const signUpData = createSignUpData({
        password: 'weak',
        confirmPassword: 'weak'
      });
      const req = createMockRequest({ body: signUpData }) as Request;
      const res = createMockResponse() as unknown as Response;

      // Mock the service to throw a password validation error
      (authService.signup as jest.Mock).mockRejectedValueOnce(
        new Error('Password validation failed: Password must be at least 8 characters long.')
      );

      // Act
      await authController.signup(req, res);

      // Assert
      expect(authService.signup).toHaveBeenCalledWith(signUpData);
      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith({
        success: false,
        error: 'Bad Request',
        message: 'Password validation failed: Password must be at least 8 characters long.'
      });
    });

    it('should return 400 if email format is invalid', async () => {
      // Arrange
      const signUpData = createSignUpData({
        email: 'invalid-email'
      });
      const req = createMockRequest({ body: signUpData }) as Request;
      const res = createMockResponse() as unknown as Response;

      // Mock the service to throw an email validation error
      (authService.signup as jest.Mock).mockRejectedValueOnce(
        new Error('Invalid email format')
      );

      // Act
      await authController.signup(req, res);

      // Assert
      expect(authService.signup).toHaveBeenCalledWith(signUpData);
      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith({
        success: false,
        error: 'Bad Request',
        message: 'Invalid email format'
      });
    });

    it('should return 500 on unexpected error', async () => {
      // Arrange
      const signUpData = createSignUpData();
      const req = createMockRequest({ body: signUpData }) as Request;
      const res = createMockResponse() as unknown as Response;

      // Mock the service to throw an unexpected error
      const internalError = new Error('Database connection error');
      (authService.signup as jest.Mock).mockRejectedValueOnce(internalError);

      // Set NODE_ENV to development to test error message behavior
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      // Act
      await authController.signup(req, res);

      // Assert
      expect(authService.signup).toHaveBeenCalledWith(signUpData);
      expect(res.status).toHaveBeenCalledWith(500);
      expect(res.json).toHaveBeenCalledWith({
        success: false,
        error: 'Internal Server Error',
        message: 'Database connection error' // In development mode, we show the actual error
      });

      // Restore NODE_ENV
      process.env.NODE_ENV = originalEnv;
    });

    it('should hide detailed error message in production mode', async () => {
      // Arrange
      const signUpData = createSignUpData();
      const req = createMockRequest({ body: signUpData }) as Request;
      const res = createMockResponse() as unknown as Response;

      // Mock the service to throw an unexpected error
      const internalError = new Error('Database connection details that should be hidden');
      (authService.signup as jest.Mock).mockRejectedValueOnce(internalError);

      // Set NODE_ENV to production
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      // Act
      await authController.signup(req, res);

      // Assert
      expect(authService.signup).toHaveBeenCalledWith(signUpData);
      expect(res.status).toHaveBeenCalledWith(500);
      expect(res.json).toHaveBeenCalledWith({
        success: false,
        error: 'Internal Server Error',
        message: 'An error occurred during sign-up' // Generic message in production
      });

      // Restore NODE_ENV
      process.env.NODE_ENV = originalEnv;
    });
  });
});
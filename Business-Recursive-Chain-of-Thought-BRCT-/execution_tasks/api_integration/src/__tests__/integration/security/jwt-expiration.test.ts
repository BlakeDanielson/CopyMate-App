import jwt from 'jsonwebtoken';
import { Role } from '../../../generated/prisma';
import { authService } from '../../../services/auth.service';
import { setupTestEnv, createMockRequest, createMockResponse } from '../../utils/test-helpers';
import { authMiddleware } from '../../../middleware/auth.middleware';

// Mock jwt
jest.mock('jsonwebtoken', () => ({
  sign: jest.fn(),
  verify: jest.fn()
}));

describe('JWT Expiration Tests', () => {
  // Set up test environment with JWT settings
  const { cleanup } = setupTestEnv();
  
  afterAll(() => {
    cleanup();
  });
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should generate tokens with 1 hour expiration', () => {
    // Use reflection to access the private generateToken method
    // This is necessary for testing a private method
    const generateToken = (authService as any).generateToken.bind(authService);
    
    // Mock the jwt.sign method to capture the payload
    (jwt.sign as jest.Mock).mockImplementation((payload) => {
      return 'mock-token';
    });
    
    // Create a mock user
    const mockUser = {
      id: 'test-user-id',
      email: 'test@example.com',
      role: Role.USER
    };
    
    // Call the generateToken method
    generateToken(mockUser);
    
    // Get the payload passed to jwt.sign
    const capturedPayload = (jwt.sign as jest.Mock).mock.calls[0][0];
    
    // Verify the expiration is set properly
    expect(capturedPayload).toHaveProperty('exp');
    expect(capturedPayload).toHaveProperty('iat');
    
    // Verify the expiration is 1 hour (3600 seconds) after the issued at time
    const expDiff = capturedPayload.exp - capturedPayload.iat;
    expect(expDiff).toBe(3600);
  });

  it('should reject expired tokens in authMiddleware', () => {
    // Mock an expired token verification
    (jwt.verify as jest.Mock).mockImplementation(() => {
      throw new Error('jwt expired');
    });
    
    // Create mock request and response
    const req = createMockRequest({
      headers: {
        authorization: 'Bearer expired-token'
      }
    });
    const res = createMockResponse();
    const next = jest.fn();
    
    // Call the middleware
    authMiddleware(req, res, next);
    
    // Verify the middleware rejected the request
    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
      success: false,
      error: 'Unauthorized',
      message: 'Invalid or expired authentication token'
    }));
    expect(next).not.toHaveBeenCalled();
  });

  it('should accept valid, non-expired tokens in authMiddleware', () => {
    // Mock a valid token verification
    const decodedToken = {
      userId: 'test-user-id',
      email: 'test@example.com',
      role: Role.USER,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 3600 // 1 hour in the future
    };
    
    (jwt.verify as jest.Mock).mockImplementation(() => decodedToken);
    
    // Create mock request and response
    const req = createMockRequest({
      headers: {
        authorization: 'Bearer valid-token'
      }
    });
    const res = createMockResponse();
    const next = jest.fn();
    
    // Call the middleware
    authMiddleware(req, res, next);
    
    // Verify the middleware accepted the request
    expect(next).toHaveBeenCalled();
    expect(req.user).toEqual({
      id: decodedToken.userId,
      email: decodedToken.email,
      role: decodedToken.role
    });
  });
});
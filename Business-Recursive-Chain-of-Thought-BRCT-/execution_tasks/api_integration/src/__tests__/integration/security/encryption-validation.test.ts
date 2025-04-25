import { authService } from '../../../services/auth.service';
import { Role } from '../../../generated/prisma';

describe('Encryption and Secret Validation Tests', () => {
  const originalNodeEnv = process.env.NODE_ENV;
  const originalJwtSecret = process.env.JWT_SECRET;
  
  afterEach(() => {
    // Restore environment variables after each test
    process.env.NODE_ENV = originalNodeEnv;
    process.env.JWT_SECRET = originalJwtSecret;
  });

  it('should throw an error when generating a token with missing JWT_SECRET', () => {
    // Arrange
    process.env.JWT_SECRET = '';
    
    // Create a mock user
    const mockUser = {
      id: 'test-user-id',
      email: 'test@example.com',
      passwordHash: 'hashed-password',
      username: null,
      fullName: null,
      role: Role.USER,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    
    // Access the private generateToken method using type assertion
    const generateToken = (authService as any).generateToken.bind(authService);
    
    // Act & Assert
    expect(() => generateToken(mockUser)).toThrow('JWT secret configuration error');
  });
  
  it('should throw an error when generating a token with JWT_SECRET that is too short', () => {
    // Arrange
    process.env.JWT_SECRET = 'short-secret'; // Less than 32 characters
    
    // Create a mock user
    const mockUser = {
      id: 'test-user-id',
      email: 'test@example.com',
      passwordHash: 'hashed-password',
      username: null,
      fullName: null,
      role: Role.USER,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    
    // Access the private generateToken method using type assertion
    const generateToken = (authService as any).generateToken.bind(authService);
    
    // Act & Assert
    expect(() => generateToken(mockUser)).toThrow('JWT secret configuration error');
  });
  
  it('should successfully generate a token with proper JWT_SECRET', () => {
    // Arrange
    process.env.JWT_SECRET = 'this-is-a-secure-secret-with-sufficient-length'; // More than 32 characters
    
    // Create a mock user
    const mockUser = {
      id: 'test-user-id',
      email: 'test@example.com',
      passwordHash: 'hashed-password',
      username: null,
      fullName: null,
      role: Role.USER,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    
    // Access the private generateToken method using type assertion
    const generateToken = (authService as any).generateToken.bind(authService);
    
    // Act & Assert - Should not throw an error
    expect(() => generateToken(mockUser)).not.toThrow();
    
    const token = generateToken(mockUser);
    expect(typeof token).toBe('string');
    expect(token.length).toBeGreaterThan(0);
  });
  
  it('should handle verifyToken gracefully when JWT_SECRET is invalid', () => {
    // Arrange
    process.env.JWT_SECRET = 'different-secret-than-what-was-used-to-generate-token';
    
    // Act & Assert
    expect(() => {
      authService.verifyToken('some-invalid-token');
    }).toThrow('Invalid token');
  });
});
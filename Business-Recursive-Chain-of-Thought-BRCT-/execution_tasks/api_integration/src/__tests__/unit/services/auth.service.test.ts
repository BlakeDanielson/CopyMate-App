import bcrypt from 'bcrypt';
import { PrismaClient, User as PrismaUser, Role } from '../../../generated/prisma';
import { authService } from '../../../services/auth.service';
import { SignUpUserInput } from '../../../types/auth';

// Mock Prisma client
jest.mock('../../../lib/prisma', () => ({
  prisma: {
    user: {
      findUnique: jest.fn(),
      create: jest.fn(),
    },
  },
}));

// Import the mocked Prisma client
import { prisma } from '../../../lib/prisma';

// Mock bcrypt
jest.mock('bcrypt', () => ({
  hash: jest.fn().mockResolvedValue('hashedPassword'),
  compare: jest.fn(),
}));

describe('AuthService - Signup', () => {
  const mockPrisma = prisma as jest.Mocked<PrismaClient>;
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  describe('signup method', () => {
    it('should throw an error if password and confirmPassword do not match', async () => {
      // Arrange
      const userData: SignUpUserInput = {
        email: 'test@example.com',
        password: 'Password123!',
        confirmPassword: 'DifferentPassword123!'
      };
      
      // Act & Assert
      await expect(authService.signup(userData)).rejects.toThrow('Passwords do not match');
      expect(mockPrisma.user.findUnique).not.toHaveBeenCalled();
      expect(mockPrisma.user.create).not.toHaveBeenCalled();
    });
    
    it('should throw an error if email format is invalid', async () => {
      // Arrange
      const userData: SignUpUserInput = {
        email: 'invalid-email',
        password: 'Password123!',
        confirmPassword: 'Password123!'
      };
      
      // Act & Assert
      await expect(authService.signup(userData)).rejects.toThrow('Invalid email format');
      expect(mockPrisma.user.findUnique).not.toHaveBeenCalled();
      expect(mockPrisma.user.create).not.toHaveBeenCalled();
    });
    
    it('should throw an error if password is less than 8 characters', async () => {
      // Arrange
      const userData: SignUpUserInput = {
        email: 'test@example.com',
        password: 'Pass1!',
        confirmPassword: 'Pass1!'
      };
      
      // Act & Assert
      await expect(authService.signup(userData)).rejects.toThrow(/Password validation failed/);
      expect(mockPrisma.user.findUnique).not.toHaveBeenCalled();
      expect(mockPrisma.user.create).not.toHaveBeenCalled();
    });
    
    it('should throw an error if password does not include uppercase letter', async () => {
      // Arrange
      const userData: SignUpUserInput = {
        email: 'test@example.com',
        password: 'password123!',
        confirmPassword: 'password123!'
      };
      
      // Act & Assert
      await expect(authService.signup(userData)).rejects.toThrow(/Password validation failed/);
      expect(mockPrisma.user.findUnique).not.toHaveBeenCalled();
      expect(mockPrisma.user.create).not.toHaveBeenCalled();
    });
    
    it('should throw an error if password does not include lowercase letter', async () => {
      // Arrange
      const userData: SignUpUserInput = {
        email: 'test@example.com',
        password: 'PASSWORD123!',
        confirmPassword: 'PASSWORD123!'
      };
      
      // Act & Assert
      await expect(authService.signup(userData)).rejects.toThrow(/Password validation failed/);
      expect(mockPrisma.user.findUnique).not.toHaveBeenCalled();
      expect(mockPrisma.user.create).not.toHaveBeenCalled();
    });
    
    it('should throw an error if password does not include number', async () => {
      // Arrange
      const userData: SignUpUserInput = {
        email: 'test@example.com',
        password: 'Password!',
        confirmPassword: 'Password!'
      };
      
      // Act & Assert
      await expect(authService.signup(userData)).rejects.toThrow(/Password validation failed/);
      expect(mockPrisma.user.findUnique).not.toHaveBeenCalled();
      expect(mockPrisma.user.create).not.toHaveBeenCalled();
    });
    
    it('should throw an error if password does not include special character', async () => {
      // Arrange
      const userData: SignUpUserInput = {
        email: 'test@example.com',
        password: 'Password123',
        confirmPassword: 'Password123'
      };
      
      // Act & Assert
      await expect(authService.signup(userData)).rejects.toThrow(/Password validation failed/);
      expect(mockPrisma.user.findUnique).not.toHaveBeenCalled();
      expect(mockPrisma.user.create).not.toHaveBeenCalled();
    });
    
    it('should throw an error if email already exists', async () => {
      // Arrange
      const userData: SignUpUserInput = {
        email: 'existing@example.com',
        password: 'Password123!',
        confirmPassword: 'Password123!'
      };
      
      mockPrisma.user.findUnique.mockResolvedValueOnce({
        id: 'existing-id',
        email: 'existing@example.com',
        passwordHash: 'hashedPassword',
        role: Role.USER,
        createdAt: new Date(),
        updatedAt: new Date(),
      } as PrismaUser);
      
      // Act & Assert
      await expect(authService.signup(userData)).rejects.toThrow('Email already exists');
      expect(mockPrisma.user.findUnique).toHaveBeenCalledWith({
        where: { email: userData.email }
      });
      expect(mockPrisma.user.create).not.toHaveBeenCalled();
    });
    
    it('should create a new user successfully with valid input', async () => {
      // Arrange
      const userData: SignUpUserInput = {
        email: 'valid@example.com',
        password: 'ValidPassword123!',
        confirmPassword: 'ValidPassword123!'
      };
      
      const mockCreatedUser = {
        id: 'new-user-id',
        email: userData.email,
        passwordHash: 'hashedPassword',
        username: null,
        fullName: null,
        role: Role.USER,
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      
      mockPrisma.user.findUnique.mockResolvedValueOnce(null);
      mockPrisma.user.create.mockResolvedValueOnce(mockCreatedUser as PrismaUser);
      
      // Act
      const result = await authService.signup(userData);
      
      // Assert
      expect(mockPrisma.user.findUnique).toHaveBeenCalledWith({
        where: { email: userData.email }
      });
      expect(bcrypt.hash).toHaveBeenCalledWith(userData.password, expect.any(Number));
      expect(mockPrisma.user.create).toHaveBeenCalledWith({
        data: {
          email: userData.email,
          passwordHash: 'hashedPassword',
          role: Role.USER,
          username: null,
          fullName: null,
        }
      });
      
      // Check that the returned user doesn't contain passwordHash
      expect(result).toEqual({
        id: 'new-user-id',
        email: userData.email,
        username: null,
        fullName: null,
        role: Role.USER,
        createdAt: expect.any(Date),
        updatedAt: expect.any(Date),
      });
      expect(result).not.toHaveProperty('passwordHash');
    });
  });
});
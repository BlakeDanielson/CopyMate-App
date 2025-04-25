/**
 * Test Utilities and Helpers
 * Provides common testing utilities and mock factories for tests
 */

import { PrismaClient, User as PrismaUser, Role } from '../../generated/prisma';

/**
 * Creates a mock Prisma User object for testing
 */
export function createMockPrismaUser(overrides: Partial<PrismaUser> = {}): PrismaUser {
  const defaultUser: PrismaUser = {
    id: 'test-user-id',
    email: 'test@example.com',
    passwordHash: 'hashed-password',
    username: null,
    fullName: null,
    role: Role.USER,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  return {
    ...defaultUser,
    ...overrides,
  };
}

/**
 * Creates a SignUpUserInput object for testing
 */
export function createSignUpData(overrides: Record<string, any> = {}) {
  const defaultData = {
    email: 'test@example.com',
    password: 'ValidPassword123!',
    confirmPassword: 'ValidPassword123!',
  };

  return {
    ...defaultData,
    ...overrides,
  };
}

/**
 * Sets up a test environment with a mocked JWT secret
 */
export function setupTestEnv() {
  // Store original environment variables
  const originalEnv = { ...process.env };
  
  // Set test environment variables
  process.env.JWT_SECRET = 'test-jwt-secret';
  process.env.JWT_EXPIRES_IN = '1h';
  process.env.NODE_ENV = 'test';
  
  return {
    // Restore original environment
    cleanup: () => {
      process.env = originalEnv;
    }
  };
}

/**
 * Create a mock Express request object
 */
export function createMockRequest(overrides: Record<string, any> = {}) {
  const req: Record<string, any> = {
    body: {},
    params: {},
    query: {},
    headers: {},
    user: null,
    ...overrides
  };
  
  return req;
}

/**
 * Create a mock Express response object
 */
export function createMockResponse() {
  const res: Record<string, any> = {};
  
  // Create mock functions for response methods
  res.status = jest.fn().mockReturnValue(res);
  res.json = jest.fn().mockReturnValue(res);
  res.send = jest.fn().mockReturnValue(res);
  
  return res;
}
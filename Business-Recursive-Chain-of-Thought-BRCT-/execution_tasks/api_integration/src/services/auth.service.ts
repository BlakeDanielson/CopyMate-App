/**
 * Authentication service
 * Handles user registration, login, JWT operations, and user management
 */

import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { prisma } from '../lib/prisma';
import { User as PrismaUser, Role } from '../generated/prisma'; // Import Role and aliased User from generated client
import {
  // User, // Removed local User import
  UserWithoutPassword,
  RegisterUserInput,
  LoginUserInput,
  SignUpUserInput, // Added SignUpUserInput
  AuthTokens,
  TokenDecoded,
  UserMetrics,
  // Role // Removed from here
} from '../types/auth';
import { MessageRole } from '../types/conversation'; // Assuming this is correct

export class AuthService {
  private readonly JWT_SECRET: string;
  // private readonly JWT_EXPIRES_IN: string; // Removed, expiration is now in payload
  private readonly SALT_ROUNDS = 10;

  constructor() {
    // Load environment variables
    // JWT_SECRET is validated at startup (app.ts) and before use (generateToken)
    this.JWT_SECRET = process.env.JWT_SECRET || '';
    // this.JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '8h'; // Removed

    // Basic check removed, more robust check added in generateToken and app.ts
    // if (!this.JWT_SECRET) {
    //   console.error('JWT_SECRET environment variable is not set!');
    // }
  }

  /**
   * Register a new user
   */
  async register(userData: RegisterUserInput): Promise<UserWithoutPassword> {
    try {
      // Check if user already exists
      const existingUser = await prisma.user.findUnique({
        where: { email: userData.email }
      });

      if (existingUser) {
        throw new Error('User already exists with this email');
      }

      // Hash the password
      const passwordHash = await bcrypt.hash(userData.password, this.SALT_ROUNDS);

      // Create user in database
      const user = await prisma.user.create({
        data: {
          email: userData.email,
          passwordHash,
          username: userData.username || null,
          fullName: userData.fullName || null,
          role: Role.USER // Use Prisma enum
        }
      });

      // Return user without password hash
      const { passwordHash: _, ...userWithoutPassword } = user;
      return userWithoutPassword as UserWithoutPassword;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  /**
   * Login a user
   */
  async login(credentials: LoginUserInput): Promise<AuthTokens> {
    try {
      // Find user by email
      const user = await prisma.user.findUnique({
        where: { email: credentials.email }
      });

      if (!user) {
        throw new Error('Invalid email or password');
      }

      // Verify password
      const passwordValid = await bcrypt.compare(credentials.password, user.passwordHash);
      if (!passwordValid) {
        throw new Error('Invalid email or password');
      }

      // Generate JWT token
      const accessToken = this.generateToken(user);

      return { accessToken };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  /**
   * Login a test user (bypasses password check) - ONLY FOR DEVELOPMENT/TESTING
   * No database connection required for this test function
   */
  async testLogin(): Promise<AuthTokens> {
    if (process.env.ENABLE_TEST_AUTH !== 'true') {
      throw new Error('Test login feature is disabled.');
    }

    try {
      console.log('Using database-independent test login...');
      
      // Create a mock test user without database access
      const mockTestUser = {
        id: 'test-user-id-123456789',
        email: 'test@example.com',
        passwordHash: 'not-used-for-test-login',
        username: 'Test User',
        fullName: 'Test User Account',
        role: Role.USER,
        createdAt: new Date(),
        updatedAt: new Date()
      } as PrismaUser;

      // Generate JWT token for the mock test user
      const accessToken = this.generateToken(mockTestUser);
      console.log(`Generated test token for test@example.com`);

      return { accessToken };
    } catch (error) {
      console.error('Test login error:', error);
      throw error; // Re-throw the error to be handled by the controller
    }
  }
/**
   * Sign up a new user
   */
  async signup(userData: SignUpUserInput): Promise<UserWithoutPassword> {
    try {
      const { email, password, confirmPassword } = userData;

      // 1. Validate Input
      if (password !== confirmPassword) {
        // This check is also in the controller, but good practice to have it here too.
        throw new Error('Passwords do not match'); // Should ideally not be reached if controller validation works
      }

      // Email format validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        throw new Error('Invalid email format');
      }

      // Password complexity validation
      const passwordErrors: string[] = [];
      if (password.length < 8) {
        passwordErrors.push('Password must be at least 8 characters long.');
      }
      if (!/[A-Z]/.test(password)) {
        passwordErrors.push('Password must include at least one uppercase letter.');
      }
      if (!/[a-z]/.test(password)) {
        passwordErrors.push('Password must include at least one lowercase letter.');
      }
      if (!/[0-9]/.test(password)) {
        passwordErrors.push('Password must include at least one number.');
      }
      if (!/[!@#$%^&*]/.test(password)) {
        passwordErrors.push('Password must include at least one special character (!@#$%^&*).');
      }

      if (passwordErrors.length > 0) {
        throw new Error(`Password validation failed: ${passwordErrors.join(' ')}`);
      }

      // 2. Check if user already exists
      const existingUser = await prisma.user.findUnique({
        where: { email: email }
      });

      if (existingUser) {
        throw new Error('Email already exists');
      }

      // 3. Hash the password
      const passwordHash = await bcrypt.hash(password, this.SALT_ROUNDS);

      // 4. Create user in database
      // Assign default role USER
      const user = await prisma.user.create({
        data: {
          email: email,
          passwordHash,
          role: Role.USER, // Assign default role
          // Add default values or nulls for other optional fields if needed
          username: null,
          fullName: null,
        }
      });

      // 5. Return user without password hash
      const { passwordHash: _, ...userWithoutPassword } = user;
      return userWithoutPassword as UserWithoutPassword;

    } catch (error) {
      console.error('Signup service error:', error);
      // Re-throw the error to be handled by the controller
      // Specific error messages are thrown within the try block for validation/existence checks
      throw error;
    }
  }


  /**
   * Get user by ID
   */
  async getUserById(id: string): Promise<UserWithoutPassword | null> {
    try {
      // Special handling for test user
      if (id === 'test-user-id-123456789' && process.env.ENABLE_TEST_AUTH === 'true') {
        console.log('Using mock test user profile without database access');
        
        // Return a mock test user without querying the database
        return {
          id: 'test-user-id-123456789',
          email: 'test@example.com',
          username: 'Test User',
          fullName: 'Test User Account',
          role: Role.USER,
          createdAt: new Date(),
          updatedAt: new Date()
        } as UserWithoutPassword;
      }
      
      // Regular database lookup for non-test users
      const user = await prisma.user.findUnique({
        where: { id }
      });

      if (!user) return null;

      // Return user without password hash
      const { passwordHash: _, ...userWithoutPassword } = user;
      return userWithoutPassword as UserWithoutPassword;
    } catch (error) {
      console.error('Get user error:', error);
      throw error;
    }
  }

  /**
   * Generate JWT token
   */
  // Update parameter type to use PrismaUser
  private generateToken(user: PrismaUser): string {
    // Validate JWT_SECRET before attempting to sign
    if (!this.JWT_SECRET || this.JWT_SECRET.length < 32) {
      console.error('FATAL: JWT_SECRET is missing or too short (min 32 chars). Cannot generate token.');
      // Throwing an error here prevents token generation with an insecure secret.
      // The application should ideally not reach this point due to startup checks in app.ts.
      throw new Error('JWT secret configuration error.');
    }

    const nowSeconds = Math.floor(Date.now() / 1000);
    const expirationSeconds = 60 * 60; // 1 hour

    const payload = {
      userId: user.id,
      email: user.email,
      role: user.role,
      iat: nowSeconds, // Issued at timestamp (seconds since epoch)
      exp: nowSeconds + expirationSeconds // Expiration timestamp (seconds since epoch)
    };

    // Sign the token with the secret and payload including expiration
    // No need for expiresIn option here as 'exp' is in the payload
    return jwt.sign(payload, this.JWT_SECRET);
  }

  /**
   * Verify JWT token
   */
  verifyToken(token: string): TokenDecoded {
    try {
      return jwt.verify(token, this.JWT_SECRET) as TokenDecoded;
    } catch (error) {
      throw new Error('Invalid token');
    }
  }

  /**
   * Get usage metrics for a user
   */
  async getUserMetrics(userId: string): Promise<UserMetrics> {
    try {
      // Special handling for test user
      if (userId === 'test-user-id-123456789' && process.env.ENABLE_TEST_AUTH === 'true') {
        console.log('Using mock metrics for test user without database access');
        
        // Calculate the current billing period (start of current month to end of month)
        const now = new Date();
        const billingPeriodStart = new Date(now.getFullYear(), now.getMonth(), 1);
        const billingPeriodEnd = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59, 999);
        
        // Return mock metrics for test user
        return {
          usedMessages: 0,
          totalQuota: 1000,
          remainingMessages: 1000,
          usagePercentage: 0,
          billingPeriodStart,
          billingPeriodEnd,
          messagesPerProvider: {
            'openai': 0,
            'anthropic': 0,
            'gemini': 0
          }
        };
      }
      
      // Regular metrics calculation for non-test users
      // Calculate the current billing period (start of current month to end of month)
      const now = new Date();
      const billingPeriodStart = new Date(now.getFullYear(), now.getMonth(), 1);
      const billingPeriodEnd = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59, 999);
      
      // Define the total quota (can be moved to an environment variable later)
      const totalQuota = 1000;
      
      // Count assistant messages for this user within the current billing period
      const messageCount = await prisma.message.count({
        where: {
          conversation: {
            userId: userId
          },
          role: MessageRole.ASSISTANT,
          createdAt: {
            gte: billingPeriodStart,
            lte: billingPeriodEnd
          }
        }
      });
      
      // Calculate remaining messages and usage percentage
      const remainingMessages = Math.max(0, totalQuota - messageCount);
      const usagePercentage = Math.min(100, (messageCount / totalQuota) * 100);
      
      // Get breakdown by provider (optional)
      const providerBreakdown = await prisma.message.groupBy({
        by: ['modelUsed'],
        where: {
          conversation: {
            userId: userId
          },
          role: MessageRole.ASSISTANT,
          createdAt: {
            gte: billingPeriodStart,
            lte: billingPeriodEnd
          },
          modelUsed: {
            not: null
          }
        },
        _count: true
      });
      
      // Format provider breakdown into a record
      const messagesPerProvider: Record<string, number> = {};
      
      // Define the type for the groupBy result
      interface ModelGroupResult {
        modelUsed: string | null;
        _count: number;
      }
      
      providerBreakdown.forEach((item: ModelGroupResult) => {
        if (item.modelUsed) {
          // Extract provider from model name (e.g., 'gpt-4' -> 'openai')
          const provider = this.extractProviderFromModel(item.modelUsed);
          const count = messagesPerProvider[provider] || 0;
          messagesPerProvider[provider] = count + item._count;
        }
      });
      
      return {
        usedMessages: messageCount,
        totalQuota,
        remainingMessages,
        usagePercentage,
        billingPeriodStart,
        billingPeriodEnd,
        messagesPerProvider: Object.keys(messagesPerProvider).length > 0 ? messagesPerProvider : undefined
      };
    } catch (error) {
      console.error('Get user metrics error:', error);
      throw error;
    }
  }
  
  /**
   * Extract provider name from model identifier
   */
  private extractProviderFromModel(modelName: string): string {
    if (modelName.startsWith('gpt-') || modelName.includes('openai')) {
      return 'openai';
    } else if (modelName.startsWith('claude') || modelName.includes('anthropic')) {
      return 'anthropic';
    } else if (modelName.startsWith('gemini') || modelName.includes('gemini')) {
      return 'gemini';
    } else {
      return 'other';
    }
  }

  /**
   * Admin: Get all users
   */
  async getAllUsers(): Promise<UserWithoutPassword[]> {
    try {
      const users = await prisma.user.findMany({
        orderBy: {
          createdAt: 'desc'
        }
      });

      // Remove password hashes
      // Update type annotation in map function to PrismaUser
      return users.map((user: PrismaUser) => {
        const { passwordHash: _, ...userWithoutPassword } = user;
        return userWithoutPassword as UserWithoutPassword;
      });
    } catch (error) {
      console.error('Get all users error:', error);
      throw error;
    }
  }

  /**
   * Admin: Delete a user
   */
  async deleteUser(userId: string): Promise<UserWithoutPassword> {
    try {
      const user = await prisma.user.delete({
        where: { id: userId }
      });

      // Return user without password hash
      const { passwordHash: _, ...userWithoutPassword } = user;
      return userWithoutPassword as UserWithoutPassword;
    } catch (error) {
      console.error('Delete user error:', error);
      throw error;
    }
  }

  /**
 * Admin: Update a user's role
 */
// Ensure the role parameter uses the Prisma Role enum type
async updateUserRole(userId: string, role: Role): Promise<UserWithoutPassword> {
  try {
    // Ensure the role being passed is a valid member of the Prisma Role enum
    if (!Object.values(Role).includes(role)) {
      throw new Error(`Invalid role: ${role}`);
    }
    const user = await prisma.user.update({
      where: { id: userId },
      data: { role } // Pass the Prisma enum value directly
    });

      // Return user without password hash
      const { passwordHash: _, ...userWithoutPassword } = user;
      return userWithoutPassword as UserWithoutPassword;
    } catch (error) {
      console.error('Update user role error:', error);
      throw error;
    }
  }
}

// Create a singleton instance
export const authService = new AuthService();

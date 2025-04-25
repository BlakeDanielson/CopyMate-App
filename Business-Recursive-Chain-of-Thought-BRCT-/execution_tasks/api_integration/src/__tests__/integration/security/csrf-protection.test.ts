import request from 'supertest';
import express from 'express';
import cookieParser from 'cookie-parser';
import csurf from 'csurf';
import { authService } from '../../../services/auth.service';
import { createAuthRoutes } from '../../../routes/auth.routes';

// Mock the auth service
jest.mock('../../../services/auth.service', () => ({
  authService: {
    signup: jest.fn(),
    login: jest.fn(),
    testLogin: jest.fn(),
    getUserById: jest.fn(),
    getUserMetrics: jest.fn(),
    verifyToken: jest.fn()
  }
}));

describe('CSRF Protection Tests', () => {
  let app: express.Application;
  let csrfProtection: express.RequestHandler;

  beforeEach(() => {
    // Create a new Express app for each test
    app = express();
    app.use(express.json());
    app.use(cookieParser());
    
    // Set up CSRF protection
    csrfProtection = csurf({
      cookie: {
        httpOnly: true,
        secure: false, // Not secure for testing
        sameSite: 'strict'
      },
      value: (req) => {
        return req.headers['x-csrf-token'] as string || req.body?._csrf;
      }
    });
    
    // Add CSRF route
    const apiRoutes = express.Router();
    
    // API route to provide CSRF token to the frontend
    apiRoutes.get('/csrf-token', csrfProtection, (req, res) => {
      res.json({ csrfToken: req.csrfToken() });
    });
    
    // Mount auth routes with CSRF protection
    const authRouter = createAuthRoutes();
    
    // Apply CSRF protection to auth routes except for login/signup for testing purposes
    app.use('/api/v1/auth', authRouter);
    
    // Protected route that requires CSRF
    apiRoutes.post('/protected', csrfProtection, (req, res) => {
      res.json({ success: true, message: 'Access granted to protected resource' });
    });
    
    app.use('/api/v1', apiRoutes);
    
    // Add CSRF error handler
    app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
      if (err.code === 'EBADCSRFTOKEN') {
        return res.status(403).json({
          success: false,
          error: 'Forbidden',
          message: 'Invalid CSRF token'
        });
      }
      next(err);
    });
    
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  it('should return a CSRF token when requested', async () => {
    // Act & Assert
    const response = await request(app)
      .get('/api/v1/csrf-token')
      .expect(200);
    
    // Verify response shape
    expect(response.body).toHaveProperty('csrfToken');
    expect(typeof response.body.csrfToken).toBe('string');
    expect(response.body.csrfToken.length).toBeGreaterThan(0);
  });

  it('should reject requests to protected routes without a CSRF token', async () => {
    // Act & Assert
    const response = await request(app)
      .post('/api/v1/protected')
      .send({ data: 'test data' })
      .expect(403);
    
    // Verify response includes CSRF error
    expect(response.body).toHaveProperty('error', 'Forbidden');
    expect(response.body).toHaveProperty('message', 'Invalid CSRF token');
  });

  it('should allow requests to protected routes with a valid CSRF token', async () => {
    // Arrange - Get a CSRF token first
    const tokenResponse = await request(app)
      .get('/api/v1/csrf-token')
      .expect(200);
    
    const csrfToken = tokenResponse.body.csrfToken;
    const cookies = tokenResponse.headers['set-cookie'];
    
    // Act & Assert - Use the token in a request to a protected route
    const response = await request(app)
      .post('/api/v1/protected')
      .set('Cookie', cookies)
      .set('x-csrf-token', csrfToken)
      .send({ data: 'test data' })
      .expect(200);
    
    // Verify success response
    expect(response.body).toHaveProperty('success', true);
    expect(response.body).toHaveProperty('message', 'Access granted to protected resource');
  });
});
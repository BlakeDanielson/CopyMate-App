/**
 * Main application entry point
 */

import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import cookieParser from 'cookie-parser';
import csurf from 'csurf';
import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';
import { KeyManager } from './utils/key-management';
import { LLMService } from './services/llm-service';
import { LLMController } from './controllers/llm-controller';
import { createLLMRoutes } from './routes/llm-routes';
import { createAuthRoutes } from './routes/auth.routes';
import { createConversationRoutes } from './routes/conversation.routes';
import subscriptionRoutes from './routes/subscription.routes';
import analyticsRoutes from './routes/analytics.routes';
import { createAdminRoutes } from './routes/admin.routes';
import { trackApiPerformance } from './middleware/performance.middleware';

// Load environment variables, explicitly loading .env.local if it exists
const envPath = path.resolve(__dirname, '..', '.env.local');
if (fs.existsSync(envPath)) {
  dotenv.config({ path: envPath });
  console.log(`Loaded environment variables from: ${envPath}`);
} else {
  dotenv.config(); // Fallback to default .env loading
  console.log('Loaded environment variables using default .env mechanism.');
}


// Initialize Express app
const app = express();
const PORT = process.env.PORT || 3002;

// Stripe webhook needs raw body for signature verification
// Save raw body for stripe webhook route
const stripeWebhookPath = '/api/v1/subscriptions/webhooks';
app.use((req, res, next) => {
  if (req.path === stripeWebhookPath && req.method === 'POST') {
    let data = '';
    req.setEncoding('utf8');
    req.on('data', (chunk) => {
      data += chunk;
    });
    req.on('end', () => {
      (req as any).rawBody = data;
      next();
    });
  } else {
    next();
  }
});

// Configure middleware
app.use(helmet()); // Security headers
app.use(cors()); // CORS support
app.use(compression()); // Response compression
app.use(cookieParser()); // Add cookie parser middleware

// Skip body parsing for stripe webhooks (needs raw body)
app.use((req, res, next) => {
  if (req.path === stripeWebhookPath && req.method === 'POST') {
    next();
  } else {
    express.json()(req, res, next);
  }
});

app.use(express.urlencoded({ extended: true })); // URL-encoded body parsing

// CSRF Protection Middleware (after cookie parser and body parsers)
// Ensure CSRF_SECRET is validated and available
const csrfProtection = csurf({
  cookie: {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production', // Use secure cookies in production
    sameSite: 'strict', // Recommended for CSRF protection
  },
  value: (req: Request) => {
    // Check standard CSRF header first, then fallback to body parameter if needed
    return req.headers['x-csrf-token'] as string || req.body?._csrf;
  }
});
// Apply CSRF protection globally, but potentially exclude specific routes like webhooks if needed
// Note: Stripe webhook path is already handled to skip body parsing, which might interfere
// We need to ensure CSRF is applied *after* the webhook check or exclude it explicitly.
// Let's apply it before the API routes are mounted.

// Ensure necessary directories exist
const dataDir = path.join(__dirname, '..', 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// Basic request logging and performance tracking
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// API performance tracking middleware
// Skip tracking for Stripe webhook and root healthcheck endpoint
app.use(trackApiPerformance([stripeWebhookPath, '/']));

// Initialize key manager
const keyStoragePath = path.join(dataDir, 'keys.json');
// ENCRYPTION_KEY is validated at startup
const encryptionKey = process.env.ENCRYPTION_KEY!; // Non-null assertion safe due to validation
const keyManager = new KeyManager(encryptionKey, keyStoragePath);

// Configure provider default models
const defaultModels: Record<string, string> = {
  openai: process.env.OPENAI_DEFAULT_MODEL || 'gpt-4',
  anthropic: process.env.ANTHROPIC_DEFAULT_MODEL || 'claude-3-sonnet-20240229',
  gemini: process.env.GEMINI_DEFAULT_MODEL || 'gemini-pro'
};

// Initialize LLM service
const llmService = new LLMService(keyManager, defaultModels);

// Initialize controller
const llmController = new LLMController(llmService);

// Set up routes
const apiRoutes = express.Router();
apiRoutes.use('/llm', createLLMRoutes(llmController));
apiRoutes.use('/auth', createAuthRoutes());
apiRoutes.use('/conversations', createConversationRoutes());
apiRoutes.use('/subscriptions', subscriptionRoutes);
apiRoutes.use('/analytics', analyticsRoutes);
apiRoutes.use('/admin', createAdminRoutes());

// Add a route to get the CSRF token (must be *before* applying csrfProtection globally if GET requests are protected)
// Alternatively, apply csrfProtection only to specific routes or routers.
// Let's add it to the main app level before the API router, but after the webhook check.
app.use((req, res, next) => {
  // Exclude Stripe webhook from CSRF protection
  if (req.path === stripeWebhookPath && req.method === 'POST') {
    return next();
  }
  // Apply CSRF protection to other routes
  csrfProtection(req, res, next);
});


// API route to provide CSRF token to the frontend
apiRoutes.get('/csrf-token', (req: Request, res: Response) => {
  res.json({ csrfToken: req.csrfToken() });
});

// Mount API routes (now includes CSRF protection for most routes)
app.use('/api/v1', apiRoutes);


// Root route for healthcheck
app.get('/', (req, res) => {
  res.json({
    status: 'ok',
    service: 'UnifiedLLM Hub - API Integration',
    version: '1.0.0'
  });
});

// Error handling middleware - Add specific CSRF error handling
app.use((err: any, req: Request, res: Response, next: NextFunction) => {
  if (err.code === 'EBADCSRFTOKEN') {
    console.warn('CSRF Token Validation Failed:', err.message);
    res.status(403).json({
      success: false,
      error: 'Forbidden',
      message: 'Invalid CSRF token. Please refresh the page or try again.'
    });
  } else {
    // General error handling
    console.error('Unhandled error:', err);
    res.status(err.status || 500).json({
      success: false,
      error: err.message || 'Internal server error',
      message: process.env.NODE_ENV === 'development' ? err.stack : undefined
    });
  }
});

// Store API keys if provided in environment variables
const storeApiKeys = async () => {
  // Store OpenAI API key if provided
  if (process.env.OPENAI_API_KEY) {
    keyManager.storeKey('openai', process.env.OPENAI_API_KEY);
  }

  // Store Anthropic API key if provided
  if (process.env.ANTHROPIC_API_KEY) {
    keyManager.storeKey('anthropic', process.env.ANTHROPIC_API_KEY);
  }

  // Store Gemini API key if provided
  if (process.env.GEMINI_API_KEY) {
    keyManager.storeKey('gemini', process.env.GEMINI_API_KEY);
  }
};

// Initialize the service and start the server
const startServer = async () => {
  try {
    // Store API keys from environment
    await storeApiKeys();
    
    // Initialize LLM service
    const initialized = await llmService.initialize();
    if (initialized) {
      console.log('LLM service initialized successfully');
    } else {
      console.warn('LLM service initialization incomplete. Some providers may not be available.');
    }
    
    // Start server
    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
      console.log(`Available providers: ${llmService.getAvailableProviders().join(', ') || 'None'}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
};

// Start the server
startServer();

// Export the app for testing
export default app;

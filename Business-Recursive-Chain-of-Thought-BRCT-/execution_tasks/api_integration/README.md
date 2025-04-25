# UnifiedLLM Hub - API Integration Architecture

This package implements the API Integration Architecture for the UnifiedLLM Hub, providing a unified interface to multiple LLM providers (OpenAI, Anthropic, and Gemini) with optimized performance, error handling, and security features.

## Features

- **Unified API Interface**: Access multiple LLM providers through a single, consistent API
- **Adapter Pattern**: Standardized interface for easy integration of additional LLM providers
- **Secure API Key Management**: Encrypted storage of API keys with automatic rotation support
- **Streaming Support**: Real-time streaming of LLM responses using Server-Sent Events
- **Error Handling**: Standardized error handling with exponential backoff for rate limiting
- **Usage Tracking**: Token usage monitoring across providers
- **Model Comparison**: Compare responses from different providers for the same prompt
- **TypeScript**: Type-safe implementation with comprehensive interfaces
- **RESTful API**: Well-documented API endpoints

## Project Structure

```
src/
├── adapters/            # Provider-specific implementations
│   ├── interface.ts     # Core LLM interface
│   ├── base.ts          # Base adapter with common functionality
│   ├── openai.ts        # OpenAI-specific adapter
│   ├── anthropic.ts     # Anthropic-specific adapter
│   ├── gemini.ts        # Google Gemini-specific adapter
│   └── factory.ts       # Factory for creating adapters
├── controllers/         # Request handlers
│   └── llm-controller.ts
├── models/              # Database models (not implemented yet)
├── routes/              # API route definitions
│   └── llm-routes.ts
├── services/            # Business logic
│   └── llm-service.ts
├── types/               # TypeScript interfaces
│   └── adapters.ts      # Common types for adapters
├── utils/               # Utility functions
│   └── key-management.ts
└── app.ts               # Application entry point
```

## Prerequisites

- Node.js 16.x or higher
- npm or yarn
- API keys from the LLM providers you want to use

## Installation

1. Clone the repository
2. Install dependencies:

```bash
cd api-integration
npm install
```

3. Copy the environment example file and configure it:

```bash
cp .env.example .env
```

4. Edit the `.env` file to add your API keys and configuration.

## Configuration

The following environment variables **must** be configured for the application to function correctly. The server will exit on startup if required variables are missing or invalid.

| Variable | Description | Required | Default | Notes |
|----------|-------------|----------|---------|-------|
| `PORT` | Server port | No | 3002 | |
| `NODE_ENV` | Environment (development, production) | No | development | |
| `DATABASE_URL` | Connection string for the PostgreSQL database | Yes | - | Example: `postgresql://user:password@host:port/database?schema=public` |
| `JWT_SECRET` | Secret key for signing JWT tokens | Yes | - | Must be a strong, random string (e.g., 64+ characters). |
| `CSRF_SECRET` | Secret key for CSRF protection | Yes | - | Must be a strong, random string (e.g., 32+ characters). |
| `ENCRYPTION_KEY` | Key for encrypting API keys (AES-256-CBC) | Yes | Auto-generated in dev | Must be exactly 32 bytes (characters) long. |
| `OPENAI_API_KEY` | OpenAI API key | No | - | Required only if using OpenAI provider. |
| `ANTHROPIC_API_KEY` | Anthropic API key | No | - | Required only if using Anthropic provider. |
| `GEMINI_API_KEY` | Google Gemini API key | No | - | Required only if using Gemini provider. |
| `OPENAI_DEFAULT_MODEL` | Default OpenAI model | No | gpt-4 | |
| `ANTHROPIC_DEFAULT_MODEL` | Default Anthropic model | No | claude-3-sonnet-20240229 | |
| `GEMINI_DEFAULT_MODEL` | Default Gemini model | No | gemini-pro | |
| `ENABLE_TEST_LOGIN` | Enable/disable test login endpoint (`/api/auth/test-login`) | No | `false` | Set to `true` only for testing/development. **Never enable in production.** |
| `TEST_USER_EMAIL` | Email for test login | No | `test@example.com` | Used only if `ENABLE_TEST_LOGIN` is `true`. |
| `TEST_USER_PASSWORD` | Password for test login | No | `password` | Used only if `ENABLE_TEST_LOGIN` is `true`. |

## Usage

### Starting the Server

```bash
# Development mode with hot reloading
npm run dev

# Build and run in production mode
npm run build
npm start
```

### API Endpoints

#### Provider Management

- `GET /api/v1/llm/providers` - Get all available providers
- `GET /api/v1/llm/providers/:provider/models` - Get available models for a provider

#### Completions

- `POST /api/v1/llm/completions/:provider` - Generate a completion
- `POST /api/v1/llm/completions/:provider/stream` - Stream a completion
- `POST /api/v1/llm/completions/compare` - Compare completions across providers

#### Usage

- `GET /api/v1/llm/usage` - Get usage statistics

#### Authentication

- `POST /api/auth/signup` - Register a new user.
    - **Request Body**: `{ "email": "user@example.com", "password": "yourpassword" }`
    - **Responses**:
        - `201 Created`: User successfully registered. Returns user object (excluding password) and JWT token.
        - `400 Bad Request`: Invalid input (e.g., missing fields, invalid email format).
        - `409 Conflict`: Email already exists.
        - `429 Too Many Requests`: Rate limit exceeded.
- `POST /api/auth/login` - Authenticate a user and receive a JWT token.
    - **Request Body**: `{ "email": "user@example.com", "password": "yourpassword" }`
    - **Responses**:
        - `200 OK`: Login successful. Returns user object (excluding password) and JWT token.
        - `400 Bad Request`: Missing fields.
        - `401 Unauthorized`: Invalid credentials.
        - `429 Too Many Requests`: Rate limit exceeded.
- `GET /api/v1/csrf-token` - Get a CSRF token required for state-changing requests.
    - **Responses**:
        - `200 OK`: Returns `{ csrfToken: "..." }`.

### Example Requests

#### Generate a Completion

```bash
curl -X POST http://localhost:3000/api/v1/llm/completions/openai \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms.",
    "temperature": 0.7,
    "maxTokens": 300
  }'
```

#### Stream a Completion

```bash
curl -X POST http://localhost:3000/api/v1/llm/completions/openai/stream \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a short story about a robot that learns to paint.",
    "temperature": 0.8,
    "maxTokens": 500
  }'
```

#### Compare Completions Across Providers

```bash
curl -X POST http://localhost:3000/api/v1/llm/completions/compare \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What are the ethical implications of AI?",
    "providers": ["openai", "anthropic", "gemini"],
    "temperature": 0.7,
    "maxTokens": 400
  }'
```

## Extending the Architecture

### Adding a New Provider

1. Create a new adapter in the `src/adapters` directory
2. Implement the `LLMInterface` interface
3. Update the `AdapterFactory` to support the new provider
4. Add appropriate environment variables and configuration

### Adding New Endpoints

1. Create controller methods in the appropriate controller
2. Add routes to the appropriate router
3. Update documentation

## Error Handling

The API uses standardized error handling with the following structure:

```json
{
  "success": false,
  "error": "Error message"
}
```

## Security

- **Password Hashing**: User passwords are securely hashed using `bcrypt` before storage.
- **JWT Authentication**: User sessions are managed using JSON Web Tokens (JWT) with a 1-hour expiration time. Tokens are signed using a secret key (`JWT_SECRET`).
- **Rate Limiting**: Authentication endpoints (`/api/auth/signup`, `/api/auth/login`) are rate-limited to prevent brute-force attacks.
- **CSRF Protection**: Implemented using `csurf`. Clients must fetch a token from `/api/v1/csrf-token` and include it in subsequent state-changing requests (POST, PUT, DELETE, PATCH) via the `X-CSRF-Token` header or `_csrf` request body parameter.
- **API Key Encryption**: LLM provider API keys are encrypted at rest using AES-256-CBC (`ENCRYPTION_KEY`).
- **Secure Headers**: Security headers are set using `helmet`.
- **CORS**: Configured to restrict access as needed.

## Performance Considerations

- Connection pooling for API requests
- Streaming support for real-time responses
- Rate limiting with exponential backoff and jitter
- Edge computing architecture (designed for but not implemented yet)

## Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

## License

[MIT](LICENSE)

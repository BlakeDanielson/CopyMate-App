# UnifiedLLM Hub Frontend

This is the frontend application for the UnifiedLLM Hub, a unified interface to multiple LLM providers such as OpenAI, Anthropic, and Google Gemini.

## Features

- **Unified LLM Interface**: Connect to multiple LLM providers (OpenAI, Anthropic, Google Gemini) through a single interface
- **Real-time Streaming**: Stream responses from LLMs in real-time
- **Conversation Management**: Create, view, and manage conversations
- **Provider & Model Selection**: Choose from available providers and models
- **Customizable Parameters**: Adjust temperature, max tokens, and other LLM parameters
- **Performance Metrics**: View performance metrics for different models
- **User Authentication**: Secure login and user management
- **User Sign Up**: New users can register via the `/signup` route.
- **Responsive Design**: Works on desktop and mobile devices
- **Theme Options**: Light, dark, and system themes

## Tech Stack

- **React**: Frontend library
- **TypeScript**: Type-safe JavaScript
- **Redux Toolkit**: State management
- **Material-UI**: Component library
- **React Router**: Navigation
- **Axios**: API requests

## Project Structure

```
src/
├── components/       # Reusable UI components
├── config/           # Configuration and constants
├── hooks/            # Custom React hooks
├── interfaces/       # TypeScript interfaces
├── pages/            # Page components
├── services/         # API and other services
│   └── api/          # API service modules
├── store/            # Redux store
│   └── slices/       # Redux slices
└── utils/            # Utility functions
```

## Getting Started

### Prerequisites

- Node.js (v14 or later)
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```
   cd execution_tasks/frontend/unified-llm-hub
   ```
3. Install dependencies:
   ```
   npm install
   ```
   or
   ```
   yarn install
   ```

### Running the Application

Start the development server:
```
npm start
```
or
```
yarn start
```

The application will be available at [http://localhost:3000](http://localhost:3000).

### Building for Production

```
npm run build
```
or
```
yarn build
```

## Integration with Backend

This frontend application connects to the UnifiedLLM Hub backend API, which provides:

- Authentication services (including Login at `/api/auth/login` and **Sign Up at `/api/auth/signup`**)
- Provider API integration
- Conversation management
- LLM request handling and streaming
- Performance metrics collection
- **CSRF Protection**: The backend uses CSRF protection. The frontend must fetch a CSRF token from `/api/v1/csrf-token` (typically on initial load or before a state-changing action) and include it in the `X-CSRF-Token` header for all state-changing requests (e.g., POST, PUT, DELETE, PATCH, including signup and login).

Make sure the backend API is running and properly configured in the `.env` file.

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
REACT_APP_API_BASE_URL=http://localhost:3001/api
```

## License

[MIT](LICENSE)

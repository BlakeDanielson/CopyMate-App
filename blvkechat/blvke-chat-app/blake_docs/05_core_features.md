# 5. Core Features & Functionality

This section details the main features implemented in the `blvke-chat-app`.

## 1. Authentication

The application implements user authentication using `next-auth`.

*   **Providers:** Primarily configured for Credentials-based login (email/password). Support for OAuth providers (like Google, GitHub) can be added via `src/server/auth.ts`.
*   **Registration:** New users can sign up via the `/register` page (`src/app/register/page.tsx`), handled by `src/components/register-form.tsx` which likely calls a custom API endpoint (e.g., `/api/auth/register`) or a tRPC mutation to create a user record in the database.
*   **Login:** Existing users can log in via the `/login` page (`src/app/login/page.tsx`) using `src/components/login-form.tsx`. This typically interacts with the `signIn` function from `next-auth/react` and the Credentials provider defined in `src/server/auth.ts`.
*   **Session Management:** `next-auth` handles session creation and management (using JWT or database sessions, configured in `src/server/auth.ts`). Sessions are persisted via cookies.
*   **Route Protection:** Middleware (`middleware.ts` or `src/middleware.ts`) intercepts requests and checks for a valid session. Unauthenticated users attempting to access protected routes (like `/chat`) are redirected to the login page (`/login`).

**Key Files:**
*   `src/app/login/page.tsx`
*   `src/app/register/page.tsx`
*   `src/components/login-form.tsx`
*   `src/components/register-form.tsx`
*   `src/server/auth.ts` (NextAuth configuration)
*   `src/app/api/auth/[...nextauth]/route.ts` (NextAuth API handler)
*   `middleware.ts` / `src/middleware.ts` (Route protection)
*   `prisma/schema.prisma` (User, Account, Session models)

## 2. Chat Interface

The core chat functionality is accessible via the `/chat` route.

*   **Layout:** The chat page (`src/app/chat/page.tsx`) likely uses `src/components/chat-interface.tsx` as the main component.
*   **Conversation List:** Displays available conversations, allowing users to switch between them (`src/components/conversation-list.tsx`). Fetches data likely via a tRPC query (e.g., `conversation.getAll`).
*   **Message Display:** Shows messages for the selected conversation (`src/components/message-list.tsx`). Fetches messages via tRPC (e.g., `conversation.getMessages`). Supports rendering Markdown (`react-markdown`).
*   **Message Input:** Users can type and send messages using an input area within `src/components/chat-interface.tsx`. Sending messages likely triggers a tRPC mutation (e.g., `conversation.sendMessage`).
*   **Real-time Updates (Potential):** While not explicitly confirmed without deeper code analysis, real-time updates could be implemented using WebSockets or polling via tRPC subscriptions or React Query refetching.

**Key Files:**
*   `src/app/chat/page.tsx`
*   `src/components/chat-interface.tsx`
*   `src/components/conversation-list.tsx`
*   `src/components/message-list.tsx`
*   `src/server/api/routers/conversation.ts` (tRPC procedures)
*   `react-markdown` (Dependency for rendering)

## 3. Conversation Management

Users can manage their chat conversations.

*   **Creation:** New conversations might be initiated implicitly when sending a message to a new recipient (if applicable) or explicitly through a UI element calling a tRPC mutation (e.g., `conversation.create`).
*   **Retrieval:** Users can view their list of conversations (`conversation.getAll` tRPC query).
*   **Deletion/Archiving (Potential):** Functionality to delete or archive conversations might exist via tRPC mutations.

**Key Files:**
*   `src/server/api/routers/conversation.ts`
*   `src/lib/conversations.ts` (Potentially contains related logic)
*   `prisma/schema.prisma` (Conversation, Message models)

## 4. AI Integration (Chatbot)

The application integrates AI capabilities, likely for chatbot responses.

*   **API Endpoint:** The `/api/chat` route (`src/app/api/chat/route.ts`) seems dedicated to handling AI interactions.
*   **AI SDK:** Uses the Vercel AI SDK (`ai` and `@ai-sdk/openai` packages) for interacting with AI models (likely OpenAI's GPT models, configured via `OPENAI_API_KEY` in `.env`).
*   **Streaming Responses:** The AI SDK facilitates streaming responses, allowing the chatbot's message to appear token-by-token in the UI (`@ai-sdk/react` hook `useChat` or similar).
*   **Triggering:** AI responses might be triggered automatically in certain conversations or when specific commands/mentions are used. The logic resides within the `/api/chat` handler and potentially the tRPC procedures.

**Key Files:**
*   `src/app/api/chat/route.ts`
*   `package.json` (Dependencies: `ai`, `@ai-sdk/openai`, `@ai-sdk/react`)
*   `.env` (`OPENAI_API_KEY`)

## 5. Middleware Routing

Middleware intercepts requests for purposes like authentication.

*   **Implementation:** A `middleware.ts` file (either at the root or in `src/`) defines functions that run before requests are processed.
*   **Authentication Check:** The primary use case appears to be checking if a user is authenticated based on their `next-auth` session cookie.
*   **Redirects:** If the user is not authenticated for a protected route, the middleware redirects them to the login page. It might also handle redirecting authenticated users away from public-only pages like login/register.

**Key Files:**
*   `middleware.ts` / `src/middleware.ts`
*   `src/lib/auth.ts` (May contain helper functions used by middleware)
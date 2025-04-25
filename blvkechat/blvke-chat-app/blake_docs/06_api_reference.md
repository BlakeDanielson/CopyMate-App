# 6. API Reference

This document details the available API endpoints, including tRPC procedures and standard Next.js API routes.

## tRPC Procedures (`src/server/api/routers/`)

All tRPC procedures are accessed via the single handler at `/api/trpc/[trpc]`. Authentication is typically required (`protectedProcedure`) unless specified otherwise (`publicProcedure`). Input validation is performed using Zod.

*(Note: The actual return types are inferred by tRPC and Prisma, but key fields are described.)*

### Conversation Router (`conversation.ts`)

Handles operations related to chat conversations and messages.

*   **`conversation.getAll`**
    *   **Type:** Query
    *   **Auth:** Required
    *   **Input:** None
    *   **Output:** `Array<{ id, title, isPinned, lastMessageAt, messageCount, lastMessage }>` - List of the user's conversations, ordered by pinned status and last message time. Includes the content of the very last message.
    *   **Purpose:** Fetches a summary list of all conversations for the logged-in user.

*   **`conversation.getById`**
    *   **Type:** Query
    *   **Auth:** Required
    *   **Input:** `z.object({ id: z.string() })`
    *   **Output:** Prisma `Conversation` object or `null`.
    *   **Purpose:** Fetches details of a specific conversation by its ID.

*   **`conversation.create`**
    *   **Type:** Mutation
    *   **Auth:** Required
    *   **Input:** `z.object({ title: z.string() })`
    *   **Output:** Prisma `Conversation` object.
    *   **Purpose:** Creates a new conversation for the user.

*   **`conversation.update`**
    *   **Type:** Mutation
    *   **Auth:** Required
    *   **Input:** `z.object({ id: z.string(), title: z.string().optional(), isPinned: z.boolean().optional() })`
    *   **Output:** Prisma `Conversation` object.
    *   **Purpose:** Updates the title or pinned status of a conversation.

*   **`conversation.delete`**
    *   **Type:** Mutation
    *   **Auth:** Required
    *   **Input:** `z.object({ id: z.string() })`
    *   **Output:** `{ success: true }`
    *   **Purpose:** Deletes a conversation and its associated messages.

*   **`conversation.getMessages`**
    *   **Type:** Query
    *   **Auth:** Required
    *   **Input:** `z.object({ conversationId: z.string() })`
    *   **Output:** Array of Prisma `Message` objects, ordered by creation time (ascending).
    *   **Purpose:** Fetches all messages for a specific conversation.

*   **`conversation.addMessage`**
    *   **Type:** Mutation
    *   **Auth:** Required
    *   **Input:** `z.object({ conversationId: z.string(), role: z.string(), content: z.string(), tokensUsed: z.number().optional() })`
    *   **Output:** Prisma `Message` object.
    *   **Purpose:** Adds a new message to a conversation and updates the conversation's `lastMessageAt` timestamp.

### Post Router (`post.ts`)

Seems to be example/template code from the T3 stack setup, potentially not core to the chat app's functionality unless adapted.

*   **`post.hello`**
    *   **Type:** Query
    *   **Auth:** Public
    *   **Input:** `z.object({ text: z.string() })`
    *   **Output:** `{ greeting: string }`
    *   **Purpose:** Example public procedure.

*   **`post.create`**
    *   **Type:** Mutation
    *   **Auth:** Required
    *   **Input:** `z.object({ name: z.string().min(1) })`
    *   **Output:** Prisma `Post` object.
    *   **Purpose:** Example mutation to create a 'Post' record associated with the user.

*   **`post.getLatest`**
    *   **Type:** Query
    *   **Auth:** Required
    *   **Input:** None
    *   **Output:** Prisma `Post` object or `null`.
    *   **Purpose:** Example query to get the latest 'Post' created by the user.

*   **`post.getSecretMessage`**
    *   **Type:** Query
    *   **Auth:** Required
    *   **Input:** None
    *   **Output:** `string`
    *   **Purpose:** Example protected procedure returning a static string.

### Settings Router (`settings.ts`)

Manages user-specific application settings.

*   **`settings.get`**
    *   **Type:** Query
    *   **Auth:** Required
    *   **Input:** None
    *   **Output:** Prisma `UserSettings` object (creates default settings if none exist).
    *   **Purpose:** Fetches the settings for the logged-in user.

*   **`settings.update`**
    *   **Type:** Mutation
    *   **Auth:** Required
    *   **Input:** `z.object({ modelName: z.string().optional(), temperature: z.number().min(0).max(2).optional(), maxTokens: z.number().min(100).max(4000).optional(), theme: z.string().optional(), fontSize: z.string().optional() })`
    *   **Output:** Prisma `UserSettings` object.
    *   **Purpose:** Updates specific settings for the logged-in user (creates settings if none exist).

## Next.js API Routes (`src/app/api/`)

These are standard API endpoints handled by Next.js.

*   **`POST /api/chat`**
    *   **Auth:** Required (checks via `getCurrentUser`)
    *   **Request Body:** `{ messages: Array<{role: string, content: string}>, conversationId?: string, conversationTitle?: string }`
    *   **Response:** Streaming text response (`ai` SDK `streamText`) containing the AI assistant's message. Also saves user and assistant messages to the database via `lib/conversations`. Creates a new conversation if `conversationId` is not provided. Uses settings from `lib/settings`.
    *   **Purpose:** Handles the main AI chat interaction, receiving message history and returning a streamed AI response.

*   **`GET /api/chat?id={conversationId}`**
    *   **Auth:** Required (checks via `getCurrentUser`)
    *   **Query Parameters:** `id` (conversation ID)
    *   **Response:** JSON array of `Message` objects for the specified conversation.
    *   **Purpose:** Fetches messages for a specific conversation (potentially redundant with `conversation.getMessages` tRPC procedure, usage context needed).

*   **`POST /api/auth/login`**
    *   **Auth:** Public
    *   **Request Body:** `{ email: string, password: string }`
    *   **Response:** `{ success: true }` on successful login, error object otherwise. Handles user lookup, password comparison, and session creation via `lib/auth`.
    *   **Purpose:** Custom endpoint for handling credentials-based login. *Note: This might be used alongside or instead of the default NextAuth.js credentials flow.*

*   **`POST /api/auth/register`**
    *   **Auth:** Public
    *   **Request Body:** `{ email: string, name: string, password: string }`
    *   **Response:** `{ success: true }` on successful registration, error object otherwise. Handles user creation and session creation via `lib/auth`.
    *   **Purpose:** Custom endpoint for handling user registration.

*   **`POST /api/auth/logout`**
    *   **Auth:** Public (but effectively requires an active session to log out from)
    *   **Request Body:** None
    *   **Response:** `{ success: true }` on successful logout, error object otherwise. Calls `signOut` from `lib/auth`.
    *   **Purpose:** Custom endpoint for logging the user out.

*   **`/api/auth/[...nextauth]`**
    *   **Auth:** Handled by NextAuth.js internally.
    *   **Purpose:** Catches all standard NextAuth.js API calls (e.g., `/api/auth/session`, `/api/auth/signin/github`, `/api/auth/callback/credentials`). Configuration is in `src/server/auth.ts`.
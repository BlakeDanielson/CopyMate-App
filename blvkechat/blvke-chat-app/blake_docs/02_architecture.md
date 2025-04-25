# 2. System Architecture

This document outlines the high-level architecture of the `blvke-chat-app`.

## Overview

The application follows a modern web architecture built upon the Next.js framework, integrating a backend API layer (using both Next.js API Routes and tRPC), a database managed by Prisma, and a frontend built with React and styled using Tailwind CSS and shadcn/ui components.

## Components

1.  **Frontend (Client-Side):**
    *   **Framework:** Next.js (App Router) with React.
    *   **UI Components:** Built using `shadcn/ui` which leverages Radix UI primitives.
    *   **Styling:** Tailwind CSS for utility-first styling.
    *   **State Management:** Primarily managed via React hooks and potentially tRPC's React Query integration for server state.
    *   **Location:** `src/app/`, `src/components/`, `src/hooks/`.

2.  **Backend (Server-Side):**
    *   **Framework:** Next.js handles both server-side rendering and API endpoints.
    *   **API Layer:**
        *   **tRPC:** Used for type-safe API communication between frontend and backend. Routers are defined in `src/server/api/routers/`. The root configuration is in `src/server/api/root.ts` and `src/server/api/trpc.ts`. The client setup is in `src/trpc/`.
        *   **Next.js API Routes:** Used for specific endpoints, particularly authentication (`src/app/api/auth/`) and potentially the AI chat stream (`src/app/api/chat/`).
    *   **Authentication:** Handled by `next-auth` (`src/server/auth.ts`, `src/app/api/auth/[...nextauth]/route.ts`). Middleware (`middleware.ts` or `src/middleware.ts`) likely enforces authentication checks.
    *   **Location:** `src/server/`, `src/app/api/`.

3.  **Database:**
    *   **Type:** PostgreSQL (as indicated by `start-database.sh`).
    *   **ORM:** Prisma (`prisma/schema.prisma`, `src/server/db.ts`). Manages database schema, migrations, and type-safe database access.

4.  **AI Integration:**
    *   **Library:** Vercel AI SDK (`ai` package).
    *   **Implementation:** Likely integrated within the `/api/chat` route (`src/app/api/chat/route.ts`) for handling streaming AI responses.

## Data Flow Example (Sending a Message)

1.  **User Interaction:** User types and sends a message in the chat interface (`src/components/chat-interface.tsx`).
2.  **Frontend Request:** The frontend client (likely using tRPC's `useMutation`) sends the message content and conversation ID to the backend tRPC endpoint (e.g., `conversation.sendMessage`).
3.  **Backend Processing:**
    *   The tRPC router (`src/server/api/routers/conversation.ts`) receives the request.
    *   It validates the input (using Zod schemas).
    *   It uses Prisma (`src/server/db.ts`) to save the message to the PostgreSQL database, associating it with the correct user and conversation.
    *   (Optional AI Interaction): If the message triggers an AI response, the backend might call the `/api/chat` endpoint or directly use the AI SDK.
4.  **Database Update:** Prisma executes the SQL query to insert the new message.
5.  **Backend Response:** The tRPC endpoint returns a success status or the newly created message object.
6.  **Frontend Update:** The frontend (via React Query's cache invalidation or update mechanisms) reflects the new message in the UI (`src/components/message-list.tsx`).

## Authentication Flow

1.  User navigates to `/login` or `/register`.
2.  Submits credentials via forms (`src/components/login-form.tsx`, `src/components/register-form.tsx`).
3.  Frontend calls NextAuth.js endpoints (`/api/auth/callback/credentials` or custom routes like `/api/auth/login`).
4.  NextAuth.js adapter (using Prisma) verifies credentials against the database (`User` model).
5.  Upon success, NextAuth.js creates a session (JWT or database session) and sets a cookie.
6.  Middleware (`middleware.ts`) checks for the session cookie on subsequent requests to protected routes (e.g., `/chat`).
7.  If valid, the request proceeds; otherwise, the user is redirected to login.

*(Note: Text-based diagrams like Mermaid could be added here later if more detailed visualization is needed.)*
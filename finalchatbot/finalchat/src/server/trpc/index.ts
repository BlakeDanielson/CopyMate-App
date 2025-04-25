// src/server/trpc/index.ts
import { createTRPCRouter } from './trpc';
// Import feature routers here (e.g., import { chatRouter } from './routers/chat';)

/**
 * This is the primary router for your server.
 *
 * All routers added in /api/routers should be manually added here.
 */
export const appRouter = createTRPCRouter({
  // chat: chatRouter, // Add feature routers here
  // example: exampleRouter, // Placeholder
});

// Export type definition of API
export type AppRouter = typeof appRouter;
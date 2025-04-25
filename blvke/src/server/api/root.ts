import { createTRPCRouter } from "@/server/api/trpc"
import { conversationRouter } from "@/server/api/routers/conversation"
import { settingsRouter } from "@/server/api/routers/settings"

/**
 * This is the primary router for your server.
 *
 * All routers added in /api/routers should be manually added here.
 */
export const appRouter = createTRPCRouter({
  conversation: conversationRouter,
  settings: settingsRouter,
})

// export type definition of API
export type AppRouter = typeof appRouter

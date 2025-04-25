import { z } from "zod"
import { createTRPCRouter, protectedProcedure } from "@/server/api/trpc"

export const settingsRouter = createTRPCRouter({
  get: protectedProcedure.query(async ({ ctx }) => {
    try {
      const settings = await ctx.db.userSettings.findUnique({
        where: { userId: ctx.session.user.id },
      })

      if (!settings) {
        // Create default settings if they don't exist
        return ctx.db.userSettings.create({
          data: {
            userId: ctx.session.user.id,
            // Default values are set in the schema
          },
        })
      }

      return settings
    } catch (error) {
      // For demo purposes, return mock data if database is not available
      return {
        id: "mock-settings",
        userId: ctx.session.user.id,
        modelName: "gpt-4o",
        temperature: 0.7,
        maxTokens: 1000,
        theme: "dark",
        fontSize: "medium",
        createdAt: new Date(),
        updatedAt: new Date(),
      }
    }
  }),

  update: protectedProcedure
    .input(
      z.object({
        modelName: z.string().optional(),
        temperature: z.number().min(0).max(2).optional(),
        maxTokens: z.number().min(100).max(4000).optional(),
        theme: z.string().optional(),
        fontSize: z.string().optional(),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      try {
        const settings = await ctx.db.userSettings.findUnique({
          where: { userId: ctx.session.user.id },
        })

        if (!settings) {
          return ctx.db.userSettings.create({
            data: {
              userId: ctx.session.user.id,
              ...input,
            },
          })
        }

        return ctx.db.userSettings.update({
          where: { userId: ctx.session.user.id },
          data: input,
        })
      } catch (error) {
        // For demo purposes, return mock data if database is not available
        return {
          id: "mock-settings",
          userId: ctx.session.user.id,
          modelName: input.modelName || "gpt-4o",
          temperature: input.temperature || 0.7,
          maxTokens: input.maxTokens || 1000,
          theme: input.theme || "dark",
          fontSize: input.fontSize || "medium",
          createdAt: new Date(),
          updatedAt: new Date(),
        }
      }
    }),
})

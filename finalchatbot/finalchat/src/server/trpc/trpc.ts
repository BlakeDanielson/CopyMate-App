// src/server/trpc/trpc.ts
import { initTRPC } from '@trpc/server';
import type { CreateNextContextOptions } from '@trpc/server/adapters/next';

/**
 * Initialization of tRPC backend
 * Should be done only once per backend!
 */

// Context creation (optional for now, can be expanded later for auth, db)
export const createTRPCContext = async (opts: CreateNextContextOptions) => {
  // For now, we don't need any context, but this is where you'd add it
  // e.g., const { req, res } = opts;
  // const session = await getAuthSession({ req, res }); // Example auth
  // const db = await connectToDb(); // Example db connection
  return {
    // session,
    // db,
  };
};

const t = initTRPC.context<typeof createTRPCContext>().create();

/**
 * Export reusable router and procedure helpers
 * that can be used throughout the router
 */
export const createTRPCRouter = t.router;
export const publicProcedure = t.procedure;

// Example protected procedure (add later when Clerk is integrated)
// export const protectedProcedure = t.procedure.use(({ ctx, next }) => {
//   if (!ctx.session || !ctx.session.user) {
//     throw new TRPCError({ code: 'UNAUTHORIZED' });
//   }
//   return next({
//     ctx: {
//       // infers the `session` as non-nullable
//       session: { ...ctx.session, user: ctx.session.user },
//     },
//   });
// });
// src/lib/trpc/client.ts
import { createTRPCReact } from '@trpc/react-query';
import type { AppRouter } from '@/server/trpc'; // Import the AppRouter type
// Uncomment these if you need input/output types inferred on the client side
// import type { inferRouterInputs, inferRouterOutputs } from '@trpc/server';

/**
 * A set of typesafe hooks for consuming your API.
 */
export const trpc = createTRPCReact<AppRouter>();

/**
 * Inference helper for inputs.
 * @example type HelloInput = RouterInputs['example']['hello']
 **/
// export type RouterInputs = inferRouterInputs<AppRouter>;

/**
 * Inference helper for outputs.
 * @example type HelloOutput = RouterOutputs['example']['hello']
 **/
// export type RouterOutputs = inferRouterOutputs<AppRouter>;
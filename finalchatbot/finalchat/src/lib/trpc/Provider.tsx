// src/lib/trpc/Provider.tsx
'use client'; // This needs to be a client component

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { httpBatchLink, loggerLink } from '@trpc/client';
import React, { useState } from 'react';

import { trpc } from './client'; // We'll create this next
import { getUrl } from './utils'; // We'll create this next

export default function TrpcProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  // Use state to ensure QueryClient and trpcClient are only created once per render
  const [queryClient] = useState(() => new QueryClient({}));
  const [trpcClient] = useState(() =>
    trpc.createClient({
      links: [
        // Optional: Log tRPC requests/responses in development
        loggerLink({
          enabled: (opts) =>
            process.env.NODE_ENV === 'development' ||
            (opts.direction === 'down' && opts.result instanceof Error),
        }),
        // Batching link for performance
        httpBatchLink({
          url: getUrl(), // Dynamically get the API URL
          headers() {
            // Can add headers here if needed later (e.g., for auth)
            return {
              // authorization: getAuthCookie(),
            };
          },
        }),
      ],
    }),
  );

  return (
    <trpc.Provider client={trpcClient} queryClient={queryClient}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </trpc.Provider>
  );
}
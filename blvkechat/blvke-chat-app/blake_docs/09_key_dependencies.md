# 9. Key Dependencies

This section lists the crucial external libraries and frameworks used in the `blvke-chat-app`, as defined in `package.json`, and explains their roles.

## Core Framework & Runtime

*   **`next`**: The React framework for production. Provides Server-Side Rendering (SSR), Static Site Generation (SSG), routing (App Router used here), API routes, and optimizations.
*   **`react` / `react-dom`**: The JavaScript library for building user interfaces. Next.js is built on top of React.
*   **`typescript`**: Superset of JavaScript that adds static typing, improving code quality and maintainability. (Used in `devDependencies`).
*   **`node.js`**: The JavaScript runtime environment required to run the Next.js application. (Implicit dependency, version specified in development environment).

## API & Data Fetching

*   **`@trpc/client`, `@trpc/next`, `@trpc/react-query`, `@trpc/server`**: End-to-end typesafe API framework. Simplifies communication between the frontend (`react-query`, `client`) and backend (`server`), ensuring type consistency. Integrated with Next.js (`next`).
*   **`@tanstack/react-query`**: Powerful data-fetching and state management library for React. Used by tRPC (`@trpc/react-query`) to handle caching, background updates, and server state synchronization on the client.
*   **`zod`**: TypeScript-first schema declaration and validation library. Used extensively by tRPC for validating API inputs and outputs.
*   **`superjson`**: Serializes JavaScript data types (like Dates, Maps, Sets) that are not supported by standard JSON, often used with tRPC.

## Database & ORM

*   **`@prisma/client`**: Auto-generated and type-safe database client for Node.js & TypeScript. Used to interact with the PostgreSQL database defined in the schema.
*   **`prisma`**: The Prisma CLI tool used for database migrations, schema management, and client generation. (Used in `devDependencies`).

## Authentication

*   **`next-auth`**: Complete authentication solution for Next.js applications. Handles various authentication strategies (Credentials, OAuth).
*   **`@next-auth/prisma-adapter`**: Adapter to connect NextAuth.js with Prisma for storing user, session, and account data in the database.

## UI & Styling

*   **`tailwindcss`**: A utility-first CSS framework for rapidly building custom user interfaces.
*   **`@radix-ui/*`**: Collection of unstyled, accessible UI primitives (e.g., `Dialog`, `DropdownMenu`, `Select`). Used as the foundation for `shadcn/ui`.
*   **`shadcn/ui`**: (Not a direct dependency, but configured via `components.json` and uses Radix + Tailwind). Re-usable UI components built using Radix UI and Tailwind CSS, copied into the project (`src/components/ui/`).
*   **`lucide-react`**: Library providing a wide range of SVG icons as React components.
*   **`class-variance-authority` (cva)**: Utility for creating type-safe variant classes, often used with Tailwind CSS for component variations.
*   **`clsx` / `tailwind-merge`**: Utilities for conditionally joining CSS class names and merging Tailwind classes without style conflicts.
*   **`next-themes`**: Manages theme switching (e.g., light/dark mode) in Next.js applications.
*   **`tailwindcss-animate`**: Tailwind CSS plugin for adding enter/exit animations.
*   **`autoprefixer` / `postcss`**: Tools for processing CSS, used by Tailwind CSS for vendor prefixing and other transformations. (Used in `devDependencies`).

## AI Integration

*   **`ai` / `@ai-sdk/react` / `@ai-sdk/openai`**: Vercel AI SDK components. Provides tools for integrating Large Language Models (LLMs) into React/Next.js applications, including streaming UI updates (`@ai-sdk/react`) and specific provider integration (`@ai-sdk/openai`).

## Forms

*   **`react-hook-form`**: Performant, flexible, and extensible forms library for React.
*   **`@hookform/resolvers`**: Adapter to use validation libraries like Zod with `react-hook-form`.

## Utilities & Linting/Formatting

*   **`date-fns`**: Modern JavaScript date utility library.
*   **`react-markdown`**: React component to render Markdown as HTML.
*   **`@t3-oss/env-nextjs`**: Schema validation for environment variables in Next.js projects (used in `src/env.js`).
*   **`eslint` / `@typescript-eslint/*`**: Linter for identifying and reporting patterns in JavaScript/TypeScript code. (Used in `devDependencies`).
*   **`prettier` / `prettier-plugin-tailwindcss`**: Opinionated code formatter to ensure consistent code style. (Used in `devDependencies`).
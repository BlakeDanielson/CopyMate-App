# 10. Configuration Management

This section explains how application configuration, particularly environment variables, is managed in the `blvke-chat-app`.

## Environment Variables (`.env`)

Configuration specific to the deployment environment (development, production, preview) is handled using environment variables.

*   **`.env.example`**: This file serves as a template listing all the required environment variables for the application to run. It contains placeholder or default values. **This file should be committed to version control.**
*   **`.env`**: This file contains the actual values for the environment variables used during local development. It is created by copying `.env.example` (`cp .env.example .env`) and filling in the appropriate values (database URLs, API keys, secrets, etc.). **This file MUST NOT be committed to version control** and is listed in `.gitignore`.
*   **Production/Preview Environments:** On deployment platforms like Vercel, environment variables are set directly through the platform's dashboard or CLI, not by uploading a `.env` file. These platform-provided variables take precedence.

## Environment Variable Validation (`src/env.js`)

To ensure type safety and the presence of required environment variables at runtime, the project uses the `@t3-oss/env-nextjs` library.

*   **File:** `src/env.js` (or potentially `src/env.mjs`)
*   **Library:** `@t3-oss/env-nextjs`
*   **Validation Schema:** Inside `src/env.js`, Zod schemas are defined to specify the expected type and presence of each environment variable.
    *   `server`: Defines variables accessible only on the server-side (e.g., `DATABASE_URL`, `OPENAI_API_KEY`, `NEXTAUTH_SECRET`).
    *   `client`: Defines variables that need to be exposed to the client-side browser bundle. These variables **must** be prefixed with `NEXT_PUBLIC_`.
    *   `runtimeEnv`: Maps the schema keys to the actual `process.env` variables.
*   **Process:** When the application starts, `createEnv` from `@t3-oss/env-nextjs` validates `process.env` against the defined Zod schema.
    *   If any server-side variable is missing or has the wrong type, the build process or server startup will fail immediately, preventing runtime errors due to misconfiguration.
    *   Client-side variables are similarly validated.
*   **Accessing Variables:** The validated and typed environment variables are exported from `src/env.js` as the `env` object. This object should be imported and used throughout the application instead of accessing `process.env` directly, providing type safety and autocompletion.

```javascript
// Example usage (inside server-side code):
import { env } from "@/env.js";

const dbUrl = env.DATABASE_URL; // Type-safe access
const apiKey = env.OPENAI_API_KEY;

// Example usage (inside client-side code):
import { env } from "@/env.js";

const publicApi = env.NEXT_PUBLIC_ANALYTICS_ID; // Type-safe access
```

This setup ensures that the application fails fast if configuration is missing or incorrect, and provides a type-safe way to access environment variables throughout the codebase.
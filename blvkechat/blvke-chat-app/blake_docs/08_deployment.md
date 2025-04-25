# 8. Deployment Process

This section outlines the steps for building and deploying the `blvke-chat-app`. The primary recommended deployment platform is Vercel, given its seamless integration with Next.js.

## Building for Production

Before deployment, create a production-optimized build of the application:

```bash
npm run build
```

This command executes `next build`, which compiles the Next.js application, including:
*   Bundling React code.
*   Optimizing assets (JavaScript, CSS, images).
*   Generating static pages and serverless functions.
*   Running Prisma generate (`postinstall` script ensures Prisma Client is up-to-date).

The output is placed in the `.next` directory.

## Testing (If Applicable)

Currently, there are no dedicated test scripts defined in `package.json` (e.g., `npm test`). If automated tests (unit, integration, end-to-end) are added later using frameworks like Jest, Vitest, Cypress, or Playwright, they should be run before deployment:

```bash
# Example: Assuming a test script is added
npm test
```

Ensure all tests pass before proceeding with deployment.

## Deployment to Vercel (Recommended)

Vercel is the platform developed by the creators of Next.js and offers the most streamlined deployment experience.

1.  **Prerequisites:**
    *   A Vercel account ([https://vercel.com/signup](https://vercel.com/signup)).
    *   Git repository hosted on GitHub, GitLab, or Bitbucket.

2.  **Import Project:**
    *   Log in to your Vercel dashboard.
    *   Click "Add New..." -> "Project".
    *   Connect your Git provider if you haven't already.
    *   Select the `blvke-chat-app` repository.

3.  **Configure Project:**
    *   **Framework Preset:** Vercel should automatically detect "Next.js".
    *   **Build Command:** Should default to `npm run build` (or `next build`). Verify this is correct.
    *   **Output Directory:** Should default to `.next`. Verify this.
    *   **Install Command:** Should default to `npm install`. Verify this.

4.  **Environment Variables:**
    *   Navigate to the project's "Settings" -> "Environment Variables" section in Vercel.
    *   Add all the necessary environment variables defined in your `.env.example` file. **Crucially, you MUST provide production values for:**
        *   `DATABASE_URL`: Connection string for your **production** PostgreSQL database (e.g., Vercel Postgres, Neon, Supabase, Aiven, AWS RDS).
        *   `NEXTAUTH_SECRET`: A strong, unique secret generated specifically for production. **DO NOT reuse the development secret.**
        *   `NEXTAUTH_URL`: The canonical URL of your deployed application (e.g., `https://your-app-name.vercel.app`).
        *   `OPENAI_API_KEY`: Your production OpenAI API key.
        *   Any other required keys (e.g., OAuth provider client IDs/secrets).
    *   Ensure variables are set for the "Production" environment (and potentially "Preview" and "Development" if needed for Vercel's preview deployments).

5.  **Deploy:**
    *   Click the "Deploy" button.
    *   Vercel will clone the repository, install dependencies, run the build command, and deploy the application.
    *   Subsequent pushes to the connected Git branch (e.g., `main`) will automatically trigger new deployments.

## Other Deployment Options

While Vercel is recommended, you can deploy the application to other platforms that support Node.js applications:

*   **Docker:** You can create a `Dockerfile` to containerize the application (using the production build from `npm run build` and running `npm run start`). This container can then be deployed to platforms like AWS ECS, Google Cloud Run, Kubernetes, etc.
*   **Node.js Server:** Deploy the output of `npm run build` to a traditional Node.js server environment (like AWS EC2, DigitalOcean Droplet) using a process manager like PM2 (`pm2 start npm --name blvke-chat-app -- start`).

**Important Considerations for Other Platforms:**

*   **Environment Variables:** Ensure all required environment variables are securely configured on the target platform.
*   **Database:** Provision and configure a production PostgreSQL database accessible from your deployment environment.
*   **HTTPS:** Configure HTTPS, typically using a reverse proxy like Nginx or Caddy, or platform-provided load balancers.
*   **Build Process:** Ensure the `npm run build` command is executed as part of your deployment pipeline.
# LLM Chatbot with T3 Stack

This is a full-featured LLM chatbot application built with the T3 Stack (TypeScript, tRPC, Tailwind).

## Tech Stack

- **Framework**: [Next.js](https://nextjs.org)
- **Language**: [TypeScript](https://www.typescriptlang.org)
- **Styling**: [Tailwind CSS](https://tailwindcss.com)
- **UI Components**: [shadcn/ui](https://ui.shadcn.com)
- **API Layer**: [tRPC](https://trpc.io)
- **Database ORM**: [Prisma](https://prisma.io)
- **Database**: PostgreSQL
- **Authentication**: [NextAuth.js](https://next-auth.js.org)
- **Validation**: [Zod](https://zod.dev)
- **AI Integration**: [AI SDK](https://sdk.vercel.ai)

## Features

- User authentication (email/password, GitHub, Google)
- Conversation management
- Message history
- AI integration with OpenAI models
- Customizable settings
- Responsive design
- Dark mode
- Type-safe API with tRPC
- Database integration with Prisma

## Getting Started

1. Clone the repository
2. Install dependencies: `npm install`
3. Set up environment variables (see `.env.example`)
4. Set up the database: `npx prisma db push`
5. Start the development server: `npm run dev`
6. Open [http://localhost:3000](http://localhost:3000) in your browser

## Environment Variables

Create a `.env` file with the following variables:

\`\`\`
# Database
DATABASE_URL="postgresql://..."

# NextAuth
NEXTAUTH_SECRET="your-secret"
NEXTAUTH_URL="http://localhost:3000"

# OAuth Providers
GITHUB_CLIENT_ID="your-github-client-id"
GITHUB_CLIENT_SECRET="your-github-client-secret"
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"

# OpenAI
OPENAI_API_KEY="your-openai-api-key"
\`\`\`

## Development

This project uses the T3 Stack, which provides a set of tools for building type-safe, full-stack applications.

- **tRPC**: Type-safe API layer
- **Prisma**: Type-safe database ORM
- **NextAuth.js**: Authentication
- **Tailwind CSS**: Styling
- **shadcn/ui**: UI components

## Deployment

This project can be deployed to Vercel with minimal configuration.

1. Push your code to a GitHub repository
2. Import the repository to Vercel
3. Set up the environment variables
4. Deploy!

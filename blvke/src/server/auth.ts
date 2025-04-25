import { PrismaAdapter } from "@next-auth/prisma-adapter"
import type { GetServerSidePropsContext } from "next"
import { getServerSession, type DefaultSession, type NextAuthOptions } from "next-auth"
import GitHubProvider from "next-auth/providers/github"
import GoogleProvider from "next-auth/providers/google"
import CredentialsProvider from "next-auth/providers/credentials"
import { env } from "@/env.mjs"
import { db } from "@/server/db"
import { z } from "zod"

/**
 * Module augmentation for `next-auth` types. Allows us to add custom properties to the `session`
 * object and keep type safety.
 *
 * @see https://next-auth.js.org/getting-started/typescript#module-augmentation
 */
declare module "next-auth" {
  interface Session extends DefaultSession {
    user: DefaultSession["user"] & {
      id: string
      // ...other properties
      // role: UserRole;
    }
  }

  // interface User {
  //   // ...other properties
  //   // role: UserRole;
  // }
}

/**
 * Options for NextAuth.js used to configure adapters, providers, callbacks, etc.
 *
 * @see https://next-auth.js.org/configuration/options
 */
export const authOptions: NextAuthOptions = {
  callbacks: {
    session: ({ session, user, token }) => {
      if (user) {
        return {
          ...session,
          user: {
            ...session.user,
            id: user.id,
          },
        }
      }
      return {
        ...session,
        user: {
          ...session.user,
          id: token.sub || "unknown",
        },
      }
    },
  },
  adapter: PrismaAdapter(db),
  providers: [
    GitHubProvider({
      clientId: env.GITHUB_CLIENT_ID || "",
      clientSecret: env.GITHUB_CLIENT_SECRET || "",
    }),
    GoogleProvider({
      clientId: env.GOOGLE_CLIENT_ID || "",
      clientSecret: env.GOOGLE_CLIENT_SECRET || "",
    }),
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const credentialsSchema = z.object({
          email: z.string().email(),
          password: z.string().min(6),
        })

        const parsedCredentials = credentialsSchema.safeParse(credentials)

        if (!parsedCredentials.success) {
          return null
        }

        // For demo purposes, allow test@example.com/password
        if (parsedCredentials.data.email === "test@example.com" && parsedCredentials.data.password === "password") {
          return {
            id: "test-user-id",
            name: "Test User",
            email: "test@example.com",
            image: null,
          }
        }

        // In a real app, you would verify against the database
        // const user = await db.user.findUnique({
        //   where: { email: parsedCredentials.data.email }
        // });

        // if (!user || !await verifyPassword(user.password, parsedCredentials.data.password)) {
        //   return null;
        // }

        // return user;

        return null
      },
    }),
  ],
  pages: {
    signIn: "/login",
  },
  session: {
    strategy: "jwt",
  },
  secret: env.NEXTAUTH_SECRET || env.JWT_SECRET,
}

/**
 * Wrapper for `getServerSession` so that you don't need to import the `authOptions` in every file.
 *
 * @see https://next-auth.js.org/configuration/nextjs
 */
export const getServerAuthSession = (ctx: {
  req: GetServerSidePropsContext["req"]
  res: GetServerSidePropsContext["res"]
}) => {
  return getServerSession(ctx.req, ctx.res, authOptions)
}

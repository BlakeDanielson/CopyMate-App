/**
 * Prisma client singleton
 */

// Import from the custom output directory specified in schema.prisma
import { PrismaClient } from '../generated/prisma';
import path from 'path';
import fs from 'fs';

// Create directory for prisma client if it doesn't exist
const generatedDir = path.join(__dirname, '..', 'generated');
const prismaDir = path.join(generatedDir, 'prisma');

if (!fs.existsSync(generatedDir)) {
  fs.mkdirSync(generatedDir, { recursive: true });
}

if (!fs.existsSync(prismaDir)) {
  fs.mkdirSync(prismaDir, { recursive: true });
}

// Use a single PrismaClient instance across the application
const globalForPrisma = global as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
  });

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

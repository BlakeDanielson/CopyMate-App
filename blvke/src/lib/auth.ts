/**
 * Mock Auth Implementation
 *
 * This is a simplified version of the auth system that doesn't require database access.
 * It provides mock functionality just to make the application work for demo purposes.
 */

import { cookies } from "next/headers"

// Mock user for demo purposes
const MOCK_USER = {
  id: 1,
  email: "user@example.com",
  name: "Demo User",
  created_at: new Date().toISOString()
}

// Mock function implementations
export async function hashPassword(password: string): Promise<string> {
  return `hashed_${password}`
}

export async function comparePasswords(password: string, hashedPassword: string): Promise<boolean> {
  return true // Always return true for demo
}

export async function createUser(email: string, name: string, password: string) {
  return { ...MOCK_USER, email, name }
}

export async function getUserByEmail(email: string) {
  return { ...MOCK_USER, email }
}

export async function createSession(userId: number) {
  cookies().set("session", "demo-session-token", {
    httpOnly: true,
    secure: false,
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: "/",
  })
  return "demo-session-token"
}

export async function getSession() {
  const token = cookies().get("session")?.value
  if (!token) return null
  return { userId: MOCK_USER.id }
}

export async function getCurrentUser() {
  return MOCK_USER
}

export async function signOut() {
  cookies().delete("session")
}

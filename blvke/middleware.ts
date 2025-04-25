import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const isAuthenticated = request.cookies.has("session")

  // Public routes
  const publicRoutes = ["/login", "/register"]

  // Auth routes that require authentication
  const authRoutes = ["/chat", "/settings", "/history"]

  // Root path should redirect to chat if authenticated, login if not
  if (pathname === "/") {
    return NextResponse.redirect(new URL(isAuthenticated ? "/chat" : "/login", request.url))
  }

  // Redirect authenticated users away from public routes
  if (isAuthenticated && publicRoutes.some((route) => pathname.startsWith(route))) {
    return NextResponse.redirect(new URL("/chat", request.url))
  }

  // Redirect unauthenticated users away from protected routes
  if (!isAuthenticated && authRoutes.some((route) => pathname.startsWith(route))) {
    return NextResponse.redirect(new URL("/login", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}

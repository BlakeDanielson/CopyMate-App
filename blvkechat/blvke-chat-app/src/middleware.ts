import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const isAuthenticated = request.cookies.has("session")
  console.log(`[Middleware] Pathname: ${pathname}, Authenticated: ${isAuthenticated}`)

  // Public routes
  const publicRoutes = ["/login", "/register", "/landing"]

  // Auth routes that require authentication
  const authRoutes = ["/chat", "/settings", "/history"]

  // Root path should redirect to landing if not authenticated, chat if authenticated
  if (pathname === "/") {
    const redirectUrl = isAuthenticated ? "/chat" : "/landing"
    console.log(`[Middleware] Root path detected. Redirecting to ${redirectUrl}`)
    return NextResponse.redirect(new URL(redirectUrl, request.url))
  }

  // Redirect authenticated users away from public routes (except landing)
  if (isAuthenticated && publicRoutes.some((route) => pathname.startsWith(route)) && pathname !== "/landing") {
    console.log(`[Middleware] Authenticated user accessing public route ${pathname}. Redirecting to /chat`)
    return NextResponse.redirect(new URL("/chat", request.url))
  }

  // Redirect unauthenticated users away from protected routes
  if (!isAuthenticated && authRoutes.some((route) => pathname.startsWith(route))) {
    console.log(`[Middleware] Unauthenticated user accessing protected route ${pathname}. Redirecting to /login`)
    return NextResponse.redirect(new URL("/login", request.url))
  }

  // Specific check for /landing
  if (pathname === "/landing") {
    console.log("[Middleware] Accessing /landing. Allowing request.")
  }

  console.log(`[Middleware] No redirect conditions met for ${pathname}. Allowing request.`)
  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}

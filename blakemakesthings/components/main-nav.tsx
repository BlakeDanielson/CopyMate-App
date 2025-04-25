"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Menu, X, ChevronDown } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { ThemeToggle } from "@/components/theme-toggle"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

// Update routes structure to include dropdown
const routes = [
  { href: "/", label: "Home" },
  { href: "/about", label: "About" },
  { href: "/projects", label: "Projects" },
  {
    label: "Fun Things",
    dropdown: true,
    items: [
      { href: "/music", label: "Music" },
      { href: "/business-musings", label: "Business Musings" },
      { href: "/my-story", label: "My Story" },
    ],
  },
  { href: "/contact", label: "Contact" },
]

export function MainNav() {
  const pathname = usePathname()
  const [open, setOpen] = React.useState(false)

  return (
    <header className="fixed top-0 z-50 w-full border-b border-zinc-800 bg-black/80 backdrop-blur-md">
      <div className="container flex h-16 items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2 text-lg font-medium text-white">
          <div className="relative flex h-8 w-8 items-center justify-center rounded-full bg-purple-900/80 text-white">
            <div className="absolute inset-0 animate-pulse rounded-full bg-purple-500 opacity-60 blur-sm"></div>
            <span className="relative z-10">BD</span>
          </div>
          <span className="hidden sm:inline-block">Blake Danielson</span>
        </Link>

        <div className="flex items-center gap-4">
          {/* Desktop Navigation */}
          <nav className="hidden md:flex md:gap-6">
            {routes.map((route, index) =>
              route.dropdown ? (
                <DropdownMenu key={index}>
                  <DropdownMenuTrigger className="flex items-center gap-1 text-sm font-medium text-zinc-400 transition-colors hover:text-purple-400">
                    {route.label}
                    <ChevronDown className="h-4 w-4" />
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="border-zinc-800 bg-zinc-900">
                    {route.items?.map((item) => (
                      <DropdownMenuItem key={item.href} asChild>
                        <Link
                          href={item.href}
                          className={`w-full px-2 py-1.5 text-sm transition-colors hover:bg-zinc-800 hover:text-purple-400 ${
                            pathname === item.href ? "text-purple-500" : "text-zinc-400"
                          }`}
                        >
                          {item.label}
                        </Link>
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <Link
                  key={route.href}
                  href={route.href}
                  className={`text-sm font-medium transition-colors hover:text-purple-400 ${
                    pathname === route.href ? "text-purple-500" : "text-zinc-400"
                  }`}
                >
                  {route.label}
                </Link>
              ),
            )}
          </nav>

          <ThemeToggle />

          {/* Mobile Navigation */}
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden">
                <Menu className="h-5 w-5 text-white" />
                <span className="sr-only">Toggle menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="border-zinc-800 bg-black">
              <div className="flex items-center justify-between">
                <Link href="/" className="flex items-center gap-2 text-lg font-medium text-white">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-900/80 text-white">
                    <div className="absolute inset-0 animate-pulse rounded-full bg-purple-500 opacity-60 blur-sm"></div>
                    <span className="relative z-10">BD</span>
                  </div>
                  <span className="hidden sm:inline-block">Blake Danielson</span>
                </Link>
                <Button variant="ghost" size="icon" onClick={() => setOpen(false)}>
                  <X className="h-5 w-5 text-white" />
                  <span className="sr-only">Close menu</span>
                </Button>
              </div>
              <nav className="mt-8 flex flex-col gap-6">
                {routes.map((route, index) =>
                  route.dropdown ? (
                    <div key={index} className="space-y-3">
                      <p className="text-xl font-medium text-purple-500">{route.label}</p>
                      <div className="ml-4 flex flex-col gap-3">
                        {route.items?.map((item) => (
                          <Link
                            key={item.href}
                            href={item.href}
                            className={`text-lg transition-colors hover:text-purple-400 ${
                              pathname === item.href ? "text-purple-500" : "text-zinc-400"
                            }`}
                            onClick={() => setOpen(false)}
                          >
                            {item.label}
                          </Link>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <Link
                      key={route.href}
                      href={route.href}
                      className={`text-xl font-medium transition-colors hover:text-purple-400 ${
                        pathname === route.href ? "text-purple-500" : "text-zinc-400"
                      }`}
                      onClick={() => setOpen(false)}
                    >
                      {route.label}
                    </Link>
                  ),
                )}
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}

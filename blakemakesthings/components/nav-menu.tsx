"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Menu } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"

const routes = [
  { href: "/", label: "Home" },
  { href: "/projects", label: "Projects" },
  { href: "/about", label: "About" },
  { href: "/contact", label: "Contact" },
]

export function NavMenu() {
  const pathname = usePathname()
  const [open, setOpen] = React.useState(false)

  return (
    <>
      {/* Mobile Navigation */}
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon" className="md:hidden">
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="right" className="w-[300px] sm:w-[400px]">
          <nav className="flex flex-col gap-4">
            {routes.map((route) => (
              <Link
                key={route.href}
                href={route.href}
                className={`text-xl font-medium ${
                  pathname === route.href ? "text-teal-600 dark:text-teal-400" : "text-zinc-600 dark:text-zinc-400"
                }`}
                onClick={() => setOpen(false)}
              >
                {route.label}
              </Link>
            ))}
          </nav>
        </SheetContent>
      </Sheet>

      {/* Desktop Navigation */}
      <nav className="hidden md:flex md:gap-6">
        {routes.map((route) => (
          <Link
            key={route.href}
            href={route.href}
            className={`text-sm font-medium transition-colors hover:text-teal-600 dark:hover:text-teal-400 ${
              pathname === route.href ? "text-teal-600 dark:text-teal-400" : "text-zinc-600 dark:text-zinc-400"
            }`}
          >
            {route.label}
          </Link>
        ))}
      </nav>
    </>
  )
}

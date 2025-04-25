"use client"
import Link from "next/link"
import { ArrowRight } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { MainNav } from "@/components/main-nav"
import { SiteFooter } from "@/components/site-footer"

export default function MyStoryPage() {
  return (
    <div className="min-h-screen bg-black">
      <MainNav />

      {/* Hero Section */}
      <div className="relative bg-zinc-900 pt-24">
        <div className="absolute inset-0 bg-grid-white/5 opacity-50"></div>
        <div className="absolute inset-0 bg-gradient-to-b from-black/50 to-zinc-900"></div>

        <div className="container relative z-10 mx-auto px-4 py-16 text-center">
          <Badge className="mb-4 bg-purple-500/20 text-purple-300">Personal Journey</Badge>
          <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl md:text-6xl">
            My <span className="text-purple-400">Story</span>
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-zinc-300">
            The journey, lessons, and pivotal moments that shaped who I am today
          </p>

          <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-black to-transparent"></div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-4xl">
          {/* Introduction */}
          <div className="mb-16 text-center">
            <p className="text-xl text-zinc-400">
              This page is coming soon. Check back later for the full story of my personal and professional journey.
            </p>
            <div className="mt-8">
              <Link href="/">
                <Button className="bg-purple-600 hover:bg-purple-700">
                  Back to Home
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <SiteFooter />
    </div>
  )
}

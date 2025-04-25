import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Brain, MessageSquare, Zap, Shield, Sparkles, ArrowRight } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Brain className="h-8 w-8 text-violet-600" />
            <span className="text-xl font-bold">AI Chat Assistant</span>
          </div>
          <div className="flex items-center space-x-4">
            <Link href="/login" className="text-gray-600 hover:text-violet-600">
              Login
            </Link>
            <Link href="/register">
              <Button className="bg-violet-600 hover:bg-violet-700">Sign Up</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-b from-white to-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-6 text-gray-900">
              v0.dev Component Added Successfully
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              The component has been integrated into your Next.js application.
            </p>
            <Link href="/landing">
              <Button className="bg-violet-600 hover:bg-violet-700 text-lg px-8 py-6">
                View Full Landing Page
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

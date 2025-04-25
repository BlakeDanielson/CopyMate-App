import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Brain, MessageSquare, Zap, Shield, Sparkles, ArrowRight } from "lucide-react"
import FeatureCard from "@/components/feature-card"
import TestimonialCard from "@/components/testimonial-card"
import ChatbotDemo from "@/components/chatbot-demo"

export default function LandingPage() {
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
        <div className="container mx-auto px-4 flex flex-col lg:flex-row items-center">
          <div className="lg:w-1/2 mb-10 lg:mb-0">
            <h1 className="text-4xl md:text-5xl font-bold mb-6 text-gray-900">
              Your Personal AI Assistant for Everyday Tasks
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Harness the power of advanced AI to boost your productivity, answer questions, and assist with your daily
              tasks.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/register">
                <Button className="bg-violet-600 hover:bg-violet-700 text-lg px-8 py-6">Get Started</Button>
              </Link>
              <Link href="#features">
                <Button variant="outline" className="text-lg px-8 py-6">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
          <div className="lg:w-1/2">
            <ChatbotDemo />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Powerful Features</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our AI assistant comes packed with features designed to make your life easier and more productive.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon={<MessageSquare className="h-6 w-6 text-violet-600" />}
              title="Natural Conversations"
              description="Engage in natural, human-like conversations with our advanced AI that understands context and nuance."
            />
            <FeatureCard
              icon={<Zap className="h-6 w-6 text-violet-600" />}
              title="Lightning Fast Responses"
              description="Get instant answers to your questions with our high-performance AI processing engine."
            />
            <FeatureCard
              icon={<Shield className="h-6 w-6 text-violet-600" />}
              title="Secure & Private"
              description="Your conversations are encrypted and your data is never shared with third parties."
            />
            <FeatureCard
              icon={<Sparkles className="h-6 w-6 text-violet-600" />}
              title="Smart Suggestions"
              description="Receive intelligent suggestions and recommendations based on your conversation history."
            />
            <FeatureCard
              icon={<Brain className="h-6 w-6 text-violet-600" />}
              title="Continuous Learning"
              description="Our AI gets smarter with every interaction, providing increasingly relevant responses."
            />
            <FeatureCard
              icon={<ArrowRight className="h-6 w-6 text-violet-600" />}
              title="Seamless Integration"
              description="Easily integrate with your favorite apps and services for a streamlined workflow."
            />
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">What Our Users Say</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Thousands of users rely on our AI assistant every day. Here's what some of them have to say.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <TestimonialCard
              quote="This AI assistant has completely transformed how I work. It's like having a personal assistant available 24/7."
              author="Sarah Johnson"
              role="Marketing Director"
              avatarUrl="/thoughtful-gaze.png"
            />
            <TestimonialCard
              quote="The natural language capabilities are impressive. It feels like I'm chatting with a knowledgeable colleague."
              author="Michael Chen"
              role="Software Engineer"
              avatarUrl="/thoughtful-gaze.png"
            />
            <TestimonialCard
              quote="I use this for research, writing, and even creative brainstorming. It's become an essential tool in my workflow."
              author="Emily Rodriguez"
              role="Content Creator"
              avatarUrl="/thoughtful-gaze.png"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-violet-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to Experience the Power of AI?</h2>
          <p className="text-xl mb-8 max-w-3xl mx-auto">
            Join thousands of satisfied users who are already boosting their productivity with our AI assistant.
          </p>
          <Link href="/register">
            <Button className="bg-white text-violet-600 hover:bg-gray-100 text-lg px-8 py-6">
              Get Started for Free
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Brain className="h-6 w-6 text-violet-400" />
                <span className="text-lg font-bold">AI Chat Assistant</span>
              </div>
              <p className="text-gray-400">Your personal AI assistant for everyday tasks.</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Product</h3>
              <ul className="space-y-2">
                <li>
                  <a href="#features" className="text-gray-400 hover:text-white">
                    Features
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white">
                    Pricing
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white">
                    API
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Resources</h3>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="text-gray-400 hover:text-white">
                    Documentation
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white">
                    Blog
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white">
                    Support
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Company</h3>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="text-gray-400 hover:text-white">
                    About
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white">
                    Careers
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white">
                    Contact
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
            <p>&copy; {new Date().getFullYear()} AI Chat Assistant. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

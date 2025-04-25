"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { ArrowLeft, Mail, MessageSquare, Phone, Send } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"

export default function ContactPage() {
  const { toast } = useToast()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsSubmitting(true)

    // Simulate form submission
    await new Promise((resolve) => setTimeout(resolve, 1500))

    setIsSubmitting(false)
    toast({
      title: "Message sent!",
      description: "Thank you for your message. I'll get back to you soon.",
    })

    // Reset form
    e.currentTarget.reset()
  }

  return (
    <div className="container py-12 pt-24 md:py-24">
      <div className="mx-auto max-w-4xl">
        <Link
          href="/"
          className="inline-flex items-center text-sm text-zinc-600 hover:text-purple-600 dark:text-zinc-400 dark:hover:text-purple-400"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Home
        </Link>

        <div className="mt-8">
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">Get in Touch</h1>
          <p className="mt-4 text-xl text-zinc-600 dark:text-zinc-400">
            I'd love to hear from you! Whether you have a project in mind or just want to connect.
          </p>
        </div>

        <div className="mt-12 grid gap-12 md:grid-cols-2">
          <div>
            <div className="space-y-8">
              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-100 text-purple-600 dark:bg-purple-900/50 dark:text-purple-400">
                  <Mail className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold">Email</h3>
                  <p className="mt-1 text-zinc-600 dark:text-zinc-400">blakejdanielson@gmail.com</p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-100 text-purple-600 dark:bg-purple-900/50 dark:text-purple-400">
                  <Phone className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold">Phone</h3>
                  <p className="mt-1 text-zinc-600 dark:text-zinc-400">(925) 324-9491</p>
                  <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-500">Available weekdays 9am-5pm PST</p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-100 text-purple-600 dark:bg-purple-900/50 dark:text-purple-400">
                  <MessageSquare className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold">Social Media</h3>
                  <div className="mt-1 space-y-1 text-zinc-600 dark:text-zinc-400">
                    <p>
                      <a
                        href="https://www.linkedin.com/in/blakedan97/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-purple-600 hover:underline dark:text-purple-400"
                      >
                        LinkedIn
                      </a>
                    </p>
                    <p>
                      <a
                        href="https://github.com/BlakeDanielson"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-purple-600 hover:underline dark:text-purple-400"
                      >
                        GitHub
                      </a>
                    </p>
                    <p>
                      <a
                        href="https://soundcloud.com/blvkemusic"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-purple-600 hover:underline dark:text-purple-400"
                      >
                        SoundCloud
                      </a>
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-12 rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-800/50">
              <h3 className="text-lg font-bold">Let's grab a virtual coffee</h3>
              <p className="mt-2 text-zinc-600 dark:text-zinc-400">
                I'm always open to connecting with fellow tech enthusiasts, potential collaborators, or anyone
                interested in AI and product development.
              </p>
              <a
                href="https://calendly.com"
                target="_blank"
                rel="noopener noreferrer"
                className="mt-4 inline-flex items-center text-purple-600 hover:underline dark:text-purple-400"
              >
                Schedule a 30-minute chat
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="ml-1 h-4 w-4"
                >
                  <path d="M7 7h10v10" />
                  <path d="M7 17 17 7" />
                </svg>
              </a>
            </div>
          </div>

          <div className="rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-800/50">
            <h2 className="text-xl font-bold">Send a Message</h2>
            <p className="mt-2 text-zinc-600 dark:text-zinc-400">
              Have a specific question or project in mind? Fill out the form below.
            </p>

            <form onSubmit={handleSubmit} className="mt-6 space-y-6">
              <div className="space-y-2">
                <label htmlFor="name" className="text-sm font-medium">
                  Name
                </label>
                <Input
                  id="name"
                  name="name"
                  required
                  className="border-zinc-300 focus:border-purple-500 focus:ring-purple-500 dark:border-zinc-700 dark:focus:border-purple-400 dark:focus:ring-purple-400"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Email
                </label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  required
                  className="border-zinc-300 focus:border-purple-500 focus:ring-purple-500 dark:border-zinc-700 dark:focus:border-purple-400 dark:focus:ring-purple-400"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="subject" className="text-sm font-medium">
                  Subject
                </label>
                <Input
                  id="subject"
                  name="subject"
                  required
                  className="border-zinc-300 focus:border-purple-500 focus:ring-purple-500 dark:border-zinc-700 dark:focus:border-purple-400 dark:focus:ring-purple-400"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="message" className="text-sm font-medium">
                  Message
                </label>
                <Textarea
                  id="message"
                  name="message"
                  rows={5}
                  required
                  className="border-zinc-300 focus:border-purple-500 focus:ring-purple-500 dark:border-zinc-700 dark:focus:border-purple-400 dark:focus:ring-purple-400"
                />
              </div>

              <Button
                type="submit"
                className="w-full bg-purple-600 hover:bg-purple-700 dark:bg-purple-600 dark:hover:bg-purple-700"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <span className="flex items-center">
                    <svg
                      className="mr-2 h-4 w-4 animate-spin"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Sending...
                  </span>
                ) : (
                  <span className="flex items-center">
                    <Send className="mr-2 h-4 w-4" />
                    Send Message
                  </span>
                )}
              </Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

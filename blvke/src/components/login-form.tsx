"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useToast } from "@/components/ui/use-toast"
import { AtSign, Lock } from "lucide-react"

export default function LoginForm() {
  const router = useRouter()
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Login failed")
      }

      router.push("/chat")
      router.refresh()
    } catch (error: any) {
      console.error("Login error:", error)
      toast({
        title: "Login Error",
        description: error.message || "Failed to login. Please try again.",
        variant: "destructive",
      })

      // If we're in test mode, provide additional guidance
      if (formData.email === "test@example.com") {
        toast({
          title: "Test Mode Troubleshooting",
          description: "Make sure you're using the exact credentials: test@example.com / password",
          variant: "default",
        })
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="email" className="text-foreground">
          Email
        </Label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <AtSign className="h-5 w-5 text-muted-foreground" />
          </div>
          <Input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={formData.email}
            onChange={handleChange}
            className="pl-10 bg-secondary/50 border-secondary text-foreground"
            placeholder="you@example.com"
          />
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="password" className="text-foreground">
            Password
          </Label>
          <Link href="#" className="text-sm text-primary hover:text-primary/80">
            Forgot password?
          </Link>
        </div>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <Lock className="h-5 w-5 text-muted-foreground" />
          </div>
          <Input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            value={formData.password}
            onChange={handleChange}
            className="pl-10 bg-secondary/50 border-secondary text-foreground"
            placeholder="••••••••"
          />
        </div>
      </div>

      <Button type="submit" className="w-full bg-primary hover:bg-primary/90" disabled={loading}>
        {loading ? "Signing in..." : "Sign in"}
      </Button>

      <div className="text-center text-sm text-muted-foreground">
        Don't have an account?{" "}
        <Link href="/register" className="text-primary hover:text-primary/80">
          Sign up
        </Link>
      </div>
    </form>
  )
}

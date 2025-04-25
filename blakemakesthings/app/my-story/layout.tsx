import type React from "react"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "My Story | Blake Danielson",
  description: "The personal journey, lessons, and pivotal moments that shaped Blake Danielson.",
}

export default function MyStoryLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return <>{children}</>
}

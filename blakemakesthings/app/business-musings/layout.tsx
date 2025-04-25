import type React from "react"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Business Musings | Blake Danielson",
  description: "Insights, observations, and wisdom gathered from the business world by Blake Danielson.",
}

export default function BusinessMusingsLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return <>{children}</>
}

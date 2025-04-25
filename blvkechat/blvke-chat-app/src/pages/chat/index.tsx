"use client"

import { useSession } from "next-auth/react"
import { useRouter } from "next/router"
import { useEffect } from "react"
import ChatInterface from "@/components/chat-interface"

export default function ChatPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const { id } = router.query

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login")
    }
  }, [status, router])

  if (status === "loading") {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
      </div>
    )
  }

  if (!session) {
    return null
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <ChatInterface user={session.user} initialConversationId={typeof id === "string" ? id : undefined} />
    </div>
  )
}

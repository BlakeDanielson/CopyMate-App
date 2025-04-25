import { redirect } from "next/navigation"
import { getCurrentUser } from "@/lib/auth"
import { getConversation } from "@/lib/conversations"
import ChatInterface from "@/components/chat-interface"

export default async function ChatPage({
  searchParams,
}: {
  searchParams: { id?: string }
}) {
  const user = await getCurrentUser()

  if (!user) {
    redirect("/login")
  }

  let conversationId: number | undefined

  if (searchParams.id) {
    const id = Number.parseInt(searchParams.id)
    if (!isNaN(id)) {
      // Verify the conversation exists and belongs to the user
      const conversation = await getConversation(id, user.id)
      if (conversation) {
        conversationId = id
      }
    }
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <ChatInterface user={user} initialConversationId={conversationId} />
    </div>
  )
}

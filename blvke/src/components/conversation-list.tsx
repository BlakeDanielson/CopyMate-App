"use client"

import type React from "react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Pin, Trash, MessageSquare } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { formatDistanceToNow } from "date-fns"
import { api } from "@/utils/api"

interface ConversationListProps {
  userId: string
  onSelectConversation: (id: string, title: string) => void
  selectedConversationId?: string
}

export default function ConversationList({
  userId,
  onSelectConversation,
  selectedConversationId,
}: ConversationListProps) {
  const { toast } = useToast()
  const utils = api.useContext()

  // Fetch conversations
  const { data: conversations, isLoading } = api.conversation.getAll.useQuery()

  // Mutations
  const updateConversation = api.conversation.update.useMutation({
    onSuccess: () => {
      utils.conversation.getAll.invalidate()
    },
  })

  const deleteConversation = api.conversation.delete.useMutation({
    onSuccess: () => {
      utils.conversation.getAll.invalidate()
    },
  })

  const togglePin = async (id: string, isPinned: boolean, e: React.MouseEvent) => {
    e.stopPropagation()

    try {
      await updateConversation.mutateAsync({
        id,
        isPinned: !isPinned,
      })

      toast({
        title: !isPinned ? "Conversation pinned" : "Conversation unpinned",
        description: !isPinned ? "The conversation has been pinned to the top." : "The conversation has been unpinned.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update conversation. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()

    if (!confirm("Are you sure you want to delete this conversation?")) return

    try {
      await deleteConversation.mutateAsync({ id })

      toast({
        title: "Conversation deleted",
        description: "The conversation has been permanently deleted.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete conversation. Please try again.",
        variant: "destructive",
      })
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex items-center gap-2">
            <Skeleton className="h-10 w-full bg-secondary/50" />
          </div>
        ))}
      </div>
    )
  }

  if (!conversations || conversations.length === 0) {
    return (
      <div className="text-center py-4">
        <MessageSquare className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
        <p className="text-muted-foreground">No conversations yet</p>
        <p className="text-sm text-muted-foreground">Start a new chat to begin</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {conversations.map((conversation) => (
        <div key={conversation.id} className="flex items-center gap-2 group">
          <Button
            variant={selectedConversationId === conversation.id ? "secondary" : "ghost"}
            className={`w-full justify-start text-left truncate h-auto py-2 ${
              selectedConversationId === conversation.id
                ? "bg-secondary text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
            onClick={() => onSelectConversation(conversation.id, conversation.title)}
          >
            <div className="flex flex-col items-start">
              <div className="flex items-center gap-1">
                {conversation.isPinned && <Pin size={12} className="text-primary" />}
                <span className="truncate font-medium">{conversation.title}</span>
              </div>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <span>{conversation.messageCount} messages</span>
                <span>•</span>
                <span>{formatDistanceToNow(new Date(conversation.lastMessageAt), { addSuffix: true })}</span>
              </div>
            </div>
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-foreground hover:bg-secondary"
            onClick={(e) => togglePin(conversation.id, conversation.isPinned, e)}
            title={conversation.isPinned ? "Unpin conversation" : "Pin conversation"}
          >
            <Pin size={16} className={conversation.isPinned ? "fill-primary text-primary" : ""} />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="opacity-0 group-hover:opacity-100 transition-opacity text-red-500 hover:text-red-400 hover:bg-red-900/20"
            onClick={(e) => handleDeleteConversation(conversation.id, e)}
            title="Delete conversation"
          >
            <Trash size={16} />
          </Button>
        </div>
      ))}
    </div>
  )
}

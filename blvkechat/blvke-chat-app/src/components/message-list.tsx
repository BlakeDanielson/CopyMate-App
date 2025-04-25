"use client"

import { useState } from "react"
import { Copy, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import ReactMarkdown from "react-markdown"

interface Message {
  id: string
  role: "user" | "assistant" | "system"
  content: string
}

interface MessageListProps {
  messages: Message[]
}

export default function MessageList({ messages }: MessageListProps) {
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  return (
    <div className="space-y-6">
      {messages.map((message) => (
        <div
          key={message.id}
          className={cn(
            "flex gap-3 p-4 rounded-lg group",
            message.role === "user" ? "bg-secondary/50 border border-border" : "bg-primary/10 border border-primary/20",
          )}
        >
          <div
            className={cn(
              "w-8 h-8 rounded-full flex items-center justify-center text-foreground shrink-0",
              message.role === "user" ? "bg-secondary" : "bg-primary/20",
            )}
          >
            {message.role === "user" ? "U" : "AI"}
          </div>
          <div className="flex-1 overflow-hidden">
            <div className="prose prose-invert prose-sm sm:prose-base max-w-none">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-foreground hover:bg-secondary"
            onClick={() => copyToClipboard(message.content, message.id)}
            title="Copy to clipboard"
          >
            {copiedId === message.id ? <Check size={16} /> : <Copy size={16} />}
          </Button>
        </div>
      ))}
    </div>
  )
}

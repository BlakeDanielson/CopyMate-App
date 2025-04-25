"use client"

import { useState, useRef, useEffect } from "react"
import { useChat } from "@ai-sdk/react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Mic, Send, Settings, Plus, Download, LogOut, Menu, X } from "lucide-react"
import ConversationList from "./conversation-list"
import MessageList from "./message-list"
import { useRouter } from "next/navigation"
import { useToast } from "@/components/ui/use-toast"
import { useMobile } from "@/hooks/use-mobile"

interface ChatInterfaceProps {
  user: {
    id: number
    name: string
    email: string
  }
  initialConversationId?: number
}

export default function ChatInterface({ user, initialConversationId }: ChatInterfaceProps) {
  const router = useRouter()
  const { toast } = useToast()
  const isMobile = useMobile()
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile)
  const [isRecording, setIsRecording] = useState(false)
  const [conversationId, setConversationId] = useState<number | undefined>(initialConversationId)
  const [conversationTitle, setConversationTitle] = useState<string>("New Conversation")
  const messageEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const { messages, input, handleInputChange, handleSubmit, isLoading, error, setMessages } = useChat({
    api: "/api/chat",
    body: {
      conversationId,
      conversationTitle,
    },
    onResponse: (response) => {
      if (!response.ok) {
        toast({
          title: "Error",
          description: "Failed to get a response. Please try again.",
          variant: "destructive",
        })
      }
    },
    onFinish: () => {
      // Scroll to bottom when new message is received
      setTimeout(() => {
        messageEndRef.current?.scrollIntoView({ behavior: "smooth" })
      }, 100)
    },
  })

  // Handle errors
  useEffect(() => {
    if (error) {
      toast({
        title: "Error",
        description: error.message || "Something went wrong. Please try again.",
        variant: "destructive",
      })
    }
  }, [error, toast])

  // Scroll to bottom on initial load
  useEffect(() => {
    messageEndRef.current?.scrollIntoView()
  }, [])

  // Adjust textarea height based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "60px"
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }, [input])

  // Close sidebar on mobile when navigating to a conversation
  useEffect(() => {
    if (isMobile && conversationId) {
      setSidebarOpen(false)
    }
  }, [conversationId, isMobile])

  const handleNewChat = () => {
    setConversationId(undefined)
    setConversationTitle("New Conversation")
    setMessages([])
    router.push("/chat")
    if (isMobile) {
      setSidebarOpen(false)
    }
  }

  const handleSelectConversation = (id: number, title: string) => {
    setConversationId(id)
    setConversationTitle(title)
    router.push(`/chat?id=${id}`)
  }

  const handleExportChat = () => {
    if (messages.length === 0) return

    const content = messages.map((m) => `${m.role === "user" ? "You" : "AI"}: ${m.content}`).join("\n\n")
    const filename = conversationTitle.replace(/[^a-z0-9]/gi, "_").toLowerCase() || "chat-export"

    const blob = new Blob([content], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `${filename}-${new Date().toISOString().split("T")[0]}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast({
      title: "Conversation exported",
      description: "Your conversation has been exported successfully.",
    })
  }

  const handleLogout = async () => {
    try {
      await fetch("/api/auth/logout", { method: "POST" })
      router.push("/login")
      router.refresh()
    } catch (error) {
      console.error("Logout error:", error)
      toast({
        title: "Error",
        description: "Failed to log out. Please try again.",
        variant: "destructive",
      })
    }
  }

  const toggleVoiceRecording = () => {
    // This is a placeholder for voice recording functionality
    // In a real implementation, you would use the Web Speech API or a similar library
    setIsRecording(!isRecording)

    if (!isRecording) {
      // Start recording
      toast({
        title: "Voice recording",
        description: "Voice recording started. Speak clearly into your microphone.",
      })
    } else {
      // Stop recording and process
      toast({
        title: "Processing voice",
        description: "Voice recording stopped. Processing your input...",
      })

      // Simulate processing delay and adding a message
      setTimeout(() => {
        const simulatedText = "This is simulated voice input text."
        handleInputChange({ target: { value: simulatedText } } as any)
      }, 1500)
    }
  }

  return (
    <>
      {/* Mobile header */}
      <header className="lg:hidden bg-background border-b border-border p-4 flex items-center justify-between sticky top-0 z-10">
        <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(!sidebarOpen)}>
          {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
        </Button>
        <h1 className="text-xl font-semibold text-foreground">{conversationTitle}</h1>
        <Button variant="ghost" size="icon" onClick={() => router.push("/settings")}>
          <Settings size={20} />
        </Button>
      </header>

      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } transition-transform duration-300 fixed inset-y-0 left-0 z-20 w-64 bg-background border-r border-border lg:translate-x-0 lg:static lg:h-screen`}
      >
        <div className="flex flex-col h-full">
          <div className="p-4 border-b border-border">
            <Button
              onClick={handleNewChat}
              className="w-full mb-4 flex items-center justify-center gap-2 bg-primary hover:bg-primary/90"
            >
              <Plus size={16} /> New Chat
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            <ConversationList
              userId={user.id}
              onSelectConversation={handleSelectConversation}
              selectedConversationId={conversationId}
            />
          </div>

          <div className="p-4 border-t border-border">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="font-medium text-foreground">{user.name}</p>
                <p className="text-sm text-muted-foreground truncate">{user.email}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="flex-1 border-border text-foreground hover:bg-secondary"
                onClick={() => router.push("/settings")}
              >
                <Settings size={16} className="mr-2" /> Settings
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="flex-1 border-border text-foreground hover:bg-secondary"
                onClick={handleLogout}
              >
                <LogOut size={16} className="mr-2" /> Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col h-screen lg:h-auto">
        {/* Desktop header */}
        <header className="hidden lg:flex bg-background border-b border-border p-4 items-center justify-between">
          <h1 className="text-xl font-semibold text-foreground">{conversationTitle}</h1>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              className="border-border text-foreground hover:bg-secondary"
              onClick={handleExportChat}
              disabled={messages.length === 0}
            >
              <Download size={16} className="mr-2" /> Export
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="border-border text-foreground hover:bg-secondary"
              onClick={() => router.push("/settings")}
            >
              <Settings size={16} className="mr-2" /> Settings
            </Button>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 bg-background">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <h2 className="text-2xl font-bold mb-2 text-foreground">Welcome to AI Chat</h2>
              <p className="text-muted-foreground mb-4">Start a conversation with the AI assistant</p>
              <div className="max-w-md">
                <p className="text-sm text-muted-foreground mb-2">Example questions you can ask:</p>
                <div className="grid gap-2">
                  {[
                    "What are the key features of Next.js?",
                    "Can you explain how React hooks work?",
                    "Write a short story about a robot learning to paint",
                    "Help me debug this code: function sum(a, b) { return a - b; }",
                  ].map((question, i) => (
                    <Button
                      key={i}
                      variant="outline"
                      className="text-left justify-start h-auto py-2 px-3 border-border text-foreground hover:bg-secondary"
                      onClick={() => handleInputChange({ target: { value: question } } as any)}
                    >
                      {question}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <MessageList messages={messages} />
          )}
          <div ref={messageEndRef} />
        </div>

        {/* Input area */}
        <div className="p-4 bg-background border-t border-border">
          <form onSubmit={handleSubmit} className="flex flex-col gap-2">
            <div className="flex items-end gap-2">
              <Textarea
                ref={textareaRef}
                value={input}
                onChange={handleInputChange}
                placeholder="Type your message..."
                className="flex-1 min-h-[60px] max-h-[200px] resize-none bg-secondary/50 border-border text-foreground"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault()
                    handleSubmit(e as any)
                  }
                }}
              />
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={toggleVoiceRecording}
                  className={`border-border ${isRecording ? "bg-red-900/20 text-red-500" : "hover:bg-secondary"}`}
                >
                  <Mic size={20} className={isRecording ? "text-red-500" : ""} />
                </Button>
                <Button
                  type="submit"
                  size="icon"
                  className="bg-primary hover:bg-primary/90"
                  disabled={isLoading || input.trim() === ""}
                >
                  <Send size={20} />
                </Button>
              </div>
            </div>
            {isMobile && (
              <div className="flex justify-end gap-2 mt-2">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={handleExportChat}
                  disabled={messages.length === 0}
                  className="text-foreground hover:bg-secondary"
                >
                  <Download size={16} className="mr-2" /> Export
                </Button>
              </div>
            )}
            {isLoading && <p className="text-sm text-muted-foreground animate-pulse">AI is thinking...</p>}
          </form>
        </div>
      </div>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && isMobile && (
        <div className="fixed inset-0 bg-black/50 z-10 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}
    </>
  )
}

"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Send } from "lucide-react"

export default function ChatbotDemo() {
  const [messages, setMessages] = useState([{ role: "bot", content: "Hi there! How can I help you today?" }])
  const [inputValue, setInputValue] = useState("")
  const [isTyping, setIsTyping] = useState(false)

  const handleSendMessage = () => {
    if (!inputValue.trim()) return

    // Add user message
    setMessages((prev) => [...prev, { role: "user", content: inputValue }])
    setInputValue("")

    // Simulate bot typing
    setIsTyping(true)

    // Simulate bot response after a delay
    setTimeout(() => {
      setIsTyping(false)
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: getBotResponse(inputValue),
        },
      ])
    }, 1500)
  }

  const getBotResponse = (message: string) => {
    const lowerMessage = message.toLowerCase()

    if (lowerMessage.includes("hello") || lowerMessage.includes("hi")) {
      return "Hello! How can I assist you today?"
    } else if (lowerMessage.includes("feature") || lowerMessage.includes("do")) {
      return "I can answer questions, generate content, summarize information, and provide recommendations based on your needs!"
    } else if (lowerMessage.includes("help")) {
      return "I'm here to help! You can ask me questions, request content generation, or inquire about our services."
    } else {
      return "That's an interesting question. As an AI assistant, I'm designed to provide helpful, accurate, and relevant information. Would you like to know more about our capabilities?"
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex flex-col w-full h-[500px] bg-white rounded-xl shadow-xl overflow-hidden border border-gray-200">
      <div className="bg-violet-600 text-white p-4">
        <h3 className="font-medium">AI Chatbot</h3>
      </div>

      <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
        <div className="space-y-4">
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.role === "user"
                    ? "bg-violet-600 text-white rounded-br-none"
                    : "bg-white text-gray-800 shadow-sm rounded-bl-none"
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 rounded-lg rounded-bl-none p-3 shadow-sm max-w-[80%]">
                <div className="flex space-x-1">
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0ms" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: "150ms" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: "300ms" }}
                  ></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            className="flex-1 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-600"
          />
          <Button onClick={handleSendMessage} size="icon" className="bg-violet-600 hover:bg-violet-700">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}

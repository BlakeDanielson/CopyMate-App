import { openai } from "@ai-sdk/openai"
import { createDataStreamResponse, streamText } from "ai"
import { getCurrentUser } from "@/lib/auth"
import { addMessage, getConversation, createConversation, getMessages } from "@/lib/conversations"
import { getUserSettings } from "@/lib/settings"

export async function POST(req: Request) {
  try {
    const user = await getCurrentUser()

    if (!user) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      })
    }

    const { messages, conversationId, conversationTitle } = await req.json()

    // Get or create conversation
    let conversation
    if (conversationId) {
      conversation = await getConversation(conversationId, user.id)
      if (!conversation) {
        return new Response(JSON.stringify({ error: "Conversation not found" }), {
          status: 404,
          headers: { "Content-Type": "application/json" },
        })
      }
    } else {
      // Create a new conversation with the first message as the title
      const title = conversationTitle || messages[0]?.content?.substring(0, 100) || "New conversation"
      conversation = await createConversation(user.id, title)
    }

    // Get user settings
    const settings = await getUserSettings(user.id)

    // Store user message
    const userMessage = messages[messages.length - 1]
    if (userMessage.role === "user") {
      await addMessage(conversation.id, "user", userMessage.content)
    }

    // Log the interaction for monitoring
    console.log(
      `User ${user.id} - Conversation ${conversation.id} - Message: ${userMessage.content.substring(0, 50)}...`,
    )

    return createDataStreamResponse({
      execute: async (dataStream) => {
        const result = streamText({
          model: openai(settings?.model_name || "gpt-4o"),
          messages,
          temperature: settings?.temperature || 0.7,
          maxTokens: settings?.max_tokens || 1000,
        })

        let assistantResponse = ""

        result.onTextContent((content, isFinal) => {
          assistantResponse = content
          if (isFinal) {
            // Store assistant message when streaming is complete
            addMessage(conversation.id, "assistant", assistantResponse)

            // Log completion for monitoring
            console.log(
              `AI response to user ${user.id} - Conversation ${conversation.id} - Tokens: ~${Math.round(assistantResponse.length / 4)}`,
            )
          }
        })

        result.mergeIntoDataStream(dataStream)
      },
    })
  } catch (error) {
    console.error("Error in chat API:", error)
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    })
  }
}

// Add a GET endpoint to load conversation messages
export async function GET(req: Request) {
  try {
    const user = await getCurrentUser()

    if (!user) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      })
    }

    const url = new URL(req.url)
    const conversationId = url.searchParams.get("id")

    if (!conversationId) {
      return new Response(JSON.stringify({ error: "Conversation ID is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      })
    }

    const messages = await getMessages(Number.parseInt(conversationId), user.id)

    return new Response(JSON.stringify(messages), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    })
  } catch (error) {
    console.error("Error in get messages API:", error)
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    })
  }
}

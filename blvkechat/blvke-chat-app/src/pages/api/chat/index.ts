import { openai } from "@ai-sdk/openai"
import { createDataStreamResponse, streamText } from "ai"
import { getServerSession } from "next-auth"
import { authOptions } from "@/server/auth"
import { db } from "@/server/db"
import { env } from "@/env.mjs"

export default async function handler(req, res) {
  try {
    const session = await getServerSession(req, res, authOptions)

    if (!session?.user) {
      return res.status(401).json({ error: "Unauthorized" })
    }

    const { messages, conversationId, conversationTitle } = await req.json()

    // Get or create conversation
    let conversation
    if (conversationId) {
      conversation = await db.conversation.findUnique({
        where: {
          id: conversationId,
          userId: session.user.id,
        },
      })

      if (!conversation) {
        return res.status(404).json({ error: "Conversation not found" })
      }
    } else {
      // Create a new conversation with the first message as the title
      const title = conversationTitle || messages[0]?.content?.substring(0, 100) || "New conversation"
      conversation = await db.conversation.create({
        data: {
          title,
          userId: session.user.id,
        },
      })
    }

    // Get user settings
    let settings = await db.userSettings.findUnique({
      where: { userId: session.user.id },
    })

    if (!settings) {
      settings = await db.userSettings.create({
        data: {
          userId: session.user.id,
        },
      })
    }

    // Store user message
    const userMessage = messages[messages.length - 1]
    if (userMessage.role === "user") {
      await db.message.create({
        data: {
          conversationId: conversation.id,
          role: "user",
          content: userMessage.content,
        },
      })
    }

    // Log the interaction for monitoring
    console.log(
      `User ${session.user.id} - Conversation ${conversation.id} - Message: ${userMessage.content.substring(0, 50)}...`,
    )

    return createDataStreamResponse({
      execute: async (dataStream) => {
        const result = streamText({
          model: openai(settings?.modelName || "gpt-4o"),
          messages,
          temperature: settings?.temperature || 0.7,
          maxTokens: settings?.maxTokens || 1000,
          apiKey: env.OPENAI_API_KEY,
        })

        let assistantResponse = ""

        result.onTextContent((content, isFinal) => {
          assistantResponse = content
          if (isFinal) {
            // Store assistant message when streaming is complete
            db.message.create({
              data: {
                conversationId: conversation.id,
                role: "assistant",
                content: assistantResponse,
                tokensUsed: Math.round(assistantResponse.length / 4), // Rough estimate
              },
            })

            // Update conversation's lastMessageAt
            db.conversation.update({
              where: { id: conversation.id },
              data: { lastMessageAt: new Date() },
            })

            // Log completion for monitoring
            console.log(
              `AI response to user ${session.user.id} - Conversation ${conversation.id} - Tokens: ~${Math.round(assistantResponse.length / 4)}`,
            )
          }
        })

        result.mergeIntoDataStream(dataStream)
      },
    })(res)
  } catch (error) {
    console.error("Error in chat API:", error)
    return res.status(500).json({ error: "Internal server error" })
  }
}

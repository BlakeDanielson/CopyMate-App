import { getCurrentUser } from "@/lib/auth"
import { getConversations, createConversation } from "@/lib/conversations"

export async function GET() {
  try {
    const user = await getCurrentUser()

    if (!user) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      })
    }

    const conversations = await getConversations(user.id)

    return new Response(JSON.stringify(conversations), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    })
  } catch (error) {
    console.error("Error in conversations API:", error)
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    })
  }
}

export async function POST(req: Request) {
  try {
    const user = await getCurrentUser()

    if (!user) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      })
    }

    const { title } = await req.json()

    if (!title) {
      return new Response(JSON.stringify({ error: "Title is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      })
    }

    const conversation = await createConversation(user.id, title)

    return new Response(JSON.stringify(conversation), {
      status: 201,
      headers: { "Content-Type": "application/json" },
    })
  } catch (error) {
    console.error("Error in create conversation API:", error)
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    })
  }
}

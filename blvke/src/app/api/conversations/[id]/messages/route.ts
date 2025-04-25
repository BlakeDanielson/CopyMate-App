import { getCurrentUser } from "@/lib/auth"
import { getMessages, addMessage } from "@/lib/conversations"

export async function GET(req: Request, { params }: { params: { id: string } }) {
  try {
    const user = await getCurrentUser()

    if (!user) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      })
    }

    const messages = await getMessages(Number.parseInt(params.id), user.id)

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

export async function POST(req: Request, { params }: { params: { id: string } }) {
  try {
    const user = await getCurrentUser()

    if (!user) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      })
    }

    const { role, content, tokens_used } = await req.json()

    if (!role || !content) {
      return new Response(JSON.stringify({ error: "Role and content are required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      })
    }

    const message = await addMessage(Number.parseInt(params.id), role, content, tokens_used || 0)

    return new Response(JSON.stringify(message), {
      status: 201,
      headers: { "Content-Type": "application/json" },
    })
  } catch (error) {
    console.error("Error in add message API:", error)
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    })
  }
}

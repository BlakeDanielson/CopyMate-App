import { getUserByEmail, comparePasswords, createSession } from "@/lib/auth"

export async function POST(req: Request) {
  try {
    const { email, password } = await req.json()

    console.log(`Login attempt for email: ${email}`)

    // Validate input
    if (!email || !password) {
      console.log("Missing required fields")
      return new Response(JSON.stringify({ error: "Missing required fields" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      })
    }

    // Get user
    const user = await getUserByEmail(email)
    if (!user) {
      console.log(`User not found: ${email}`)
      return new Response(JSON.stringify({ error: "Invalid credentials" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      })
    }

    // Verify password
    const isPasswordValid = await comparePasswords(password, user.password_hash)
    console.log(`Password validation result: ${isPasswordValid}`)

    if (!isPasswordValid) {
      console.log("Invalid password")
      return new Response(JSON.stringify({ error: "Invalid credentials" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      })
    }

    // Create session
    await createSession(user.id)
    console.log(`Login successful for user: ${user.email}`)

    return new Response(JSON.stringify({ success: true }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    })
  } catch (error) {
    console.error("Error in login API:", error)
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    })
  }
}

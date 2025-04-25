import { USE_REAL_DATABASE } from "./config"
import { executeQuery } from "./db"
import { mockDb } from "./mock-db"

// Database adapter that switches between real and mock database
export const dbAdapter = {
  // User functions
  createUser: async (email: string, name: string, passwordHash: string) => {
    if (USE_REAL_DATABASE) {
      const result = await executeQuery(
        "INSERT INTO users (email, name, password_hash) VALUES ($1, $2, $3) RETURNING id",
        [email, name, passwordHash],
      )
      return result[0]
    } else {
      return mockDb.createUser(email, name, passwordHash)
    }
  },

  getUserByEmail: async (email: string) => {
    if (USE_REAL_DATABASE) {
      const result = await executeQuery("SELECT * FROM users WHERE email = $1", [email])
      return result[0]
    } else {
      return mockDb.getUserByEmail(email)
    }
  },

  getUserById: async (id: number) => {
    if (USE_REAL_DATABASE) {
      const result = await executeQuery("SELECT id, email, name, created_at FROM users WHERE id = $1", [id])
      return result[0]
    } else {
      const user = mockDb.getUserById(id)
      if (user) {
        // Exclude password_hash for security
        const { password_hash, ...safeUser } = user
        return safeUser
      }
      return undefined
    }
  },

  // Conversation functions
  createConversation: async (userId: number, title: string) => {
    if (USE_REAL_DATABASE) {
      const result = await executeQuery("INSERT INTO conversations (user_id, title) VALUES ($1, $2) RETURNING *", [
        userId,
        title,
      ])
      return result[0]
    } else {
      return mockDb.createConversation(userId, title)
    }
  },

  getConversations: async (userId: number) => {
    if (USE_REAL_DATABASE) {
      return await executeQuery(
        `SELECT c.*, 
          (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count,
          (SELECT content FROM messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message
        FROM conversations c
        WHERE c.user_id = $1
        ORDER BY c.is_pinned DESC, c.last_message_at DESC`,
        [userId],
      )
    } else {
      return mockDb.getConversations(userId)
    }
  },

  getConversation: async (id: number, userId: number) => {
    if (USE_REAL_DATABASE) {
      const result = await executeQuery("SELECT * FROM conversations WHERE id = $1 AND user_id = $2", [id, userId])
      return result[0]
    } else {
      return mockDb.getConversation(id, userId)
    }
  },

  updateConversation: async (id: number, userId: number, data: { title?: string; is_pinned?: boolean }) => {
    if (USE_REAL_DATABASE) {
      const updates = []
      const values = []
      let paramIndex = 1

      if (data.title !== undefined) {
        updates.push(`title = $${paramIndex++}`)
        values.push(data.title)
      }

      if (data.is_pinned !== undefined) {
        updates.push(`is_pinned = $${paramIndex++}`)
        values.push(data.is_pinned)
      }

      if (updates.length === 0) return null

      updates.push(`updated_at = CURRENT_TIMESTAMP`)

      const result = await executeQuery(
        `UPDATE conversations SET ${updates.join(", ")} WHERE id = $${paramIndex++} AND user_id = $${paramIndex++} RETURNING *`,
        [...values, id, userId],
      )
      return result[0]
    } else {
      return mockDb.updateConversation(id, userId, data)
    }
  },

  deleteConversation: async (id: number, userId: number) => {
    if (USE_REAL_DATABASE) {
      await executeQuery("DELETE FROM conversations WHERE id = $1 AND user_id = $2", [id, userId])
      return true
    } else {
      return mockDb.deleteConversation(id, userId)
    }
  },

  // Message functions
  addMessage: async (conversationId: number, role: string, content: string, tokensUsed = 0) => {
    if (USE_REAL_DATABASE) {
      // Add the message
      const result = await executeQuery(
        "INSERT INTO messages (conversation_id, role, content, tokens_used) VALUES ($1, $2, $3, $4) RETURNING *",
        [conversationId, role, content, tokensUsed],
      )

      // Update the conversation's last_message_at timestamp
      await executeQuery(
        "UPDATE conversations SET last_message_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = $1",
        [conversationId],
      )

      return result[0]
    } else {
      return mockDb.addMessage(conversationId, role, content, tokensUsed)
    }
  },

  getMessages: async (conversationId: number, userId: number) => {
    if (USE_REAL_DATABASE) {
      // First verify the conversation belongs to the user
      const conversation = await executeQuery("SELECT id FROM conversations WHERE id = $1 AND user_id = $2", [
        conversationId,
        userId,
      ])

      if (!conversation || conversation.length === 0) {
        throw new Error("Conversation not found or access denied")
      }

      return await executeQuery("SELECT * FROM messages WHERE conversation_id = $1 ORDER BY created_at ASC", [
        conversationId,
      ])
    } else {
      return mockDb.getMessages(conversationId, userId)
    }
  },

  // User settings functions
  createUserSettings: async (userId: number) => {
    if (USE_REAL_DATABASE) {
      const result = await executeQuery("INSERT INTO user_settings (user_id) VALUES ($1) RETURNING *", [userId])
      return result[0]
    } else {
      return mockDb.createUserSettings(userId)
    }
  },

  getUserSettings: async (userId: number) => {
    if (USE_REAL_DATABASE) {
      const result = await executeQuery("SELECT * FROM user_settings WHERE user_id = $1", [userId])
      return result[0]
    } else {
      return mockDb.getUserSettings(userId)
    }
  },

  updateUserSettings: async (
    userId: number,
    settings: {
      model_name?: string
      temperature?: number
      max_tokens?: number
      theme?: string
      font_size?: string
    },
  ) => {
    if (USE_REAL_DATABASE) {
      const updates = []
      const values = []
      let paramIndex = 1

      for (const [key, value] of Object.entries(settings)) {
        if (value !== undefined) {
          updates.push(`${key} = $${paramIndex++}`)
          values.push(value)
        }
      }

      if (updates.length === 0) return null

      updates.push(`updated_at = CURRENT_TIMESTAMP`)

      const result = await executeQuery(
        `UPDATE user_settings SET ${updates.join(", ")} WHERE user_id = $${paramIndex++} RETURNING *`,
        [...values, userId],
      )
      return result[0]
    } else {
      return mockDb.updateUserSettings(userId, settings)
    }
  },
}

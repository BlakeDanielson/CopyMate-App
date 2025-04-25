export interface User {
  id: number
  email: string
  name: string
  password_hash: string
  created_at: string
  updated_at: string
}

export interface Conversation {
  id: number
  user_id: number
  title: string
  created_at: string
  updated_at: string
  is_pinned: boolean
  last_message_at: string
}

export interface Message {
  id: number
  conversation_id: number
  role: string
  content: string
  created_at: string
  tokens_used: number
}

export interface UserSettings {
  id: number
  user_id: number
  model_name: string
  temperature: number
  max_tokens: number
  theme: string
  font_size: string
  created_at: string
  updated_at: string
}

// In-memory storage
const users: User[] = []
let conversations: Conversation[] = []
let messages: Message[] = []
const userSettings: UserSettings[] = []

// Auto-increment counters
let userId = 1
let conversationId = 1
let messageId = 1
let settingsId = 1

// Helper function to get current timestamp
const now = () => new Date().toISOString()

// Mock database functions
export const mockDb = {
  // User functions
  createUser: (email: string, name: string, passwordHash: string): User => {
    const user: User = {
      id: userId++,
      email,
      name,
      password_hash: passwordHash,
      created_at: now(),
      updated_at: now(),
    }
    users.push(user)
    return user
  },

  getUserByEmail: (email: string): User | undefined => {
    return users.find((user) => user.email === email)
  },

  getUserById: (id: number): User | undefined => {
    return users.find((user) => user.id === id)
  },

  // Conversation functions
  createConversation: (userId: number, title: string): Conversation => {
    const timestamp = now()
    const conversation: Conversation = {
      id: conversationId++,
      user_id: userId,
      title,
      created_at: timestamp,
      updated_at: timestamp,
      is_pinned: false,
      last_message_at: timestamp,
    }
    conversations.push(conversation)
    return conversation
  },

  getConversations: (userId: number): any[] => {
    return conversations
      .filter((conv) => conv.user_id === userId)
      .map((conv) => {
        const conversationMessages = messages.filter((msg) => msg.conversation_id === conv.id)
        return {
          ...conv,
          message_count: conversationMessages.length,
          last_message:
            conversationMessages.length > 0
              ? conversationMessages.sort(
                  (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
                )[0].content
              : "",
        }
      })
  },

  getConversation: (id: number, userId: number): Conversation | undefined => {
    return conversations.find((conv) => conv.id === id && conv.user_id === userId)
  },

  updateConversation: (id: number, userId: number, data: Partial<Conversation>): Conversation | null => {
    const index = conversations.findIndex((conv) => conv.id === id && conv.user_id === userId)
    if (index === -1) return null

    conversations[index] = {
      ...conversations[index],
      ...data,
      updated_at: now(),
    }
    return conversations[index]
  },

  deleteConversation: (id: number, userId: number): boolean => {
    const initialLength = conversations.length
    conversations = conversations.filter((conv) => !(conv.id === id && conv.user_id === userId))

    // Also delete associated messages
    messages = messages.filter((msg) => msg.conversation_id !== id)

    return conversations.length < initialLength
  },

  // Message functions
  addMessage: (conversationId: number, role: string, content: string, tokensUsed = 0): Message => {
    const message: Message = {
      id: messageId++,
      conversation_id: conversationId,
      role,
      content,
      created_at: now(),
      tokens_used: tokensUsed,
    }
    messages.push(message)

    // Update conversation's last_message_at
    const convIndex = conversations.findIndex((conv) => conv.id === conversationId)
    if (convIndex !== -1) {
      conversations[convIndex].last_message_at = now()
      conversations[convIndex].updated_at = now()
    }

    return message
  },

  getMessages: (conversationId: number, userId: number): Message[] => {
    // First verify the conversation belongs to the user
    const conversation = conversations.find((conv) => conv.id === conversationId && conv.user_id === userId)
    if (!conversation) {
      throw new Error("Conversation not found or access denied")
    }

    return messages
      .filter((msg) => msg.conversation_id === conversationId)
      .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
  },

  // User settings functions
  createUserSettings: (userId: number): UserSettings => {
    const settings: UserSettings = {
      id: settingsId++,
      user_id: userId,
      model_name: "gpt-4o",
      temperature: 0.7,
      max_tokens: 1000,
      theme: "light",
      font_size: "medium",
      created_at: now(),
      updated_at: now(),
    }
    userSettings.push(settings)
    return settings
  },

  getUserSettings: (userId: number): UserSettings | undefined => {
    return userSettings.find((settings) => settings.user_id === userId)
  },

  updateUserSettings: (userId: number, data: Partial<UserSettings>): UserSettings | null => {
    const index = userSettings.findIndex((settings) => settings.user_id === userId)
    if (index === -1) return null

    userSettings[index] = {
      ...userSettings[index],
      ...data,
      updated_at: now(),
    }
    return userSettings[index]
  },

  // Helper function to seed initial data
  seedInitialData: () => {
    // Create a test user if none exists
    if (users.length === 0) {
      console.log("Seeding mock database with test user")

      // Password is "password"
      const testUser = mockDb.createUser(
        "test@example.com",
        "Test User",
        "$2b$10$8r0qPVaJeLES1i9m0Wz9xuY5Yml3JGcPDSzTJBtjUMVmFbcJgq.4W",
      )

      // Create user settings
      mockDb.createUserSettings(testUser.id)

      // Create some sample conversations
      const conv1 = mockDb.createConversation(testUser.id, "Introduction to AI")
      const conv2 = mockDb.createConversation(testUser.id, "JavaScript Help")

      // Add some messages
      mockDb.addMessage(conv1.id, "user", "What is artificial intelligence?")
      mockDb.addMessage(
        conv1.id,
        "assistant",
        "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions. The term may also be applied to any machine that exhibits traits associated with a human mind such as learning and problem-solving.",
      )

      mockDb.addMessage(conv2.id, "user", "How do I use async/await in JavaScript?")
      mockDb.addMessage(
        conv2.id,
        "assistant",
        "Async/await is a way to handle asynchronous operations in JavaScript. It's built on top of promises and makes asynchronous code look more like synchronous code.\n\n```javascript\nasync function fetchData() {\n  try {\n    const response = await fetch('https://api.example.com/data');\n    const data = await response.json();\n    return data;\n  } catch (error {\n    console.error('Error fetching data:', error);\n  }\n}\n```\n\nThe `async` keyword declares that a function returns a promise. The `await` keyword makes JavaScript wait until the promise settles and returns its result.",
      )
    }
  },
}

// Ensure the seed function is called immediately
mockDb.seedInitialData()

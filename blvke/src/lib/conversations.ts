import { dbAdapter } from "./db-adapter"

export async function getConversations(userId: number) {
  try {
    return await dbAdapter.getConversations(userId)
  } catch (error) {
    console.error("Error getting conversations:", error)
    throw error
  }
}

export async function getConversation(id: number, userId: number) {
  try {
    return await dbAdapter.getConversation(id, userId)
  } catch (error) {
    console.error("Error getting conversation:", error)
    throw error
  }
}

export async function createConversation(userId: number, title: string) {
  try {
    return await dbAdapter.createConversation(userId, title)
  } catch (error) {
    console.error("Error creating conversation:", error)
    throw error
  }
}

export async function updateConversation(id: number, userId: number, data: { title?: string; is_pinned?: boolean }) {
  try {
    return await dbAdapter.updateConversation(id, userId, data)
  } catch (error) {
    console.error("Error updating conversation:", error)
    throw error
  }
}

export async function deleteConversation(id: number, userId: number) {
  try {
    return await dbAdapter.deleteConversation(id, userId)
  } catch (error) {
    console.error("Error deleting conversation:", error)
    throw error
  }
}

export async function getMessages(conversationId: number, userId: number) {
  try {
    return await dbAdapter.getMessages(conversationId, userId)
  } catch (error) {
    console.error("Error getting messages:", error)
    throw error
  }
}

export async function addMessage(conversationId: number, role: string, content: string, tokensUsed = 0) {
  try {
    return await dbAdapter.addMessage(conversationId, role, content, tokensUsed)
  } catch (error) {
    console.error("Error adding message:", error)
    throw error
  }
}

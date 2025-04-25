import { dbAdapter } from "./db-adapter"

export async function getUserSettings(userId: number) {
  try {
    return await dbAdapter.getUserSettings(userId)
  } catch (error) {
    console.error("Error getting user settings:", error)
    throw error
  }
}

export async function updateUserSettings(
  userId: number,
  settings: {
    model_name?: string
    temperature?: number
    max_tokens?: number
    theme?: string
    font_size?: string
  },
) {
  try {
    return await dbAdapter.updateUserSettings(userId, settings)
  } catch (error) {
    console.error("Error updating user settings:", error)
    throw error
  }
}

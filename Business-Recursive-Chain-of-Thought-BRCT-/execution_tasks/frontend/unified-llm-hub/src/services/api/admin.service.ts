import { apiService } from "./api.service";
import { Role } from "../../interfaces/auth";
import { ADMIN_API_URL } from "../../config/constants";

// Response interfaces for our backend
interface UsersResponse {
  success: boolean;
  data: User[];
  message: string;
}

interface UserResponse {
  success: boolean;
  data: User;
  message: string;
}

// User interface for admin responses (simplified from the auth interface)
interface User {
  id: string;
  email: string;
  username?: string;
  fullName?: string;
  role: string;
  messageCount: number;
  createdAt: string;
  updatedAt: string;
}

export class AdminService {
  /**
   * Get all users
   */
  public async getAllUsers(): Promise<User[]> {
    try {
      const response = await apiService.get<UsersResponse>(
        `${ADMIN_API_URL}/users`
      );
      return response.data;
    } catch (error) {
      console.error("Get all users error:", error);
      throw new Error("Failed to retrieve users");
    }
  }

  /**
   * Delete a user
   */
  public async deleteUser(userId: string): Promise<User> {
    try {
      const response = await apiService.delete<UserResponse>(
        `${ADMIN_API_URL}/users/${userId}`
      );
      return response.data;
    } catch (error) {
      console.error("Delete user error:", error);
      throw new Error("Failed to delete user");
    }
  }

  /**
   * Update a user's role
   */
  public async updateUserRole(userId: string, role: Role): Promise<User> {
    try {
      const response = await apiService.patch<UserResponse>(
        `${ADMIN_API_URL}/users/${userId}/role`,
        { role }
      );
      return response.data;
    } catch (error) {
      console.error("Update user role error:", error);
      throw new Error("Failed to update user role");
    }
  }
}

// Singleton instance
export const adminService = new AdminService();

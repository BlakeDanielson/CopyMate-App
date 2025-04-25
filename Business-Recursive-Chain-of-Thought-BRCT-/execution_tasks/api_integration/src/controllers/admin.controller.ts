/**
 * Admin controller
 * Handles HTTP requests for admin operations
 */

import { Request, Response } from 'express';
import { authService } from '../services/auth.service';
import { Role } from '../generated/prisma'; // Import Role from generated client

export class AdminController {
  /**
   * Get all users
   */
  async getAllUsers(req: Request, res: Response): Promise<void> {
    try {
      const users = await authService.getAllUsers();

      res.status(200).json({
        success: true,
        data: users,
        message: 'Users retrieved successfully'
      });
    } catch (error: any) {
      console.error('Get all users error:', error);
      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred while fetching users'
      });
    }
  }

  /**
   * Delete a user
   */
  async deleteUser(req: Request, res: Response): Promise<void> {
    try {
      const { userId } = req.params;

      if (!userId) {
        res.status(400).json({
          success: false,
          error: 'Bad Request',
          message: 'User ID is required'
        });
        return;
      }

      // Prevent admins from deleting themselves
      if (userId === req.user?.id) {
        res.status(400).json({
          success: false,
          error: 'Bad Request',
          message: 'You cannot delete your own account using this endpoint'
        });
        return;
      }

      const deletedUser = await authService.deleteUser(userId);

      res.status(200).json({
        success: true,
        data: deletedUser,
        message: 'User deleted successfully'
      });
    } catch (error: any) {
      console.error('Delete user error:', error);

      // Handle not found error
      if (error.message && error.message.includes('Record to delete does not exist')) {
        res.status(404).json({
          success: false,
          error: 'Not Found',
          message: 'User not found'
        });
        return;
      }

      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred while deleting the user'
      });
    }
  }

  /**
   * Update a user's role
   */
  async updateUserRole(req: Request, res: Response): Promise<void> {
    try {
      const { userId } = req.params;
      const { role } = req.body;

      if (!userId) {
        res.status(400).json({
          success: false,
          error: 'Bad Request',
          message: 'User ID is required'
        });
        return;
      }

      if (!role || !Object.values(Role).includes(role)) {
        res.status(400).json({
          success: false,
          error: 'Bad Request',
          message: `Role must be one of: ${Object.values(Role).join(', ')}`
        });
        return;
      }

      // Prevent admins from changing their own role
      if (userId === req.user?.id) {
        res.status(400).json({
          success: false,
          error: 'Bad Request',
          message: 'You cannot change your own role using this endpoint'
        });
        return;
      }

      const updatedUser = await authService.updateUserRole(userId, role);

      res.status(200).json({
        success: true,
        data: updatedUser,
        message: 'User role updated successfully'
      });
    } catch (error: any) {
      console.error('Update user role error:', error);

      // Handle not found error
      if (error.message && error.message.includes('Record to update not found')) {
        res.status(404).json({
          success: false,
          error: 'Not Found',
          message: 'User not found'
        });
        return;
      }

      res.status(500).json({
        success: false,
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An error occurred while updating the user role'
      });
    }
  }
}

// Create a singleton instance
export const adminController = new AdminController();

/**
 * Admin routes
 * Routes for admin-only operations
 */

import { Router } from 'express';
import { adminController } from '../controllers/admin.controller';
import { authMiddleware, adminMiddleware } from '../middleware/auth.middleware';

export const createAdminRoutes = (): Router => {
  const router = Router();

  // Apply auth and admin middleware to all routes
  router.use(authMiddleware);
  router.use(adminMiddleware);

  /**
   * @route   GET /api/v1/admin/users
   * @desc    Get all users
   * @access  Admin only
   */
  router.get('/users', (req, res) => adminController.getAllUsers(req, res));

  /**
   * @route   DELETE /api/v1/admin/users/:userId
   * @desc    Delete a user
   * @access  Admin only
   */
  router.delete('/users/:userId', (req, res) => adminController.deleteUser(req, res));

  /**
   * @route   PATCH /api/v1/admin/users/:userId/role
   * @desc    Update a user's role
   * @access  Admin only
   */
  router.patch('/users/:userId/role', (req, res) => adminController.updateUserRole(req, res));

  return router;
};

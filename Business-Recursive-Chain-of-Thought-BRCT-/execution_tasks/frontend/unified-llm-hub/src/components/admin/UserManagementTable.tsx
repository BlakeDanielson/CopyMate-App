import React, { useState, useEffect } from "react";
import { Role, User } from "../../interfaces/auth";
import { adminService } from "../../services/api/admin.service";
import { format } from "date-fns";

// User interface for admin responses (simplified from the auth interface)
interface AdminUser {
  id: string;
  email: string;
  username?: string;
  fullName?: string;
  role: string;
  messageCount: number;
  createdAt: string;
  updatedAt: string;
}

const UserManagementTable: React.FC = () => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState<Role>(Role.USER);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const fetchedUsers = await adminService.getAllUsers();
      setUsers(fetchedUsers);
      setError(null);
    } catch (err) {
      setError("Failed to fetch users. Please try again later.");
      console.error("Error fetching users:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (userId: string) => {
    setSelectedUserId(userId);
    setIsDeleteModalOpen(true);
  };

  const handleRoleClick = (userId: string, currentRole: string) => {
    setSelectedUserId(userId);
    setSelectedRole(currentRole === "ADMIN" ? Role.USER : Role.ADMIN);
    setIsRoleModalOpen(true);
  };

  const confirmDelete = async () => {
    if (!selectedUserId) return;

    try {
      await adminService.deleteUser(selectedUserId);
      setUsers(users.filter((user) => user.id !== selectedUserId));
      setIsDeleteModalOpen(false);
      setSelectedUserId(null);
    } catch (err) {
      setError("Failed to delete user. Please try again later.");
      console.error("Error deleting user:", err);
    }
  };

  const confirmRoleChange = async () => {
    if (!selectedUserId) return;

    try {
      const updatedUser = await adminService.updateUserRole(
        selectedUserId,
        selectedRole
      );
      setUsers(
        users.map((user) => (user.id === selectedUserId ? updatedUser : user))
      );
      setIsRoleModalOpen(false);
      setSelectedUserId(null);
    } catch (err) {
      setError("Failed to update user role. Please try again later.");
      console.error("Error updating user role:", err);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), "MMM d, yyyy h:mm a");
    } catch (e) {
      return dateString;
    }
  };

  if (loading) return <div className="p-4 text-center">Loading users...</div>;

  if (error)
    return (
      <div className="p-4 text-center text-red-500">
        <p>{error}</p>
        <button
          className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          onClick={fetchUsers}
        >
          Try Again
        </button>
      </div>
    );

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-200">
        <thead>
          <tr className="bg-gray-100">
            <th className="py-2 px-4 border-b text-left">Email</th>
            <th className="py-2 px-4 border-b text-left">Name</th>
            <th className="py-2 px-4 border-b text-left">Role</th>
            <th className="py-2 px-4 border-b text-left">Message Count</th>
            <th className="py-2 px-4 border-b text-left">Created At</th>
            <th className="py-2 px-4 border-b text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.length === 0 ? (
            <tr>
              <td colSpan={6} className="py-4 text-center">
                No users found.
              </td>
            </tr>
          ) : (
            users.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50">
                <td className="py-2 px-4 border-b">{user.email}</td>
                <td className="py-2 px-4 border-b">
                  {user.fullName || user.username || "-"}
                </td>
                <td className="py-2 px-4 border-b">
                  <span
                    className={`px-2 py-1 rounded ${
                      user.role === "ADMIN"
                        ? "bg-purple-100 text-purple-800"
                        : "bg-gray-100"
                    }`}
                  >
                    {user.role}
                  </span>
                </td>
                <td className="py-2 px-4 border-b">{user.messageCount}</td>
                <td className="py-2 px-4 border-b">
                  {formatDate(user.createdAt)}
                </td>
                <td className="py-2 px-4 border-b">
                  <button
                    className="mr-2 px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                    onClick={() => handleRoleClick(user.id, user.role)}
                  >
                    {user.role === "ADMIN" ? "Revoke Admin" : "Make Admin"}
                  </button>
                  <button
                    className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                    onClick={() => handleDeleteClick(user.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>

      {/* Delete Confirmation Modal */}
      {isDeleteModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Confirm Deletion</h3>
            <p>
              Are you sure you want to delete this user? This action cannot be
              undone.
            </p>
            <div className="mt-6 flex justify-end space-x-3">
              <button
                className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
                onClick={() => setIsDeleteModalOpen(false)}
              >
                Cancel
              </button>
              <button
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                onClick={confirmDelete}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Role Change Confirmation Modal */}
      {isRoleModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Confirm Role Change</h3>
            <p>
              Are you sure you want to{" "}
              {selectedRole === Role.ADMIN
                ? "grant admin privileges to"
                : "revoke admin privileges from"}{" "}
              this user?
            </p>
            <div className="mt-6 flex justify-end space-x-3">
              <button
                className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
                onClick={() => setIsRoleModalOpen(false)}
              >
                Cancel
              </button>
              <button
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                onClick={confirmRoleChange}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagementTable;

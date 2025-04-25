import React from "react";
import UserManagementTable from "../components/admin/UserManagementTable";

const AdminPage: React.FC = () => {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Admin Panel</h1>
        <p className="text-gray-600">
          Manage users and system settings for the UnifiedLLM Hub.
        </p>
      </div>

      <div className="bg-white rounded shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">User Management</h2>
        <UserManagementTable />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded shadow p-6">
          <h2 className="text-xl font-semibold mb-4">System Stats</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded">
              <p className="text-sm text-gray-500">Total Users</p>
              <p className="text-2xl font-bold" id="total-users">
                Loading...
              </p>
            </div>
            <div className="bg-green-50 p-4 rounded">
              <p className="text-sm text-gray-500">Active Subscriptions</p>
              <p className="text-2xl font-bold" id="active-subscriptions">
                Loading...
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded">
              <p className="text-sm text-gray-500">Total Messages</p>
              <p className="text-2xl font-bold" id="total-messages">
                Loading...
              </p>
            </div>
            <div className="bg-yellow-50 p-4 rounded">
              <p className="text-sm text-gray-500">Admin Users</p>
              <p className="text-2xl font-bold" id="admin-users">
                Loading...
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <button className="w-full py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed">
              View Analytics Dashboard
            </button>
            <button
              className="w-full py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
              disabled
            >
              Manage Subscription Plans
            </button>
            <button
              className="w-full py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
              disabled
            >
              System Settings
            </button>
            <button
              className="w-full py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
              disabled
            >
              Server Operations
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPage;

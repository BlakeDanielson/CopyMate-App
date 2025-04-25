import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useTypedSelector } from "../../hooks/useTypedSelector";

interface ProtectedRouteProps {
  children: React.ReactNode;
  adminOnly?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  adminOnly = false,
}) => {
  const { user, isAuthenticated } = useTypedSelector((state) => state.auth);
  const location = useLocation();

  if (!isAuthenticated || !user) {
    // Redirect to the login page with a return URL
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if route is admin-only and user is not an admin
  if (adminOnly && user.role !== "ADMIN") {
    // Redirect to the dashboard with a state indication of access denied
    return <Navigate to="/dashboard" state={{ accessDenied: true }} replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;

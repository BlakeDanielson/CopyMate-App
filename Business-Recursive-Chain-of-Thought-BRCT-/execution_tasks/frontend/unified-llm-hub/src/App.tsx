import React, { useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import { useTypedSelector } from "./hooks/useTypedSelector";
import { useAppDispatch } from "./hooks/useAppDispatch";
import { THEMES } from "./config/constants";
import MainLayout from "./components/layout/MainLayout";
import Login from "./pages/Login";
import SignUp from "./pages/SignUp"; // Import SignUp page
import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";
import Settings from "./pages/Settings";
import Admin from "./pages/Admin";
import NotFound from "./pages/NotFound";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import { checkAuth } from "./store/slices/authSlice";
import { initializeMockData } from "./store/slices/llmSlice";

const App: React.FC = () => {
  const dispatch = useAppDispatch();
  const theme = useTypedSelector((state) => state.ui.theme);

  // Initialize app on mount
  useEffect(() => {
    // Check if user is authenticated
    dispatch(checkAuth());

    // For development: initialize mock LLM data
    dispatch(initializeMockData());
  }, [dispatch]);

  // Create theme based on user preference
  const themeObject = React.useMemo(() => {
    const mode =
      theme === THEMES.SYSTEM
        ? window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light"
        : theme;

    return createTheme({
      palette: {
        mode: mode as "light" | "dark",
        primary: {
          main: "#4a6fa5",
        },
        secondary: {
          main: "#3d84a8",
        },
        background: {
          default: mode === "dark" ? "#121212" : "#f5f5f5",
          paper: mode === "dark" ? "#1e1e1e" : "#ffffff",
        },
      },
      typography: {
        fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      },
    });
  }, [theme]);

  return (
    <ThemeProvider theme={themeObject}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} /> {/* Add SignUp route */}

          {/* Protected routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="chat" element={<Chat />} />
            <Route path="chat/:conversationId" element={<Chat />} />
            <Route path="settings" element={<Settings />} />
            <Route
              path="admin"
              element={
                <ProtectedRoute adminOnly={true}>
                  <Admin />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* Fallback route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
};

export default App;

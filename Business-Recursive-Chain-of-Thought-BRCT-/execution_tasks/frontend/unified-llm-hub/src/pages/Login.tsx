import React, { useState } from "react";
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  InputAdornment,
  IconButton,
} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { useAppDispatch } from "../hooks/useAppDispatch"; // Keep for standard login
import { useTypedSelector } from "../hooks/useTypedSelector"; // Keep for standard login state
import { login, setUser } from "../store/slices/authSlice"; // Import setUser to update auth state
import { authService } from "../services/api/auth.service"; // Import direct service for test login

const Login: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [testLoading, setTestLoading] = useState(false); // State for test login button
  const [testError, setTestError] = useState<string | null>(null); // State for test login error
  const dispatch = useAppDispatch(); // Keep for standard login
  const navigate = useNavigate();
  // Standard login state from Redux
  const { loading, error, isAuthenticated } = useTypedSelector(
    (state) => state.auth
  );

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate("/");
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (email && password) {
      await dispatch(login({ email, password }));
    }
  };

  // Handler for the Test Login button
  const handleTestLogin = async () => {
    setTestLoading(true);
    setTestError(null);
    try {
      const user = await authService.testLogin();
      if (user) {
        // Update Redux store with the user data to trigger isAuthenticated change
        dispatch(setUser(user));
        console.log("Test login successful, user in Redux store");
        // No need to navigate here as the useEffect will handle it once isAuthenticated is true
      } else {
        setTestError("Test login completed but no user data was returned.");
      }
    } catch (err: any) {
      console.error("Test login failed:", err);
      setTestError(
        err.message || "An unknown error occurred during test login."
      );
    } finally {
      setTestLoading(false);
    }
  };

  // Check if the test login feature should be enabled
  const enableTestAuth = process.env.REACT_APP_ENABLE_TEST_AUTH === "true";

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            width: "100%",
          }}
        >
          <Typography component="h1" variant="h5" sx={{ mb: 3 }}>
            UnifiedLLM Hub
          </Typography>

          <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
            Sign in
          </Typography>

          {error && (
            <Alert severity="error" sx={{ width: "100%", mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* Display test login error */}
          {testError && (
            <Alert severity="warning" sx={{ width: "100%", mb: 2 }}>
              {testError}
            </Alert>
          )}

          <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{ mt: 1, width: "100%" }}
          >
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type={showPassword ? "text" : "password"}
              id="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading || !email || !password}
            >
              {loading ? <CircularProgress size={24} /> : "Sign In"}
            </Button>

            {/* Conditionally render Test Login button */}
            {enableTestAuth && (
              <Button
                fullWidth
                variant="outlined" // Use outlined style to differentiate
                sx={{ mt: 1, mb: 1 }}
                onClick={handleTestLogin}
                disabled={testLoading}
              >
                {testLoading ? (
                  <CircularProgress size={24} />
                ) : (
                  "Test Login (No Auth)"
                )}
              </Button>
            )}

            <Typography
              variant="body2"
              color="text.secondary"
              align="center"
              sx={{ mt: 2 }}
            >
              Demo credentials: demo@example.com / password
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;

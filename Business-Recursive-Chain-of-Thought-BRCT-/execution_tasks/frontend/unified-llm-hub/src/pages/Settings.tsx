import React, { useState, useEffect, SyntheticEvent } from "react";
import {
  Box,
  Paper,
  Typography,
  Divider,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  Slider,
  Button,
  Alert,
  CircularProgress,
  Grid,
  TextField,
  Tab,
  Tabs,
} from "@mui/material";
import SubscriptionDetails from "../components/settings/SubscriptionDetails";
import SubscriptionPlans from "../components/settings/SubscriptionPlans";
import { useAppDispatch } from "../hooks/useAppDispatch";
import { useTypedSelector } from "../hooks/useTypedSelector";
import {
  setSelectedProvider,
  setSelectedModel,
  updateParameters,
} from "../store/slices/llmSlice";
import { setTheme, addNotification } from "../store/slices/uiSlice";
import { updateUserPreferences } from "../store/slices/authSlice";
import { THEMES } from "../config/constants";

const Settings: React.FC = () => {
  const dispatch = useAppDispatch();

  const { user } = useTypedSelector((state) => state.auth);
  const { providers, models, selectedProvider, selectedModel, parameters } =
    useTypedSelector((state) => state.llm);
  const { theme: appTheme } = useTypedSelector((state) => state.ui);

  const [temperature, setTemperature] = useState(parameters.temperature);
  const [maxTokens, setMaxTokens] = useState(parameters.maxTokens);
  const [topP, setTopP] = useState(parameters.topP);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (_event: SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Load models when provider changes
  useEffect(() => {
    if (selectedProvider) {
      // This would normally fetch models for the selected provider
      // For now, we're using the mock data initialized in the store
    }
  }, [selectedProvider, dispatch]);

  const handleSave = async () => {
    setSaving(true);
    setSuccess(false);

    // Update LLM parameters
    dispatch(updateParameters({ temperature, maxTokens, topP }));

    // Update user preferences
    if (user) {
      dispatch(
        updateUserPreferences({
          theme: appTheme,
          defaultProvider: selectedProvider || undefined,
          defaultModel: selectedModel || undefined,
          defaultParameters: {
            temperature,
            maxTokens,
            topP,
          },
        })
      );
    }

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));

    setSaving(false);
    setSuccess(true);

    // Add notification
    dispatch(
      addNotification({
        type: "success",
        message: "Settings saved successfully",
      })
    );

    // Clear success message after 3 seconds
    setTimeout(() => setSuccess(false), 3000);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom mb={3}>
        Settings
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          aria-label="settings tabs"
        >
          <Tab label="General" />
          <Tab label="Subscription" />
          <Tab label="LLM Settings" />
        </Tabs>
      </Box>

      {/* General Tab */}
      {activeTab === 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Appearance
          </Typography>
          <Divider sx={{ mb: 2 }} />

          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel id="theme-label">Theme</InputLabel>
            <Select
              labelId="theme-label"
              value={appTheme}
              label="Theme"
              onChange={(e) =>
                dispatch(
                  setTheme(e.target.value as "light" | "dark" | "system")
                )
              }
            >
              <MenuItem value={THEMES.LIGHT}>Light</MenuItem>
              <MenuItem value={THEMES.DARK}>Dark</MenuItem>
              <MenuItem value={THEMES.SYSTEM}>System Default</MenuItem>
            </Select>
          </FormControl>

          <Typography variant="h6" gutterBottom mt={4}>
            Account Information
          </Typography>
          <Divider sx={{ mb: 2 }} />

          <Box sx={{ mb: 2 }}>
            <Typography variant="body1" gutterBottom>
              <strong>Email:</strong> {user?.email || "Not logged in"}
            </Typography>

            <Typography variant="body1" gutterBottom>
              <strong>Account Type:</strong>{" "}
              {user?.subscription?.plan
                ? `${user.subscription.plan} Plan`
                : "Free Account"}
            </Typography>
          </Box>
        </Paper>
      )}

      {/* Subscription Tab */}
      {activeTab === 1 && (
        <Box>
          <SubscriptionDetails />
          <SubscriptionPlans />
        </Box>
      )}

      {/* LLM Settings Tab */}
      {activeTab === 2 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            LLM Settings
          </Typography>
          <Divider sx={{ mb: 2 }} />

          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel id="provider-label">Default Provider</InputLabel>
            <Select
              labelId="provider-label"
              value={selectedProvider || ""}
              label="Default Provider"
              onChange={(e) => dispatch(setSelectedProvider(e.target.value))}
            >
              {providers.map((provider) => (
                <MenuItem key={provider.id} value={provider.id}>
                  {provider.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel id="model-label">Default Model</InputLabel>
            <Select
              labelId="model-label"
              value={selectedModel || ""}
              label="Default Model"
              onChange={(e) => dispatch(setSelectedModel(e.target.value))}
              disabled={!selectedProvider || models.length === 0}
            >
              {models.map((model) => (
                <MenuItem key={model.id} value={model.id}>
                  {model.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Typography variant="subtitle2" gutterBottom>
            Temperature
          </Typography>
          <Slider
            value={temperature}
            min={0}
            max={1}
            step={0.01}
            onChange={(_, value) => setTemperature(value as number)}
            valueLabelDisplay="auto"
            sx={{ mb: 3 }}
          />

          <Typography variant="subtitle2" gutterBottom>
            Max Tokens
          </Typography>
          <TextField
            type="number"
            value={maxTokens}
            onChange={(e) => setMaxTokens(Number(e.target.value))}
            fullWidth
            sx={{ mb: 3 }}
          />

          <Typography variant="subtitle2" gutterBottom>
            Top P
          </Typography>
          <Slider
            value={topP}
            min={0}
            max={1}
            step={0.01}
            onChange={(_, value) => setTopP(value as number)}
            valueLabelDisplay="auto"
            sx={{ mb: 3 }}
          />

          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              Settings saved successfully!
            </Alert>
          )}

          <Button
            variant="contained"
            color="primary"
            onClick={handleSave}
            disabled={saving}
            fullWidth
          >
            {saving ? <CircularProgress size={24} /> : "Save Settings"}
          </Button>
        </Paper>
      )}
    </Box>
  );
};

export default Settings;

import React, { useEffect, useState } from "react";
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Divider,
  Button,
  LinearProgress,
  CircularProgress,
  Tabs,
  Tab,
} from "@mui/material";
import AnalyticsDashboard from "../components/metrics/AnalyticsDashboard";
import { useNavigate } from "react-router-dom";
import { useAppDispatch } from "../hooks/useAppDispatch";
import { useTypedSelector } from "../hooks/useTypedSelector";
import { fetchConversations } from "../store/slices/conversationSlice";
import { fetchUserMetrics } from "../store/slices/authSlice";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { user } = useTypedSelector((state) => state.auth);
  const { conversations, loading } = useTypedSelector(
    (state) => state.conversation
  );
  const { providers, models, selectedProvider, selectedModel } =
    useTypedSelector((state) => state.llm);

  // Tab state
  const [tabValue, setTabValue] = useState(0);

  // Check if user is admin
  const isAdmin = user?.role === "ADMIN";

  useEffect(() => {
    dispatch(fetchConversations());
    dispatch(fetchUserMetrics());
  }, [dispatch]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Welcome section */}
      <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5">Welcome, {user?.name || "User"}</Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
          Here's an overview of your UnifiedLLM Hub usage and latest
          conversations.
        </Typography>
      </Paper>

      {/* Admin tabs if user is admin */}
      {isAdmin && (
        <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            aria-label="dashboard tabs"
          >
            <Tab label="User Dashboard" />
            <Tab label="System Analytics" />
          </Tabs>
        </Box>
      )}

      {/* User Dashboard */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={4}>
          {/* Stats Section */}
          <Grid item xs={12} md={4}>
            <Card elevation={2}>
              <CardHeader title="Usage Statistics" />
              <CardContent>
                <Typography variant="body2">
                  Subscription: {user?.subscription?.plan || "Basic"}
                </Typography>

                {loading && !user?.metrics ? (
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "center",
                      mt: 2,
                      mb: 2,
                    }}
                  >
                    <CircularProgress size={24} />
                  </Box>
                ) : user?.metrics ? (
                  <>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Messages used: {user.metrics.usedMessages} /{" "}
                      {user.metrics.totalQuota}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        mt: 0.5,
                        fontSize: "0.8rem",
                        color: "text.secondary",
                      }}
                    >
                      {user.metrics.remainingMessages} messages remaining
                    </Typography>

                    <Box sx={{ mt: 1.5, mb: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={user.metrics.usagePercentage}
                        color={
                          user.metrics.usagePercentage > 85
                            ? "error"
                            : user.metrics.usagePercentage > 70
                            ? "warning"
                            : "primary"
                        }
                        sx={{ height: 8, borderRadius: 1 }}
                      />
                    </Box>

                    <Typography variant="body2" sx={{ mt: 2 }}>
                      Current billing period: {user.metrics.billingPeriodStart}{" "}
                      to {user.metrics.billingPeriodEnd}
                    </Typography>

                    {user.metrics.messagesPerProvider && (
                      <>
                        <Box sx={{ mt: 2, mb: 1 }}>
                          <Typography variant="body2">
                            Usage by provider:
                          </Typography>
                        </Box>
                        <List dense>
                          {Object.entries(user.metrics.messagesPerProvider).map(
                            ([provider, count]) => (
                              <ListItem key={provider} disablePadding>
                                <ListItemText
                                  primary={
                                    provider.charAt(0).toUpperCase() +
                                    provider.slice(1)
                                  }
                                  secondary={`${count} messages`}
                                />
                              </ListItem>
                            )
                          )}
                        </List>
                      </>
                    )}
                  </>
                ) : (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Messages used: {user?.subscription?.messageUsed || 0} /{" "}
                    {user?.subscription?.messageQuota || 1000}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Current Settings */}
          <Grid item xs={12} md={4}>
            <Card elevation={2}>
              <CardHeader title="Current Settings" />
              <CardContent>
                <Typography variant="body2">
                  Default Provider:{" "}
                  {providers.find((p) => p.id === selectedProvider)?.name ||
                    "None selected"}
                </Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Default Model:{" "}
                  {models.find((m) => m.id === selectedModel)?.name ||
                    "None selected"}
                </Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Theme: {user?.preferences?.theme || "System default"}
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => navigate("/settings")}
                  >
                    Change Settings
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Recent Conversations */}
          <Grid item xs={12} md={4}>
            <Card elevation={2}>
              <CardHeader
                title="Recent Conversations"
                action={
                  <Button
                    variant="contained"
                    size="small"
                    onClick={() => navigate("/chat")}
                  >
                    New Chat
                  </Button>
                }
              />
              <CardContent>
                {loading ? (
                  <Typography>Loading...</Typography>
                ) : conversations.length === 0 ? (
                  <Typography variant="body2">
                    No conversations yet. Start a new chat!
                  </Typography>
                ) : (
                  <List dense>
                    {conversations.slice(0, 5).map((conversation, index) => (
                      <React.Fragment key={conversation.id}>
                        {index > 0 && <Divider component="li" />}
                        <ListItem disablePadding>
                          <ListItemButton
                            onClick={() => navigate(`/chat/${conversation.id}`)}
                          >
                            <ListItemText
                              primary={
                                conversation.title || "Untitled Conversation"
                              }
                              secondary={formatDate(conversation.updatedAt)}
                            />
                          </ListItemButton>
                        </ListItem>
                      </React.Fragment>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Admin Analytics Dashboard - Only visible to admins */}
      {isAdmin && (
        <TabPanel value={tabValue} index={1}>
          <AnalyticsDashboard />
        </TabPanel>
      )}
    </Box>
  );
};

export default Dashboard;

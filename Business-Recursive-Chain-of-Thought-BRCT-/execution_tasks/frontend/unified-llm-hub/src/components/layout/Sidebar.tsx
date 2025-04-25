import React, { useEffect, useState } from "react";
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  Avatar,
  Toolbar,
  IconButton,
  Tooltip,
  CircularProgress,
} from "@mui/material";
import ChatIcon from "@mui/icons-material/Chat";
import DashboardIcon from "@mui/icons-material/Dashboard";
import SettingsIcon from "@mui/icons-material/Settings";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/DeleteOutline";
import { useLocation, useNavigate } from "react-router-dom";
import { useTypedSelector } from "../../hooks/useTypedSelector";
import { useAppDispatch } from "../../hooks/useAppDispatch";
import {
  fetchConversations,
  setActiveConversation,
  deleteConversationThunk,
  createLocalConversation,
  createNewConversation,
} from "../../store/slices/conversationSlice";
import { formatDistanceToNow } from "date-fns";

interface SidebarProps {
  drawerWidth: number;
}

const Sidebar: React.FC<SidebarProps> = ({ drawerWidth }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { activeConversation, conversations, loading } = useTypedSelector(
    (state) => state.conversation
  );
  const { user } = useTypedSelector((state) => state.auth);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);

  // Determine navigation items based on user role
  const mainNavItems = React.useMemo(() => {
    const items = [
      { text: "Chat", icon: <ChatIcon />, path: "/" },
      { text: "Dashboard", icon: <DashboardIcon />, path: "/dashboard" },
      { text: "Settings", icon: <SettingsIcon />, path: "/settings" },
    ];

    // Add Admin link only for admin users
    if (user?.role === "ADMIN") {
      items.push({
        text: "Admin",
        icon: <AdminPanelSettingsIcon />,
        path: "/admin",
      });
    }

    return items;
  }, [user?.role]);

  useEffect(() => {
    if (user) {
      dispatch(fetchConversations());
    }
  }, [dispatch, user]);

  const handleNewChat = () => {
    // Clear active conversation to start a fresh chat
    dispatch(setActiveConversation(null));
    navigate("/");
  };

  const handleConversationClick = (id: string) => {
    const conversation = conversations.find((conv) => conv.id === id);
    if (conversation) {
      dispatch(setActiveConversation(conversation));
      navigate(`/chat/${id}`);
    }
  };

  const handleDeleteConversation = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation(); // Prevent triggering the ListItemButton click

    if (window.confirm("Are you sure you want to delete this conversation?")) {
      setIsDeleting(id);
      try {
        await dispatch(deleteConversationThunk(id)).unwrap();

        // If we deleted the active conversation, clear it
        if (activeConversation && activeConversation.id === id) {
          dispatch(setActiveConversation(null));
          navigate("/");
        }
      } catch (error) {
        console.error("Failed to delete conversation:", error);
      } finally {
        setIsDeleting(null);
      }
    }
  };

  // Format timestamp to relative time (e.g., "2 hours ago")
  const formatTimestamp = (date: Date | string) => {
    if (!date) return "";

    const dateObj = typeof date === "string" ? new Date(date) : date;
    return formatDistanceToNow(dateObj, { addSuffix: true });
  };

  return (
    <Box
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: drawerWidth,
          boxSizing: "border-box",
        },
      }}
    >
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          UnifiedLLM Hub
        </Typography>
      </Toolbar>
      <Divider />

      {/* User info */}
      {user && (
        <Box sx={{ p: 2, display: "flex", alignItems: "center" }}>
          <Avatar sx={{ mr: 2 }}>
            {user.email ? user.email.charAt(0).toUpperCase() : "U"}
          </Avatar>
          <Box>
            <Typography variant="subtitle2" noWrap>
              {user.email}
            </Typography>
            <Typography variant="body2" color="text.secondary" noWrap>
              {user.subscription?.plan || "Free Plan"}
            </Typography>
          </Box>
        </Box>
      )}

      {/* Main navigation */}
      <List>
        {mainNavItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />

      {/* New chat button */}
      <Box sx={{ p: 2 }}>
        <ListItem disablePadding>
          <ListItemButton
            onClick={handleNewChat}
            sx={{
              borderRadius: 1,
              border: "1px dashed",
              borderColor: "divider",
            }}
          >
            <ListItemIcon>
              <AddIcon />
            </ListItemIcon>
            <ListItemText primary="New Chat" />
          </ListItemButton>
        </ListItem>
      </Box>

      {/* Conversations list */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          px: 2,
          py: 1,
        }}
      >
        <Typography variant="subtitle2">Recent Conversations</Typography>
        {loading && <CircularProgress size={16} />}
      </Box>
      <List dense>
        {conversations && conversations.length > 0 ? (
          conversations.map((conversation) => (
            <ListItem
              key={conversation.id}
              disablePadding
              secondaryAction={
                isDeleting === conversation.id ? (
                  <CircularProgress size={20} />
                ) : (
                  <Tooltip title="Delete conversation">
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      size="small"
                      onClick={(e) =>
                        handleDeleteConversation(e, conversation.id)
                      }
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )
              }
            >
              <ListItemButton
                selected={Boolean(
                  activeConversation &&
                    activeConversation.id === conversation.id
                )}
                onClick={() => handleConversationClick(conversation.id)}
              >
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <ChatIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary={conversation.title || "Untitled Chat"}
                  secondary={
                    conversation.updatedAt
                      ? formatTimestamp(conversation.updatedAt)
                      : ""
                  }
                  primaryTypographyProps={{
                    noWrap: true,
                    fontSize: 14,
                  }}
                  secondaryTypographyProps={{
                    noWrap: true,
                    fontSize: 11,
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))
        ) : !loading ? (
          <ListItem>
            <ListItemText
              primary="No conversations yet"
              primaryTypographyProps={{
                variant: "body2",
                color: "text.secondary",
                align: "center",
              }}
            />
          </ListItem>
        ) : null}
      </List>
    </Box>
  );
};

export default Sidebar;

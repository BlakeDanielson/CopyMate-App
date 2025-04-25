import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { STORAGE_KEYS, THEMES } from "../../config/constants";

interface UiState {
  sidebarOpen: boolean;
  theme: "light" | "dark" | "system";
  settingsOpen: boolean;
  activeTab: string;
  notifications: Notification[];
}

interface Notification {
  id: string;
  type: "success" | "error" | "info" | "warning";
  message: string;
  timestamp: Date;
  read: boolean;
}

// Initialize theme from localStorage or default to system
const getInitialTheme = (): "light" | "dark" | "system" => {
  const savedTheme = localStorage.getItem(STORAGE_KEYS.THEME);
  if (
    savedTheme &&
    (savedTheme === "light" || savedTheme === "dark" || savedTheme === "system")
  ) {
    return savedTheme as "light" | "dark" | "system";
  }
  return THEMES.SYSTEM as "light" | "dark" | "system";
};

const initialState: UiState = {
  sidebarOpen: true,
  theme: getInitialTheme(),
  settingsOpen: false,
  activeTab: "chat",
  notifications: [],
};

const uiSlice = createSlice({
  name: "ui",
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    setTheme: (state, action: PayloadAction<"light" | "dark" | "system">) => {
      state.theme = action.payload;
      localStorage.setItem(STORAGE_KEYS.THEME, action.payload);
    },
    toggleSettings: (state) => {
      state.settingsOpen = !state.settingsOpen;
    },
    setSettingsOpen: (state, action: PayloadAction<boolean>) => {
      state.settingsOpen = action.payload;
    },
    setActiveTab: (state, action: PayloadAction<string>) => {
      state.activeTab = action.payload;
    },
    addNotification: (
      state,
      action: PayloadAction<Omit<Notification, "id" | "timestamp" | "read">>
    ) => {
      const notification: Notification = {
        id: Date.now().toString(),
        ...action.payload,
        timestamp: new Date(),
        read: false,
      };
      state.notifications.unshift(notification);
    },
    markNotificationAsRead: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find(
        (n) => n.id === action.payload
      );
      if (notification) {
        notification.read = true;
      }
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
  },
});

export const {
  toggleSidebar,
  setSidebarOpen,
  setTheme,
  toggleSettings,
  setSettingsOpen,
  setActiveTab,
  addNotification,
  markNotificationAsRead,
  clearNotifications,
} = uiSlice.actions;

export default uiSlice.reducer;

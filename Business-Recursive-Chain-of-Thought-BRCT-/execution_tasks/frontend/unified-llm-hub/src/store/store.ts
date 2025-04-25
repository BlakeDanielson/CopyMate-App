import { configureStore } from "@reduxjs/toolkit";
import conversationReducer from "./slices/conversationSlice";
import authReducer from "./slices/authSlice";
import uiReducer from "./slices/uiSlice";
import llmReducer from "./slices/llmSlice";
import subscriptionReducer from "./slices/subscriptionSlice";
import analyticsReducer from "./slices/analyticsSlice";

export const store = configureStore({
  reducer: {
    conversation: conversationReducer,
    auth: authReducer,
    ui: uiReducer,
    llm: llmReducer,
    subscription: subscriptionReducer,
    analytics: analyticsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ["conversation/setStreamingMessage"],
        // Ignore these field paths in all actions
        ignoredActionPaths: ["payload.timestamp", "meta.timestamp"],
        // Ignore these paths in the state
        ignoredPaths: [
          "conversation.activeConversation.messages",
          "conversation.conversations",
        ],
      },
    }),
});

// Still export the inferred type for components that expect it
export type StoreState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

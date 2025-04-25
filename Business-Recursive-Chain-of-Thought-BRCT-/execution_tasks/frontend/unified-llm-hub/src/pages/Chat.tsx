import React, { useState, useEffect } from "react";
import { llmService } from "../services/api/llm.service";
import { conversationService } from "../services/api/conversation.service";
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  CircularProgress,
  List,
  ListItem,
  useTheme,
  Collapse,
  Divider,
  Grid,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import DeleteIcon from "@mui/icons-material/Delete";
import SettingsIcon from "@mui/icons-material/Settings";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import { useParams, useNavigate } from "react-router-dom";
import { useAppDispatch } from "../hooks/useAppDispatch";
import { useTypedSelector } from "../hooks/useTypedSelector";
import {
  fetchConversation,
  sendMessage,
  addMessage,
  updateStreamingMessage,
  createLocalConversation,
  startStreaming,
  stopStreaming,
  deleteConversationThunk,
} from "../store/slices/conversationSlice";
import { MESSAGE_ROLES } from "../config/constants";
import ChatMessage from "../components/chat/ChatMessage";
import ModelSelector from "../components/model-selection/ModelSelector";
import ParameterControls from "../components/settings/ParameterControls";

const Chat: React.FC = () => {
  const { conversationId } = useParams<{ conversationId: string }>();
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const theme = useTheme();

  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const { activeConversation, loading, streaming } = useTypedSelector(
    (state) => state.conversation
  );
  const { selectedProvider, selectedModel, parameters } = useTypedSelector(
    (state) => state.llm
  );

  // Load conversation if ID is provided
  useEffect(() => {
    if (conversationId) {
      dispatch(fetchConversation(conversationId));
    } else if (!activeConversation) {
      // Create a new local conversation if no active conversation
      dispatch(createLocalConversation("New Conversation"));
    }
  }, [conversationId, dispatch, activeConversation]);

  const handleSendMessage = async () => {
    if (!input.trim() || loading || streaming) return;

    // Add user message to conversation
    const userMessage = {
      id: Date.now().toString(),
      role: MESSAGE_ROLES.USER as "user",
      content: input,
      timestamp: new Date(),
    };

    dispatch(addMessage(userMessage));

    // Clear input and show typing indicator
    setInput("");
    setIsTyping(true);

    // Add initial assistant message (empty)
    const assistantMessage = {
      id: (Date.now() + 1).toString(),
      role: MESSAGE_ROLES.ASSISTANT as "assistant",
      content: "",
      timestamp: new Date(),
      provider: selectedProvider || undefined,
      model: selectedModel || undefined,
    };

    dispatch(addMessage(assistantMessage));
    dispatch(startStreaming());

    // Get combined parameters with provider and model
    const combinedParameters = {
      provider: selectedProvider || undefined,
      model: selectedModel || undefined,
      ...parameters,
    };

    try {
      // Check if browser supports EventSource for streaming
      if (window.EventSource) {
        // Use streaming API
        const source = llmService.streamMessage(
          input,
          activeConversation?.id || null,
          combinedParameters
        );

        let response = "";

        // Set up event handlers
        source.onmessage = (event: MessageEvent) => {
          try {
            const data = JSON.parse(event.data);
            if (data.content) {
              response += data.content;
              dispatch(updateStreamingMessage({ content: response }));
            }
          } catch (error) {
            console.error("Error parsing SSE data:", error);
          }
        };

        source.onerror = (error: Event) => {
          console.error("EventSource error:", error);
          source.close();
          dispatch(stopStreaming());
          setIsTyping(false);
        };

        source.addEventListener("complete", () => {
          source.close();
          dispatch(stopStreaming());
          setIsTyping(false);
        });
      } else {
        // Fallback for browsers without EventSource support
        await dispatch(
          sendMessage({
            message: input,
            conversationId: activeConversation?.id || null,
            parameters: combinedParameters,
          })
        );

        setIsTyping(false);
        dispatch(stopStreaming());
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setIsTyping(false);
      dispatch(stopStreaming());
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "calc(100vh - 64px)",
        p: 2,
      }}
    >
      <Paper
        elevation={2}
        sx={{
          display: "flex",
          flexDirection: "column",
          flexGrow: 1,
          overflow: "hidden",
          borderRadius: 2,
        }}
      >
        {/* Chat header */}
        <Box
          sx={{
            p: 2,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            borderBottom: 1,
            borderColor: "divider",
          }}
        >
          <Typography variant="h6">
            {activeConversation?.title || "New Conversation"}
          </Typography>
          <IconButton
            color="error"
            size="small"
            disabled={loading}
            onClick={() => {
              if (
                activeConversation?.id &&
                window.confirm(
                  "Are you sure you want to delete this conversation?"
                )
              ) {
                dispatch(deleteConversationThunk(activeConversation.id))
                  .unwrap()
                  .then(() => {
                    navigate("/");
                  })
                  .catch((error: unknown) => {
                    console.error("Failed to delete conversation:", error);
                  });
              } else {
                navigate("/");
              }
            }}
          >
            <DeleteIcon />
          </IconButton>
        </Box>

        {/* Settings panel */}
        <Box
          sx={{
            p: 1,
            borderBottom: 1,
            borderColor: "divider",
            display: "flex",
            justifyContent: "flex-end",
          }}
        >
          <IconButton
            size="small"
            onClick={() => setShowSettings(!showSettings)}
            color={showSettings ? "primary" : "default"}
            sx={{ mr: 1 }}
          >
            <SettingsIcon fontSize="small" />
            {showSettings ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>

        <Collapse in={showSettings}>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: "divider" }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Model Selection
                </Typography>
                <ModelSelector vertical={false} />
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Parameters
                </Typography>
                <ParameterControls vertical={false} compact />
              </Grid>
            </Grid>
          </Box>
        </Collapse>

        {/* Messages container */}
        <Box
          sx={{
            flexGrow: 1,
            overflow: "auto",
            p: 2,
            bgcolor:
              theme.palette.mode === "dark" ? "background.paper" : "grey.50",
          }}
        >
          {loading ? (
            <Box sx={{ display: "flex", justifyContent: "center", p: 3 }}>
              <CircularProgress />
            </Box>
          ) : activeConversation?.messages &&
            activeConversation.messages.length > 0 ? (
            <Box>
              {activeConversation.messages.map((message, index) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  isStreaming={
                    streaming &&
                    message.role === MESSAGE_ROLES.ASSISTANT &&
                    index === activeConversation.messages.length - 1
                  }
                  showMetrics={true}
                />
              ))}
            </Box>
          ) : (
            <Box
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                p: 3,
              }}
            >
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Start a new conversation
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center">
                Send a message to begin chatting with the AI
              </Typography>
            </Box>
          )}
        </Box>

        {/* Input area */}
        <Box
          sx={{
            p: 2,
            borderTop: 1,
            borderColor: "divider",
          }}
        >
          <Box
            component="form"
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            sx={{
              display: "flex",
              alignItems: "center",
            }}
          >
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Type your message here..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading || streaming}
              sx={{ mr: 1 }}
              multiline
              maxRows={4}
            />
            <Button
              variant="contained"
              color="primary"
              endIcon={<SendIcon />}
              disabled={!input.trim() || loading || streaming}
              onClick={handleSendMessage}
              type="submit"
            >
              Send
            </Button>
          </Box>

          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mt: 1,
            }}
          >
            <Typography variant="caption" color="text.secondary">
              {selectedProvider && selectedModel
                ? `Using ${selectedModel} (${selectedProvider})`
                : "Select a provider and model in settings"}
            </Typography>

            <Typography variant="caption" color="text.secondary">
              {streaming || isTyping ? "AI is typing..." : "Ready"}
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default Chat;

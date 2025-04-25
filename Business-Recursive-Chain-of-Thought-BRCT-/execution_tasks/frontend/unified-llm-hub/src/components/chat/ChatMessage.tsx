import React from "react";
import {
  Paper,
  Typography,
  Box,
  Avatar,
  Chip,
  useTheme,
  Tooltip,
} from "@mui/material";
import { Message } from "../../interfaces/llm";
import { MESSAGE_ROLES } from "../../config/constants";

interface ChatMessageProps {
  message: Message;
  isStreaming?: boolean;
  showMetrics?: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isStreaming = false,
  showMetrics = false,
}) => {
  const theme = useTheme();
  const isUser = message.role === MESSAGE_ROLES.USER;
  const isAssistant = message.role === MESSAGE_ROLES.ASSISTANT;
  const isSystem = message.role === MESSAGE_ROLES.SYSTEM;

  // Colors for different message types
  const messageColor = {
    backgroundColor: isUser
      ? theme.palette.primary.light
      : isSystem
      ? theme.palette.info.light
      : theme.palette.background.paper,
    color: isUser
      ? theme.palette.primary.contrastText
      : isSystem
      ? theme.palette.info.contrastText
      : theme.palette.text.primary,
  };

  // Calculate metrics display
  const timeToFirstToken = message.metrics?.timeToFirstToken || 0;
  const tokensPerSecond = message.metrics?.tokensPerSecond || 0;
  const totalTokens = message.metrics?.totalTokens || 0;

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: isUser ? "flex-end" : "flex-start",
        mb: 2,
        maxWidth: "100%",
      }}
    >
      <Box
        sx={{
          display: "flex",
          flexDirection: isUser ? "row-reverse" : "row",
          alignItems: "flex-start",
          maxWidth: "85%",
        }}
      >
        {/* Avatar */}
        <Avatar
          sx={{
            bgcolor: isUser
              ? "primary.main"
              : isSystem
              ? "info.main"
              : "secondary.main",
            width: 36,
            height: 36,
            mx: 1,
          }}
        >
          {isUser ? "U" : isSystem ? "S" : "AI"}
        </Avatar>

        {/* Message bubble */}
        <Paper
          elevation={1}
          sx={{
            p: 2,
            borderRadius: 2,
            ...messageColor,
            maxWidth: "calc(100% - 50px)",
            wordBreak: "break-word",
          }}
        >
          {message.content ? (
            <Typography variant="body1" component="div">
              {message.content.split("\n").map((line, i) => (
                <React.Fragment key={i}>
                  {line}
                  {i !== message.content.split("\n").length - 1 && <br />}
                </React.Fragment>
              ))}
            </Typography>
          ) : isAssistant && isStreaming ? (
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Typography variant="body2" color="text.secondary">
                AI is typing...
              </Typography>
              <Box
                sx={{
                  display: "flex",
                  ml: 1,
                  "& > span": {
                    width: 6,
                    height: 6,
                    margin: "0 2px",
                    borderRadius: "50%",
                    backgroundColor: "text.secondary",
                    display: "inline-block",
                    animation: "typing-dot 1.4s infinite ease-in-out both",
                  },
                  "& > span:nth-of-type(1)": {
                    animationDelay: "0s",
                  },
                  "& > span:nth-of-type(2)": {
                    animationDelay: "0.2s",
                  },
                  "& > span:nth-of-type(3)": {
                    animationDelay: "0.4s",
                  },
                }}
              >
                <span />
                <span />
                <span />
              </Box>
            </Box>
          ) : (
            <Typography variant="body2" color="text.secondary">
              (Empty message)
            </Typography>
          )}

          {/* Display model and provider if available */}
          {isAssistant && message.model && (
            <Box
              sx={{
                mt: 1,
                display: "flex",
                justifyContent: "flex-start",
                alignItems: "center",
              }}
            >
              <Tooltip
                title={`Model: ${message.model}${
                  message.provider ? ` | Provider: ${message.provider}` : ""
                }`}
              >
                <Chip
                  label={`${message.model}`}
                  size="small"
                  variant="outlined"
                />
              </Tooltip>
            </Box>
          )}
        </Paper>
      </Box>

      {/* Message metadata */}
      <Box
        sx={{
          display: "flex",
          flexDirection: isUser ? "row-reverse" : "row",
          alignItems: "center",
          maxWidth: "85%",
          ml: isUser ? 0 : 7,
          mr: isUser ? 7 : 0,
          mt: 0.5,
        }}
      >
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ fontStyle: "italic" }}
        >
          {new Date(message.timestamp).toLocaleTimeString()} •{" "}
          {isUser ? "You" : isSystem ? "System" : "AI"}
        </Typography>

        {/* Performance metrics if available and enabled */}
        {isAssistant && showMetrics && message.metrics && (
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              ml: 1,
            }}
          >
            <Tooltip title="Time to first token (ms)">
              <Chip
                label={`TTFT: ${timeToFirstToken}ms`}
                size="small"
                sx={{ fontSize: "0.65rem", height: 20, mr: 0.5 }}
              />
            </Tooltip>
            <Tooltip title="Tokens per second">
              <Chip
                label={`TPS: ${tokensPerSecond}/s`}
                size="small"
                sx={{ fontSize: "0.65rem", height: 20, mr: 0.5 }}
              />
            </Tooltip>
            <Tooltip title="Total tokens in response">
              <Chip
                label={`Tokens: ${totalTokens}`}
                size="small"
                sx={{ fontSize: "0.65rem", height: 20 }}
              />
            </Tooltip>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default ChatMessage;

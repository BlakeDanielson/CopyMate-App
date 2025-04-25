'use client'; // Required for hooks like useState, useEffect, and tRPC hooks

import React, { useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid'; // For generating unique message IDs
import { ChatInput } from './ChatInput';
import { MessageList } from './MessageList';
import { Message } from './MessageItem'; // Import the shared Message type
import { api as trpcApi } from '@/lib/trpc/client';

// Add interface for props
interface ChatInterfaceProps {
  api?: typeof trpcApi; // Make the API optional for testing
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ api = trpcApi }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentInput, setCurrentInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Helper function to add a message to the list
  const addMessage = useCallback((message: Message) => {
    setMessages((prevMessages) => [...prevMessages, message]);
  }, []);

  // tRPC mutation hook
  const sendMessageMutation = api.chat.sendMessage.useMutation({
    onMutate: (variables) => {
      // Set loading state and clear previous errors
      setIsLoading(true);
      setError(null);

      // Optimistic update: Add user message immediately
      // Note: We generate a temporary ID here. If the backend returned the final
      // message object including its ID, we might update it in onSuccess.
      const userMessage: Message = {
        id: uuidv4(), // Generate temporary ID
        sender: 'user',
        text: variables.message,
      };
      addMessage(userMessage);

      // Clear the input field optimistically
      setCurrentInput('');

      // Return context for potential rollback on error
      return { userMessageId: userMessage.id };
    },
    onSuccess: (data, variables, context) => {
      // Add the LLM's response
      const llmMessage: Message = {
        id: uuidv4(), // Generate ID for LLM response
        sender: 'llm',
        text: data.reply,
      };
      addMessage(llmMessage);
      // Input is already cleared in onMutate
    },
    onError: (error, variables, context) => {
      setError(`Error: ${error.message || "Failed to get response. Please try again."}`);
      // Optional: Rollback optimistic update if needed
      // For simplicity here, we'll leave the user message but show an error.
      // If rollback is desired:
      // if (context?.userMessageId) {
      //   setMessages(prev => prev.filter(msg => msg.id !== context.userMessageId));
      // }
      // Restore input? Maybe not, user might want to retry.
    },
    onSettled: () => {
      // Always reset loading state when the mutation finishes
      setIsLoading(false);
    },
  });

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentInput(event.target.value);
  };

  const handleSubmit = () => {
    const trimmedInput = currentInput.trim();
    if (trimmedInput.length > 0 && !sendMessageMutation.isPending) { // Use isPending from mutation
      sendMessageMutation.mutate({ message: trimmedInput });
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <MessageList messages={messages} />
      {error && (
        <div className="p-2 text-center text-red-600 bg-red-100 border-t border-red-200">
          {error}
        </div>
      )}
      <ChatInput
        value={currentInput}
        onChange={handleInputChange}
        onSubmit={handleSubmit}
        isLoading={isLoading} // Pass the loading state
      />
    </div>
  );
};

// Also export as default for backward compatibility
export default ChatInterface;
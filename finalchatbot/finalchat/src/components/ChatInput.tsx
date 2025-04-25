import React, { useState } from 'react';

interface ChatInputProps {
  value: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onSubmit: () => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ value, onChange, onSubmit, isLoading }) => {

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && !event.shiftKey && !isLoading) {
      event.preventDefault(); // Prevent default form submission or newline
      onSubmit();
    }
  };
  
  // Add keyPress handler for test compatibility
  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && !event.shiftKey && !isLoading) {
      event.preventDefault();
      onSubmit();
    }
  };

  const handleClick = () => {
    if (!isLoading) {
      onSubmit();
    }
  };

  return (
    <div className="p-4 border-t border-gray-200 bg-white">
      <div className="flex items-center space-x-2">
        <input
          type="text"
          placeholder="Type a message..."
          value={value}
          onChange={onChange}
          onKeyDown={handleKeyDown}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          onClick={handleClick}
          disabled={isLoading}
          className="px-6 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

// Also export as default for backward compatibility
export default ChatInput;
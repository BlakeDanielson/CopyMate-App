import React, { useRef, useEffect } from 'react';
import { MessageItem, Message } from './MessageItem';

interface MessageListProps {
  messages: Message[];
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]); // Scroll to bottom whenever messages change

  return (
    <div data-testid="message-list" className="flex-1 overflow-y-auto p-4 space-y-2 bg-gray-50">
      {messages.map((msg) => (
        <MessageItem key={msg.id} message={msg} />
      ))}
      {/* Dummy div to help scroll to the bottom */}
      <div ref={messagesEndRef} />
    </div>
  );
};

// Also export as default for backward compatibility
export default MessageList;
import React from 'react';

export interface Message {
  id: string;
  sender: 'user' | 'llm';
  text: string;
}

interface MessageItemProps {
  message: Message;
}

export const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const isUser = message.sender === 'user';
  const alignment = isUser ? 'justify-end' : 'justify-start';
  const bgColor = isUser ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800';
  const bubbleStyles = `max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl px-4 py-2 rounded-lg shadow`;
  const messageTypeClass = isUser ? 'user-message' : 'llm-message';

  return (
    <div className={`flex ${alignment} mb-2 ${messageTypeClass}`} data-testid="message-item" data-sender={message.sender}>
      <div className={`${bgColor} ${bubbleStyles}`}>
        <p className="text-sm break-words">{message.text}</p>
      </div>
    </div>
  );
};

// Also export as default for backward compatibility
export default MessageItem;
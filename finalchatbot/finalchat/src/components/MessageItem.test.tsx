import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MessageItem } from './MessageItem';

describe('MessageItem Component', () => {
  test('renders user message with correct content', () => {
    const message = {
      id: '1',
      sender: 'user' as const,
      text: 'Hello, this is a test message'
    };
    
    render(<MessageItem message={message} />);
    
    expect(screen.getByText(message.text)).toBeInTheDocument();
    // Check if it's styled as a user message (using a data attribute)
    const messageElement = screen.getByText(message.text).closest('[data-sender]');
    expect(messageElement).toHaveAttribute('data-sender', 'user');
  });
  
  test('renders LLM message with correct content', () => {
    const message = {
      id: '2',
      sender: 'llm' as const,
      text: 'I am an AI assistant, how can I help?'
    };
    
    render(<MessageItem message={message} />);
    
    expect(screen.getByText(message.text)).toBeInTheDocument();
    // Check if it's styled as an LLM message (using a data attribute)
    const messageElement = screen.getByText(message.text).closest('[data-sender]');
    expect(messageElement).toHaveAttribute('data-sender', 'llm');
  });
  
  test('applies different styling based on sender type', () => {
    const userMessage = {
      id: '3',
      sender: 'user' as const,
      text: 'User message'
    };
    
    const llmMessage = {
      id: '4',
      sender: 'llm' as const,
      text: 'LLM message'
    };
    
    const { rerender } = render(<MessageItem message={userMessage} />);
    
    const userMessageElement = screen.getByText(userMessage.text).closest('[data-testid="message-item"]');
    expect(userMessageElement).toHaveClass('user-message');
    
    rerender(<MessageItem message={llmMessage} />);
    
    const llmMessageElement = screen.getByText(llmMessage.text).closest('[data-testid="message-item"]');
    expect(llmMessageElement).toHaveClass('llm-message');
  });
  
  test('displays message text with proper formatting', () => {
    const messageWithMultipleLines = {
      id: '5',
      sender: 'llm' as const,
      text: 'This is a message\nwith multiple lines\nto test text formatting'
    };
    
    render(<MessageItem message={messageWithMultipleLines} />);
    
    // The text should be preserved with proper formatting
    expect(screen.getByText(/This is a message/)).toBeInTheDocument();
    expect(screen.getByText(/with multiple lines/)).toBeInTheDocument();
    expect(screen.getByText(/to test text formatting/)).toBeInTheDocument();
  });
});
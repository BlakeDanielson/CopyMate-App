import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MessageList } from './MessageList';
import { MessageItem } from './MessageItem';

// Mock scrollIntoView since it's not available in jsdom
beforeAll(() => {
  // Create a mock implementation of scrollIntoView
  const scrollIntoViewMock = jest.fn();
  Element.prototype.scrollIntoView = scrollIntoViewMock;
});

// Mock the MessageItem component to test if it receives the correct props
jest.mock('./MessageItem', () => ({
  MessageItem: jest.fn().mockImplementation(({ message }) => (
    <div data-testid="message-item-mock" data-message-id={message.id}>
      {message.text}
    </div>
  ))
}));

describe('MessageList Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders empty state when no messages are provided', () => {
    render(<MessageList messages={[]} />);
    
    // Check for an empty state container (with just the scroll ref div)
    const messageContainer = screen.getByTestId('message-list');
    expect(messageContainer).toBeInTheDocument();
    expect(messageContainer.children.length).toBe(1); // 1 child for scroll ref div
  });

  test('renders a list of messages using MessageItem components', () => {
    const messages = [
      { id: '1', sender: 'user' as const, text: 'Hello' },
      { id: '2', sender: 'llm' as const, text: 'Hi there' },
      { id: '3', sender: 'user' as const, text: 'How are you?' }
    ];
    
    render(<MessageList messages={messages} />);
    
    // Check if all messages are rendered
    const renderedMessages = screen.getAllByTestId('message-item-mock');
    expect(renderedMessages.length).toBe(3);
    
    // Check if MessageItem is called with correct props for each message
    expect(MessageItem).toHaveBeenCalledTimes(3);
    
    // Instead of strict checking call arguments, just verify the right messages were passed
    messages.forEach((message, index) => {
      // Get the message prop from the actual call
      const actualCall = MessageItem.mock.calls[index];
      const messageArg = actualCall[0].message;
      
      // Verify the message matches what we expect
      expect(messageArg).toEqual(message);
    });
  });

  test('renders messages in the correct order', () => {
    const messages = [
      { id: '1', sender: 'user' as const, text: 'First message' },
      { id: '2', sender: 'llm' as const, text: 'Second message' },
      { id: '3', sender: 'user' as const, text: 'Third message' }
    ];
    
    render(<MessageList messages={messages} />);
    
    const renderedMessages = screen.getAllByTestId('message-item-mock');
    
    // Check that messages are displayed in the same order they were provided
    expect(renderedMessages[0]).toHaveTextContent('First message');
    expect(renderedMessages[1]).toHaveTextContent('Second message');
    expect(renderedMessages[2]).toHaveTextContent('Third message');
  });

  test('has appropriate scroll container for messages', () => {
    const messages = [
      { id: '1', sender: 'user' as const, text: 'Test message' }
    ];
    
    render(<MessageList messages={messages} />);
    
    // The message list should be in a scrollable container
    const messageContainer = screen.getByTestId('message-list');
    expect(messageContainer).toHaveClass('overflow-y-auto'); // Assuming Tailwind CSS
  });
  
  test('scrolls to bottom when new messages are added', () => {
    // We already mocked scrollIntoView in beforeAll
    const scrollIntoViewMock = Element.prototype.scrollIntoView as jest.Mock;
    
    const messages = [
      { id: '1', sender: 'user' as const, text: 'Test message' }
    ];
    
    render(<MessageList messages={messages} />);
    
    // We expect the component to try to scroll to the bottom when mounted with messages
    expect(scrollIntoViewMock).toHaveBeenCalled();
  });
});